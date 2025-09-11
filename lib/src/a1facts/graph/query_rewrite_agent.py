from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.utils.modelconfig import my_query_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from colored import cprint




class QueryRewriteAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology        
        self.agent = Agent(
            name="Query rewrite agent",
            role="Rewrite the query to use known entities",
            model=my_query_model,
            tools=mytools,
            instructions=dedent("""
                Rewrite the query to use known entities.
                """),
                markdown=True,
                debug_mode=False,
            )
    
    def rewrite_query(self, query: str, class_entity_pairs: dict):
        #print(class_entity_pairs)
        #cprint(query, 'yellow')
        prompt = dedent(f"""
            Rewrite the query to use known entities from the graph, for entities not in the graph keep the entity names as is.
            Here are the known entity pairs: {class_entity_pairs}
            Here is the query to rewrite: {query}
            Only return the rewritten query, no other text.
            """
        )

        result = self.agent.run(prompt)
        #cprint(result.content, 'green')
        return result.content