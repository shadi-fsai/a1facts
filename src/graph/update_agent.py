from neo4j import GraphDatabase
from datetime import date
from dotenv import load_dotenv
import os
from ontology.knowledge_ontology import KnowledgeOntology
from utils.modelconfig import my_model
from utils.modelconfig import my_query_model
from agno.tools import tool
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
# Load environment variables from .env file
load_dotenv()

class UpdateAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology
        self.update_agent = Agent(
            name="Knowledge Graph Update Agent",
            role="Update the knowledge graph",
            model=my_model,
            tools=mytools,
            instructions=dedent(f"""
                The user is providing you unstrucutred knowledge. Translate the knowledge into a structured format based on the ontology.
                Ontology:[{self.ontology}]
                Return the results in RDFS format.
                When you are done, add every entity and relationship to the graph using the tools available to you 
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            show_tool_calls=True,
            markdown=True,
            debug_mode=True,
            )

    def update(self, knowledge: str):
        return self.update_agent.run(knowledge)
