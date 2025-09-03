from graph.graph_database import Neo4jGraphDatabase, BaseGraphDatabase, NetworkxGraphDatabase
from ontology.knowledge_ontology import KnowledgeOntology
from graph.query_agent import QueryAgent
from graph.update_agent import UpdateAgent
from graph.query_rewrite_agent import QueryRewriteAgent
from datetime import date


class KnowledgeGraph:
    """
    Manages interactions with a Neo4j graph database, including adding, updating,
    and querying entities and relationships based on a provided ontology.
    """

    def __init__(self, ontology: KnowledgeOntology):
        """
        Initializes the KnowledgeGraph, connects to the Neo4j database, and sets up
        the query and update agents with tools derived from the ontology.

        Args:
            ontology (KnowledgeOntology): The ontology defining the graph's structure.
        """
        self.ontology = ontology
        self.graph_database = Neo4jGraphDatabase()
        self.get_tools = self.ontology.get_get_tools(self.graph_database.get_all_entities_by_label, 
            self.graph_database.get_entity_properties, self.graph_database.get_relationship_properties, self.graph_database.get_relationship_entities)
        self.add_or_update_tools = self.ontology.get_add_or_update_tools(self.graph_database.add_or_update_entity, self.graph_database.add_relationship)        
        self.query_agent = QueryAgent(self.ontology,self.get_tools ) 
        self.update_agent = UpdateAgent(self.ontology,self.add_or_update_tools)
        self.rewrite_agent = QueryRewriteAgent(self.ontology,[])
        self.class_entity_pairs = {}

    def get_class_entity_pairs(self):
        for entity_class in self.ontology.entity_classes:
            self.class_entity_pairs[entity_class.entity_class_name] = []
            entities = self.get_all_entities_by_label(entity_class.entity_class_name)
            for entity in entities:
                self.class_entity_pairs[entity_class.entity_class_name].append(entity[entity_class.primary_key_prop.property_name])
            

    def rewrite_query(self, query: str):
        self.get_class_entity_pairs()
        return self.rewrite_agent.rewrite_query(query, self.class_entity_pairs)


    def query(self, query: str):
        """
        Executes a natural language query against the knowledge graph.

        Args:
            query (str): The natural language query to execute.

        Returns:
            str: The content of the agent's response.
        """
        rewritten_query = self.rewrite_query(query)
        return self.query_agent.query(rewritten_query)

    def update_knowledge(self, knowledge: str):
        """
        Updates the knowledge graph with new, unstructured information.

        Args:
            knowledge (str): A string of unstructured knowledge to add to the graph.

        Returns:
            str: The content of the agent's response.
        """
        rewrite_knowledge = self.rewrite_query(knowledge)
        result = self.update_agent.update(rewrite_knowledge)
        return result.content

    def close(self):
        if self.graph_database is not None:
            self.graph_database.close()

