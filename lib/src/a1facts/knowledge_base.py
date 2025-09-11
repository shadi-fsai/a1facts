from a1facts.graph.knowledge_graph import KnowledgeGraph
from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.enrichment.knowledge_acquirer import KnowledgeAcquirer
from colored import cprint
from a1facts.utils.logger import logger


class KnowledgeBase:
    def __init__(self, name: str, ontology_config_file: str, knowledge_sources_config_file: str, use_neo4j: bool = False, disable_exa: bool = False):
        logger.system(f"Initializing KnowledgeBase for {name}")
        self.name = name
        self.ontology = KnowledgeOntology(ontology_config_file)
        self.graph = KnowledgeGraph(self.ontology, use_neo4j)
        self.knowledge_acquirer = KnowledgeAcquirer(self.graph, self.ontology, knowledge_sources_config_file, disable_exa)
        logger.system(f"KnowledgeBase initialized for {self.name}")

    def query(self, query: str):
        """
        Executes a query against the knowledge graph.

        This method allows you to retrieve information stored in the knowledge graph
        based on its ontological structure.

        Args:
            query (str): The query to execute against the knowledge graph.

        Returns:
            str: The result of the query from the knowledge graph.
        """
        logger.user(f"Querying knowledge graph for {query}")
        cprint(f"Querying knowledge graph", "green")
        truncated_query = query[:70] + "..." if len(query) > 70 else query
        cprint(f"Query: {truncated_query}", "yellow")
        return self.graph.query(query)

    def acquire_knowledge_for_query(self, query: str):
        """
        Acquires new knowledge based on a query and updates the knowledge graph.

        This method uses the configured knowledge sources to find new information
        related to the query, which is then integrated into the knowledge graph.

        Args:
            query (str): The query to guide the knowledge acquisition process.

        Returns:
            str: The newly acquired knowledge.
        """
        logger.user(f"Acquiring knowledge for {query}")
        cprint(f"Acquiring knowledge", "green")
        truncated_query = query[:70] + "..." if len(query) > 70 else query
        cprint(f"Knowledge seeked: {truncated_query}", "yellow")
        newknowledge = self.knowledge_acquirer.acquire(query)
        self.ingest_knowledge(newknowledge)
        return newknowledge
    
    def ingest_knowledge(self, knowledge: str):
        """
        Ingests and integrates new knowledge into the knowledge graph.

        This method takes a string of knowledge, processes it, and updates the
        knowledge graph according to the ontology.

        Args:
            knowledge (str): The knowledge to be ingested into the knowledge graph.

        Returns:
            str: The result of the knowledge ingestion operation.
        """
        logger.user(f"Ingesting knowledge for {knowledge}")
        cprint(f"Ingesting knowledge", "green")
        truncated_knowledge = knowledge[:70] + "..." if len(knowledge) > 70 else knowledge
        cprint(f"Knowledge to update: {truncated_knowledge}", "yellow")
        return self.graph.update_knowledge(knowledge)

    def get_tools(self):
        logger.system(f"Getting tools for {self.name}")
        def query_tool(query: str):
            return self.query(query)

        def acquire_tool(query: str):
            result = self.acquire_knowledge_for_query(query)
            return result

        query_tool.__doc__ = f"""Query the knowledge graph for precise information for {self.ontology.description}
ARGS: query: str - The query to query the knowledge graph
RETURNS: str - The result from the knowledge graph"""
        query_tool.__parameters__ = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to query the knowledge graph"
                }
            },
            "required": ["query"]
        }

        acquire_tool.__doc__ = f"""Acquire knowledge from the knowledge acquirer and update the knowledge graph for {self.ontology.description}
Objective: To get high reliability and credibility information from the knowledge sources
ARGS: query: str - The query to acquire knowledge from the knowledge acquirer
RETURNS: str - The result from the knowledge acquirer"""
        acquire_tool.__parameters__ = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to acquire knowledge from the knowledge acquirer"
                }
            },
            "required": ["query"]
        }
        logger.system(f"Tools returned for {self.name}")
        return [query_tool, acquire_tool]

    def __str__(self) -> str:
        return f"a1facts('{self.name}', ontology='{self.ontology}', knowledge_acquirer={self.knowledge_acquirer})"

    def __del__(self) -> None:
        """
        Destructor that automatically closes the Neo4j graph connection
        when the a1facts instance is garbage collected.
        """
        logger.system(f"Destroying KnowledgeBase for {self.name}")
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()
            logger.system(f"KnowledgeBase closed for {self.name}")