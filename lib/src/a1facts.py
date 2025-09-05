from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_acquirer import KnowledgeAcquirer
from colored import cprint

class KnowledgeBase:
    def __init__(self, name: str, ontology_config_file: str, knowledge_sources_config_file: str, use_neo4j: bool = False):
        self.name = name
        self.ontology = KnowledgeOntology(ontology_config_file)
        self.graph = KnowledgeGraph(self.ontology, use_neo4j)
        self.knowledge_acquirer = KnowledgeAcquirer(self.graph, self.ontology, knowledge_sources_config_file)
 

    #todo create external functions that can be used for non agent use case
    
    def get_tools(self):        
        def query_tool(query: str):
            cprint(f"Querying knowledge graph", "green")
            truncated_query = query[:70] + "..." if len(query) > 70 else query
            cprint(f"Query: {truncated_query}", "yellow")
            result = self.graph.query(query)
            return result

        def acquire_tool(query: str): 
            cprint(f"Acquiring knowledge", "green")
            truncated_query = query[:70] + "..." if len(query) > 70 else query
            cprint(f"Knowledge seeked: {truncated_query}", "yellow")
            result = self.knowledge_acquirer.acquire(query)
            self.graph.update_knowledge(result)
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

        return [query_tool, acquire_tool]

    def __str__(self) -> str:
        return f"a1facts('{self.name}', ontology='{self.ontology}', knowledge_acquirer={self.knowledge_acquirer})"

    def __del__(self) -> None:
        """
        Destructor that automatically closes the Neo4j graph connection
        when the a1facts instance is garbage collected.
        """
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()