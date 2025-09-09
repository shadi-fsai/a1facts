from ontology.knowledge_ontology import KnowledgeOntology
from utils.modelconfig import my_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime

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
                When you are done, add every entity and relationship to the graph using the tools available to you.
                First add the entities, then add the relationships.
                Make sure to add every single one of them.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            show_tool_calls=True,
            markdown=True,
            debug_mode=False,
            )

    def update(self, knowledge: str):
        return self.update_agent.run("Translate the following knowledge into a structured format based on the ontology, then add every entity and every relationship to the graph using the tools available to you.\n \n " + knowledge)
