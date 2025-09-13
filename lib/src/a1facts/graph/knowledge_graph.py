from a1facts.graph.graph_database import BaseGraphDatabase
from a1facts.graph.neo4j_graph_database import Neo4jGraphDatabase
from a1facts.graph.networkx_graph_database import NetworkxGraphDatabase
from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.graph.query_agent import QueryAgent
from a1facts.graph.update_agent import UpdateAgent
from a1facts.graph.query_rewrite_agent import QueryRewriteAgent
from colored import cprint
from a1facts.utils.logger import logger

class KnowledgeGraph:
    """
    Manages interactions with a Neo4j graph database, including adding, updating,
    and querying entities and relationships based on a provided ontology.
    """

    def __init__(self, ontology: KnowledgeOntology, use_neo4j: bool = False):
        """
        Initializes the KnowledgeGraph, connects to the Neo4j database, and sets up
        the query and update agents with tools derived from the ontology.

        Args:
            ontology (KnowledgeOntology): The ontology defining the graph's structure.
        """
        logger.system(f"Initializing KnowledgeGraph: {ontology.ontology_file} with use_neo4j: {use_neo4j}")
        self.ontology = ontology
        self.graph_database = NetworkxGraphDatabase() if not use_neo4j else Neo4jGraphDatabase()
        logger.system(f"Graph database initialized")
        self.get_tools = self.ontology.get_tools_get_entity_and_relationship(self.graph_database.get_all_entities_by_label, 
            self.graph_database.get_entity_properties, self.graph_database.get_relationship_properties, self.graph_database.get_relationship_entities)
        self.add_or_update_tools = self.ontology.get_tools_add_or_update_entity_and_relationship(self.graph_database.add_or_update_entity, self.graph_database.add_relationship)        
        logger.system(f"Add/update tools returned")
        self.query_agent = QueryAgent(self.ontology,self.get_tools ) 
        logger.system(f"Query agent initialized")
        self.update_agent = UpdateAgent(self.ontology,self.add_or_update_tools)
        logger.system(f"Update agent initialized")
        self.rewrite_agent = QueryRewriteAgent(self.ontology,[])
        logger.system(f"Rewrite agent initialized")
        self.class_entity_pairs = {}
        cprint(f"KnowledgeGraph initialized", "green")

    def _get_class_entity_pairs(self):
        for entity_class in self.ontology.entity_classes:
            self.class_entity_pairs[entity_class.entity_class_name] = []
            entities = self.graph_database.get_all_entities_by_label(entity_class.entity_class_name)
            for entity in entities:
                self.class_entity_pairs[entity_class.entity_class_name].append(entity[entity_class.primary_key_prop.property_name])      

    def _rewrite_query(self, query: str):
        self._get_class_entity_pairs()
        return self.rewrite_agent.rewrite_query(query, self.class_entity_pairs)

    def query(self, query: str):
        """
        Executes a natural language query against the knowledge graph.

        Args:
            query (str): The natural language query to execute.

        Returns:
            str: The content of the agent's response.
        """
        logger.system(f"Querying knowledge graph with query: {query}")
        rewritten_query = self._rewrite_query(query)
        logger.system(f"Rewritten query: {rewritten_query}")
        return self.query_agent.query(rewritten_query)

    def update_knowledge(self, knowledge: str):
        """
        Updates the knowledge graph with new, unstructured information.

        Args:
            knowledge (str): A string of unstructured knowledge to add to the graph.

        Returns:
            str: The content of the agent's response.
        """
        logger.system(f"Updating knowledge graph with knowledge: {knowledge}")
        rewrite_knowledge = self._rewrite_query(knowledge)
        logger.system(f"Rewritten knowledge: {rewrite_knowledge}")
        result = self.update_agent.update(rewrite_knowledge)
        logger.system(f"Result: {result.content}")
        self.graph_database.save()
        logger.system(f"Graph database saved")
        return result.content

    def close(self):
        if self.graph_database is not None:
            self.graph_database.close()
        logger.system(f"Knowledge graph closed")
