from ontology.knowledge_ontology import KnowledgeOntology
from utils.modelconfig import my_query_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from colored import cprint

class QueryAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology        
        self.agent = Agent(
            name="Knowledge Graph Agent",
            role="Interact with the knowledge graph",
            model=my_query_model,
            tools=mytools,
            instructions=dedent(f"""
                Get information from the knowledge base.
                Use the tools to get information from the graph.
                Today is {datetime.now().strftime("%Y-%m-%d")}
                """),
                show_tool_calls=True,
                markdown=True,
                debug_mode=True,
            )

    def query(self, query: str):

        result = self.agent.run(query)
        cprint(result, 'green')
        return result.content