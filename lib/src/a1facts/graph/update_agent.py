from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.utils.modelconfig import my_high_precision_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from a1facts.utils.logger import logger

class UpdateAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology
        self.update_agent = Agent(
            name="Knowledge Graph Update Agent",
            role="Update the knowledge graph",
            model=my_high_precision_model,
            tools=mytools,

            instructions=dedent(f"""
                The user is providing you unstrucutred knowledge. Translate the knowledge into a structured format based on the ontology.
                Ontology:[{self.ontology}]
                Return the results in RDFS format.
                Ideally, every RDFS entity should have sources.
                When you are done, add every entity and relationship to the graph using the tools available to you.
                First add the entities, then add the relationships.
                Make sure to add every single one of them.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            markdown=True,
            debug_mode=False,
            )

    def update(self, knowledge: str):
        logger.system(f"Updating knowledge graph with knowledge: {knowledge}")
        return self.update_agent.run("Translate the following knowledge into a structured format based on the ontology, then add every entity and every relationship to the graph using the tools available to you.\n \n " + knowledge)
