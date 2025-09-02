from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_acquirer import KnowledgeAcquirer

class A1C:
    def __init__(self, name: str, ontology_config_file: str, knowledge_sources_config_file: str):
        self.name = name
        self.ontology = KnowledgeOntology(ontology_config_file)
        self.graph = KnowledgeGraph(self.ontology)
        self.knowledge_acquirer = KnowledgeAcquirer(self.graph, self.ontology, knowledge_sources_config_file)
    def get_tools(self):
        def query_tool(query: str): 
            result = self.graph.query(query)
            return result

        def acquire_tool(query: str): 
            result = self.knowledge_acquirer.acquire(query)
            self.graph.update_knowledge(result)
            return result

        query_tool.__name__ = "query"
        query_tool.__doc__ = "Query the knowledge graph and knowledge acquirer\n" + \
            "ARGS: query: str - The query to query the knowledge graph and knowledge acquirer\n" + \
            "RETURNS: str - The result from the knowledge graph and knowledge acquirer"

        acquire_tool.__name__ = "acquire"
        acquire_tool.__doc__ = "Acquire knowledge from the knowledge acquirer and update the knowledge graph\n" + \
            "ARGS: query: str - The query to acquire knowledge from the knowledge acquirer\n" + \
            "RETURNS: str - The result from the knowledge acquirer"

        return [query_tool, acquire_tool]

    def __str__(self) -> str:
        return f"a1c('{self.name}', ontology='{self.ontology}', knowledge_acquirer={self.knowledge_acquirer})"

    def __del__(self) -> None:
        """
        Destructor that automatically closes the Neo4j graph connection
        when the a1c instance is garbage collected.
        """
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()