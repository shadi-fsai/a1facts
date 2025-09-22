from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.utils.modelconfig import my_high_precision_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from a1facts.utils.logger import logger
from colored import cprint
from pydantic import BaseModel, Field


class RDFSResult(BaseModel):
    rdfs: str = Field(description="The RDFS format of the knowledge. Only include entities, relationships and their properties that are in the ontology.")
    other_information: str = Field(description="Other information that couldn't be described in the ontology. Ideally this is empty, but if you have other info that is not in the ontology, included it here verbatim.")
    ontology_elements_used: list[str] = Field(description="The elements of the ontology that were used to create the RDFS format. each line should represent either an entity or a relationship and should include the properties verbatim that were used from the ontology.")


class UpdateAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology
        self.rdfs_agent = Agent(
            name="RDFS Agent",
            role="Translate the knowledge into a structured format based on the ontology.",
            model=my_high_precision_model,
            instructions=dedent(f"""
                Translate the knowledge into a structured format based on the ontology.
                Ontology:[{self.ontology}]
                Return the results in RDFS format. Include both entities and relationships -- along with their properties.
                ALWAYS use the properties verbatim that were used from the ontology.
                ALWAYS use the entities and relationships verbatim that were used from the ontology.
                NEVER make up information. 
                Only use the information provided to you. DO NOT use your own knowledge to make up information.
                Ideally, every RDFS entity should have sources.
                If you have an entity that can't be expressed in the ontology, include it in the other_information field.
                Use ":" as prefix for the entities and relationships. use "a" to describe an entity that is a type of another entity.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            markdown=True,
            debug_mode=False,
            output_schema=RDFSResult,
        )
        self.update_agent = Agent(
            name="Knowledge Graph Update Agent",
            role="Update the knowledge graph",
            model=my_high_precision_model,
            tools=mytools,

            instructions=dedent(f"""
                The user is providing you RDFS format of the knowledge. 
                Add every entity and relationship to the graph using the tools available to you.
                First add the entities, then add the relationships.
                Make sure to add every single one of them.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            markdown=True,
            debug_mode=False,
            input_schema=RDFSResult,
            )

    def update(self, knowledge: str):
        #step 0 - translate the knowledge into rdfs format
        #step 1 - deduplicate the knowledge using spacy; add alises to entities and relatioinships
        #step 2 - add the knowledge to the graph using the tools available to you
        logger.system(f"Updating knowledge graph with knowledge: {knowledge}")
        rdfs_result = self.rdfs_agent.run("Translate the following knowledge into a structured format based on the ontology\n\n " + knowledge)
        cprint(rdfs_result.content.rdfs, 'red')
        cprint(rdfs_result.content.other_information, 'yellow')
        
        entities, relationships = self.ontology.parse_rdfs_with_validation(rdfs_result.content.rdfs)
        for entity in entities:
            cprint(entity, 'green')
        exit()
        for relationship in relationships:
            cprint(relationship, 'blue')
        exit()    
        logger.system(f"RDFS result: {rdfs_result.content.rdfs + "\nToday is " + datetime.now().strftime("%Y-%m-%d")}")
        logger.system(f"RDFS not in ontology: {rdfs_result.content.other_information}")
        return self.update_agent.run(rdfs_result.content.rdfs + "\nToday is " + datetime.now().strftime("%Y-%m-%d"))