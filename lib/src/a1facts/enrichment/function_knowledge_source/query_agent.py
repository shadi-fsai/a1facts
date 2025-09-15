from agno.agent import Agent
from textwrap import dedent
from a1facts.utils.modelconfig import my_fast_language_model
from datetime import datetime

class QueryAgent:
    def __init__(self, tools: list):
        self.agent = Agent(
            name="Query Agent",
            role="Query the knowledge sources",
            model=my_fast_language_model,
            tools=tools,
            instructions=dedent(f"""
                Query the knowledge sources for the information requested by the user.
                Provide precise sources to the information you get from the knowledge source.
                If your source is from the web, provide the URL of the source.
                If your source is from a file, provide the file name and the page number.
                If your source is from a database, provide the database name and the table name.
                If your source is from a knowledge graph, provide the entity name and the property name.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            markdown=True,
            debug_mode=False,
        )

    def query(self, query: str):
        return self.agent.run(query).content