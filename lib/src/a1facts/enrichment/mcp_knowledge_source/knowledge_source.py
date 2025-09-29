import asyncio
import inspect
import sys
from contextlib import AsyncExitStack
from a1facts.enrichment.knowledge_source import KnowledgeSource
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from agno.agent import Agent
from textwrap import dedent
from a1facts.utils.modelconfig import my_high_precision_model
from datetime import date
from threading import Thread
import atexit

class MCPKnowledgeSource(KnowledgeSource):
    def __init__(self, source_config: dict):
        self.name = source_config['name']
        self.description = source_config['description']
        self.override_reliability = source_config.get('override_reliability')
        self.override_credibility = source_config.get('override_credibility')
        self.session = None
        self.local_tools = []
        self.query_agent = None
        self.exit_stack = None

        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

        server_params = StdioServerParameters(
            command=source_config['run_command'],
            args=source_config['run_args'],
            cwd=source_config['run_cwd'],
            env=None,
        )
        
        print(f"[DEBUG] Server params for {self.name}: command={server_params.command}, args={server_params.args}, cwd={server_params.cwd}")

        if 'all_tools' in source_config and source_config['all_tools']:
            self.all_tools = True
        else:
            self.all_tools = False
        if self.all_tools:
            self.desired_tools = None
        else:
            self.desired_tools = source_config['tools']
        
        future = asyncio.run_coroutine_threadsafe(self._init_mcp(server_params), self.loop)
        future.result()

    def __del__(self):
        self.close()

    def close(self):
        # Close exit stack first while event loop is still running
        if self.exit_stack and self.loop and not self.loop.is_closed():
            try:
                # Schedule the cleanup on the event loop
                async def cleanup():
                    await self.exit_stack.aclose()
                    self.exit_stack = None

                future = asyncio.run_coroutine_threadsafe(cleanup(), self.loop)
                future.result(timeout=5)
            except Exception as e:
                # AsyncExitStack cleanup can fail in threading context, but that's OK
                # The important thing is that the MCP session worked during operation
                print(f"Warning: MCP cleanup error (expected in threading): {e}")
                self.exit_stack = None

    def close(self):
        # Close exit stack first while event loop is still running
        if self.exit_stack and self.loop and not self.loop.is_closed():
            try:
                # Schedule the cleanup on the event loop
                async def cleanup():
                    await self.exit_stack.aclose()
                    self.exit_stack = None

                future = asyncio.run_coroutine_threadsafe(cleanup(), self.loop)
                future.result(timeout=5)
            except Exception as e:
                # AsyncExitStack cleanup can fail in threading context, but that's OK
                # The important thing is that the MCP session worked during operation
                print(f"Warning: MCP cleanup error (expected in threading): {e}")
                self.exit_stack = None

        # Stop event loop and join thread
        if self.loop and self.loop.is_running():
            # Ask the loop to stop
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception:
                pass

        if self.thread and self.thread.is_alive():
            # Give the thread a little more time to finish cleanly
            self.thread.join(timeout=5)

        # After the loop has stopped and the thread joined, close the loop from the main thread
        try:
            if self.loop and not self.loop.is_closed():
                self.loop.close()
        except Exception:
            pass
            self.thread.join(timeout=2)

        # Clear references to help garbage collection
        self.session = None
        self.local_tools = []
        self.query_agent = None

    async def _init_mcp(self, server_params):
        """Initializes the MCP session and creates local tools."""
        print(f"[DEBUG] Starting MCP initialization for {self.name}")
        try:
            self.session = await self._initialize_session(server_params)
            print(f"[DEBUG] Session initialized for {self.name}")
            
            self.local_tools = await self._create_local_tools()
            print(f"[DEBUG] Local tools created for {self.name}: {len(self.local_tools)} tools")
            
            self.query_agent = self._create_query_agent()
            print(f"[DEBUG] Query agent created for {self.name}")
            
            if sys.platform == "win32":
                await asyncio.sleep(0.2)
                
            print(f"[DEBUG] MCP initialization completed for {self.name}")
        except Exception as e:
            print(f"[ERROR] MCP initialization failed for {self.name}: {e}")
            raise

    async def _initialize_session(self, server_params):
        """Initialize MCP session using proper AsyncExitStack context management"""
        print(f"[DEBUG] Initializing MCP session for {self.name}")
        self.exit_stack = AsyncExitStack()
        
        try:
            print(f"[DEBUG] Starting stdio client for {self.name}")
            # Use proper async context management for stdio client
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            print(f"[DEBUG] Stdio client started for {self.name}")
            
            print(f"[DEBUG] Creating client session for {self.name}")
            # Use proper async context management for ClientSession
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write, sampling_callback=None)
            )
            print(f"[DEBUG] Client session created for {self.name}")
            
            # Now session.initialize() will work properly
            print(f"[DEBUG] Initializing session for {self.name}")
            await session.initialize()
            print(f"[DEBUG] Session initialized successfully for {self.name}")
            
            return session
        except Exception as e:
            print(f"[ERROR] Failed to initialize MCP session for {self.name}: {e}")
            raise

    async def _create_local_tools(self):
        remote_tools_response = await self.session.list_tools()
        if self.desired_tools: #TODO if all_tools and desired set, throw error
            tasks = [self._create_local_tool(tool) for tool in remote_tools_response.tools if tool.name in self.desired_tools]
        else: #create all tools
            tasks = [self._create_local_tool(tool) for tool in remote_tools_response.tools]
        local_tools = await asyncio.gather(*tasks)
        return local_tools
    
    def _create_query_agent(self):
        return Agent(
            name=f"{self.name} Query Agent",
            role=f"Query the {self.name} knowledge source.",
            model=my_high_precision_model,
            tools=self.local_tools,
            instructions=dedent(f"""
                Query the knowledge source for the information requested by the user.
                Today's date is {date.today().strftime('%Y-%m-%d')}.
            """),
            markdown=True,
            debug_mode=False,
        )

    async def _create_local_tool(self, tool_details: types.Tool):
        """Dynamically creates a local, async function that calls a remote MCP tool."""
        
        async def tool_wrapper(*args, **kwargs):
            param_names = list(tool_details.inputSchema.get('properties', {}).keys())
            final_kwargs = {}

            if 'args' in kwargs or 'kwargs' in kwargs:
                agent_kwargs = kwargs.get('kwargs', {})
                if isinstance(agent_kwargs, dict): final_kwargs.update(agent_kwargs)
                agent_args = kwargs.get('args', [])
                if isinstance(agent_args, dict): final_kwargs.update(agent_args)
                elif isinstance(agent_args, list):
                    for i, arg_value in enumerate(agent_args):
                        if i < len(param_names): final_kwargs[param_names[i]] = arg_value
            else:
                for i, arg_value in enumerate(args):
                    if i < len(param_names): final_kwargs[param_names[i]] = arg_value
                final_kwargs.update(kwargs)
            
            filtered_kwargs = {k: v for k, v in final_kwargs.items() if k in param_names}

            print(f"Calling remote tool: {tool_details.name} with args: {filtered_kwargs}")
            try:
                result = await self.session.call_tool(tool_details.name, arguments=filtered_kwargs)
                if result.isError or not result.content:
                    error_message = result.content[0].text if result.content and isinstance(result.content[0], types.TextContent) else "Unknown error"
                    return f"Error executing tool {tool_details.name}: {error_message}"
                return result.content[0].text
            except Exception as e:
                return f"An exception occurred while calling tool {tool_details.name}: {e}"

        tool_wrapper.__name__ = tool_details.name
        doc = f"{tool_details.description or 'No description available.'}\n\nArgs:\n"
        if 'properties' in tool_details.inputSchema:
            for arg_name, arg_details in tool_details.inputSchema['properties'].items():
                is_required_str = "required" if arg_name in tool_details.inputSchema.get('required', []) else "optional"
                doc += f"    {arg_name} ({arg_details.get('type', 'unknown')}, {is_required_str}): {arg_details.get('description', '')}\n"
        tool_wrapper.__doc__ = doc
        return tool_wrapper

    def query_tool(self):
        async def query_handler(query_text: str) -> str:
            result = await self.query_agent.arun(query_text)
            return result.content
        
        query_handler.__name__ = f"query_{self.name}"
        query_handler.__doc__ = f"Query the {self.name} knowledge source. {self.description}"
        return query_handler

    def __str__(self) -> str:
        return f"{self.name} - {self.description}"

