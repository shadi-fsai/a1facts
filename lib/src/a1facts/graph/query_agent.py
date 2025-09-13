from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.utils.modelconfig import my_query_model, my_fast_tool_calling_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from colored import cprint

class QueryAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology        
        self.agent = Agent(
            name="Knowledge Graph Agent",
            role="Interact with the knowledge graph",
            model=my_fast_tool_calling_model,
            tools=mytools,
            instructions=dedent(f"""
                Get information from the knowledge base.
                Use the tools to get information from the graph.
                Today is {datetime.now().strftime("%Y-%m-%d")}

                Only use information from the knowledge graph to answer the question, do not use your own knowledge, do not make up answers. 
                If you don't know the answer, say "A verifiable answer is not available" - don't add any other text.

                Provide all sources for your answer, the sources should be extracted from the properties of the entities in the knowledge graph; you should get them when you get the information from the graph.          
                """),
                markdown=True,
                debug_mode=False,
            )

    def query(self, query: str):
        # Try to answer with the knowledge graph first
        result = self.agent.run(dedent(f"""Answer the question in %QUERY%, 
        Use as many tools as you need to get the information necessary to answer the query.
        %QUERY%: {query}"""))     

        return result.content