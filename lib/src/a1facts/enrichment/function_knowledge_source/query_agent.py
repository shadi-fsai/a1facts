from agno.agent import Agent
from textwrap import dedent
from a1facts.utils.modelconfig import my_model

class QueryAgent:
    def __init__(self, tools: list):
        self.agent = Agent(
            name="Query Agent",
            role="Query the knowledge sources",
            model=my_model,
            tools=tools,
            instructions=dedent("""
                Query the knowledge sources for the information requested by the user.
            """),
            markdown=True,
            debug_mode=False,
        )

    def query(self, query: str):
        return self.agent.run(query).content