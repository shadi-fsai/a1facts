from knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from knowledge_acquirer import KnowledgeAcquirer
from knowledge_source import KnowledgeSource

class a1c:
    def __init__(self, name: str, ontology_file: str, knowledge_sources: list[KnowledgeSource]):
        self.name = name
        self.ontology = KnowledgeOntology(ontology_file)
        self.knowledge_sources = knowledge_sources
        self.graph = KnowledgeGraph(self.ontology)
        self.knowledge_acquirer = KnowledgeAcquirer(self.graph, self.ontology, self.knowledge_sources)

    def query(self, query: str): 
        result = self.graph.query(query)
        if (result.found):
            return result.data

        result = self.knowledge_acquirer.acquire(query)
        if (result):
            return result

        self.graph.update_knowledge(result)
    
        return "No result found"

    def __str__(self) -> str:
        ks_names = [ks.name for ks in self.knowledge_sources]
        return f"a1c('{self.name}', ontology='{self.ontology}', knowledge_sources={ks_names})"

    def __del__(self) -> None:
        """
        Destructor that automatically closes the Neo4j graph connection
        when the a1c instance is garbage collected.
        """
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()