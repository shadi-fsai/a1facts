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
                Only use information from the knowledge graph to answer the question. If you don't know the answer, say so.
                Every time you return a response add a section at the end called "Wish I could find" and state what knowledge you didn't find and wish you could find
                """),
                show_tool_calls=True,
                markdown=True,
                debug_mode=False,
            )

    def query(self, query: str):
        result = self.agent.run("Answer the following question, use as many tools as you need to get the information: {" + query + "}")
        return result.content