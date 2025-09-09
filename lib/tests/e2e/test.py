import asyncio
import inspect
import sys
from datetime import date, timedelta
from threading import Thread
import contextlib
import io
import subprocess

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from agno.agent import Agent
from textwrap import dedent
from utils.modelconfig import my_model

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv",  # Executable
    args=[
        "run",
        "--directory",
        "C:\\Users\\heluo\\Documents\\fortusight\\fortusight\\src\\server\\",
        "fmp_mcp_server.py"
    ],  # DIAGNOSTIC: Test if uv can be executed in the CWD
#    cwd=, # The original path
    env=None,  # Optional environment variables
)

async def create_local_tool(session: ClientSession, tool_details: types.Tool):
    """Dynamically creates a local, async function that calls a remote MCP tool."""

    async def tool_wrapper(*args, **kwargs):
        # The tool's schema is a dict, so we access its keys directly.
        param_names = list(tool_details.inputSchema.get('properties', {}).keys())
        final_kwargs = {}

        # First, handle arguments from an agent-style call, which are nested.
        if 'args' in kwargs or 'kwargs' in kwargs:
            agent_kwargs = kwargs.get('kwargs', {})
            if isinstance(agent_kwargs, dict):
                final_kwargs.update(agent_kwargs)

            agent_args = kwargs.get('args', [])
            if isinstance(agent_args, dict):
                final_kwargs.update(agent_args)
            elif isinstance(agent_args, list):
                for i, arg_value in enumerate(agent_args):
                    if i < len(param_names):
                        final_kwargs[param_names[i]] = arg_value
        # Otherwise, assume it's a direct call with standard python *args and **kwargs.
        else:
            for i, arg_value in enumerate(args):
                if i < len(param_names):
                    final_kwargs[param_names[i]] = arg_value
            final_kwargs.update(kwargs)
        
        # Filter for arguments that are actually in the tool's schema
        filtered_kwargs = {k: v for k, v in final_kwargs.items() if k in param_names}

        print(f"Calling remote tool: {tool_details.name} with args: {filtered_kwargs}")
        try:
            result = await session.call_tool(tool_details.name, arguments=filtered_kwargs)
            if result.isError or not result.content:
                error_message = result.content[0].text if result.content and isinstance(result.content[0], types.TextContent) else "Unknown error"
                return f"Error executing tool {tool_details.name}: {error_message}"
            return result.content[0].text
        except Exception as e:
            return f"An exception occurred while calling tool {tool_details.name}: {e}"

    tool_wrapper.__name__ = tool_details.name
    
    # Create and attach a descriptive docstring for the agent
    doc = f"{tool_details.description or 'No description available.'}\n\nArgs:\n"
    if hasattr(tool_details.inputSchema, 'properties'):
        for arg_name, arg_details in tool_details.inputSchema.properties.items():
            is_required_str = "required" if arg_name in tool_details.inputSchema.get('required', []) else "optional"
            doc += f"    {arg_name} ({arg_details.get('type', 'unknown')}, {is_required_str}): {arg_details.get('description', '')}\n"
    tool_wrapper.__doc__ = doc
    
    return tool_wrapper

class QueryAgent:
    def __init__(self, tools: list):
        self.agent = Agent(
            name="Query Agent",
            role="Query the knowledge sources",
            model=my_model,
            tools=tools,
            instructions=dedent(f"""
                Query the knowledge sources for the information requested by the user.
                Today's date is {date.today().strftime('%Y-%m-%d')}.
            """),
            markdown=True,
            debug_mode=True,
        )

    async def query(self, query: str):
        result = await self.agent.arun(query)
        print(f"\n--- Query Result ---")
        print(result.content)
        return result.content


class MCPTester:
    def __init__(self, server_params):
        self.server_params = server_params
        self.session = None
        self.query_agent = None
        self.stdio_cm = None

        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

        future = asyncio.run_coroutine_threadsafe(self._initialize(), self.loop)
        try:
            print("Waiting for initialization to complete...")
            future.result(timeout=10)
            print("Initialization completed.")
        except Exception as e:
            print(f"Initialization failed: {e}")
            self.close()
            raise

    async def _initialize(self):
        print("Initializing connection...")
        self.stderr_log = open("stderr.log", "w")
        self.stdout_log = open("stdout.log", "w")
        
        # We need to modify the StdioServerParameters to redirect stdout
        server_params_dict = self.server_params.model_dump()
        
        # The mcp library doesn't directly support stdout redirection in its params,
        # so we'll have to adjust the underlying process creation.
        # This requires a bit of a workaround. Let's see if we can get the log
        # by inspecting the process object after it's created.
        
        self.stdio_cm = stdio_client(self.server_params, errlog=self.stderr_log)
        print("stdio_client created. Awaiting __aenter__...")
        read, write = await self.stdio_cm.__aenter__()
        print("...__aenter__ completed.")
        self.session = ClientSession(read, write, sampling_callback=None)
        print("ClientSession created. Initializing session...")
        await self.session.initialize()
        print("...session initialized.")

        print("Fetching available remote tools...")
        remote_tools_response = await self.session.list_tools()
        print(f"Found {len(remote_tools_response.tools)} remote tools. Creating local wrappers for all of them.")

        tasks = [create_local_tool(self.session, tool) for tool in remote_tools_response.tools]
        local_tools = await asyncio.gather(*tasks)
        
        if local_tools:
            self.query_agent = QueryAgent(tools=local_tools)
        else:
            print("Could not create any local tools.")

    def query(self, query_str):
        if not self.query_agent:
            print("Query agent not initialized.")
            return None
        
        future = asyncio.run_coroutine_threadsafe(self.query_agent.query(query_str), self.loop)
        try:
            result = future.result(timeout=30)  # Added timeout
        except Exception as e:
            print(f"Query execution failed: {e}")
            result = None
        return result

    def close(self):
        print("Closing MCPTester...")
        if self.session and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.session.close(), self.loop)
            try:
                future.result(timeout=2)
                print("Session closed.")
            except Exception as e:
                print(f"Error closing session: {e}")
        self.session = None

        if self.stdio_cm and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.stdio_cm.__aexit__(None, None, None), self.loop)
            try:
                future.result(timeout=2)
                print("stdio_cm exited.")
            except Exception as e:
                print(f"Error exiting stdio_cm: {e}")
        self.stdio_cm = None
        
        if hasattr(self, 'stderr_log') and self.stderr_log:
            self.stderr_log.close()
        if hasattr(self, 'stdout_log') and self.stdout_log:
            self.stdout_log.close()

        if self.loop.is_running():
            print("Stopping event loop.")
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        print("Joining thread...")
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            print("Warning: Event loop thread did not terminate.")
        else:
            print("Thread joined.")


if __name__ == "__main__":
    tester = None
    try:
        tester = MCPTester(server_params)
        if tester.query_agent:
            query = "What is the latest daily price of AAPL? Also get me the company profile."
            print(f"\n--- Running query: '{query}' ---")
            result = tester.query(query)
            print("\n--- Query Result ---")
            print(result)
    finally:
        if tester:
            tester.close()