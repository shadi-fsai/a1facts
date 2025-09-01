from ontology.knowledge_ontology import KnowledgeOntology
from neo4j import GraphDatabase
from datetime import date
from dotenv import load_dotenv
import os
from ontology.knowledge_ontology import KnowledgeOntology
from utils.modelconfig import my_model
from utils.modelconfig import my_query_model, my_fast_model
from agno.tools import tool
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from groq import Groq
client = Groq()
# Load environment variables from .env file
load_dotenv()


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
        return result.content