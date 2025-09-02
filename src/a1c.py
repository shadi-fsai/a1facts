from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_acquirer import KnowledgeAcquirer

class A1C:
    def __init__(self, name: str, ontology_config_file: str, knowledge_sources_config_file: str):
        self.name = name
        self.ontology = KnowledgeOntology(ontology_config_file)
        self.graph = KnowledgeGraph(self.ontology)
        self.knowledge_acquirer = KnowledgeAcquirer(self.graph, self.ontology, knowledge_sources_config_file)
    def get_tool(self):
        def query(query: str): 
            result = self.graph.query(query)
            if (result.found): #!TODO! doesn't return this yet 
                return result.data

            result = self.knowledge_acquirer.acquire(query)
            if (result):
                self.graph.update_knowledge(result)
                return result

        query.__name__ = "query"
        query.__doc__ = "Query the knowledge graph and knowledge acquirer\n" + \
            "ARGS: query: str - The query to query the knowledge graph and knowledge acquirer\n" + \
            "RETURNS: str - The result from the knowledge graph and knowledge acquirer"

        return query

    def __str__(self) -> str:
        return f"a1c('{self.name}', ontology='{self.ontology}', knowledge_acquirer={self.knowledge_acquirer})"

    def __del__(self) -> None:
        """
        Destructor that automatically closes the Neo4j graph connection
        when the a1c instance is garbage collected.
        """
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()