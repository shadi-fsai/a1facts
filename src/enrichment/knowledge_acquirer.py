from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_source import KnowledgeSource
from utils.modelconfig import my_model
from agno.agent import Agent
from textwrap import dedent
from agno.tools.exa import ExaTools
from datetime import datetime

class KnowledgeAcquirer:
    def __init__(self, graph: KnowledgeGraph, ontology: KnowledgeOntology, knowledge_sources_config_file: str):
        self.ontology = ontology
        self.graph = graph
        self.knowledge_sources_config_file = knowledge_sources_config_file
        self.knowledge_sources = self.load_knowledge_sources(self.knowledge_sources_config_file)
        self.tools = [ExaTools(num_results=20, summary=True)]
        for source in self.knowledge_sources:
            self.tools.append(source.query_tool())
        self.agent = Agent(
            name="Knowledge Acquirer",
            role="Get high reliability and credibility information from the knowledge sources",
            model=my_model,
            tools=self.tools,
            instructions=dedent(f""" Use tables to display data. 
                Follow these steps when answering questions:

                First, search the knowledge base for fundamental company data, historical performance, and established valuation models.
                If the information in the knowledge base is incomplete OR if the user asks for real-time data or recent news, search the web to fill in gaps.
                If you find all necessary fundamental data in the knowledge base, use it as the primary source for your analysis.
                Always prioritize knowledge base information (for fundamentals and valuation) over web results.
                If needed, supplement with web searches for:
                Real-time stock prices and market data.
                The latest financial news, press releases, and SEC filings.
                Broader economic indicators and industry trends.
                Analyst ratings and price targets.

                When using the web: 
                Search for at least 20 results per query. Use the tools to get the information.
                For each source assess their credibility and reliability using the following criteria:[
                A Completely reliable - There is no doubt about the source's authenticity, trustworthiness, or competency. The source has a history of complete reliability.
                B Usually reliable - There are minor doubts about the source's reliability. The source has a history of providing valid information most of the time.
                C Fairly reliable - There are doubts about the source's reliability, but they have provided valid information in the past.
                D Not usually reliable - There are significant doubts about the source's reliability.
                E Unreliable - The source has a history of providing invalid information.
                F Reliability cannot be judged - There is insufficient information to evaluate the source's reliability.]
                Never use sources that are rated D, E or F.

                When you are done synthesizing the information, assess each information based on the following criteria:[
                1. Confirmed - the information is confirmed by multiple different sources.
                2. Probably true - The information is logical and consistent with other information from different sources, but has not been fully corroborated.
                3. Possibly true - The information is reasonably logical, but cannot be judged to be probably true.
                4. Doubtful true - The information is not logical and may be contradicted by other information, but its falsehood cannot be confirmed.
                5. Improbable - The information is illogical and contradicted by other information.
                6. Credibility cannot be judged - There is insufficient information to assess the validity of the information.
                ]
                Only use information that is Confirmed, Probably true or Possibly true.
                Ensure that the information is not outdated relative to the current date.

                When information is confirmed by multiple sources, provide the sources in your reponse.

            Today is {datetime.now().strftime("%Y-%m-%d")}"""),
            show_tool_calls=True,
            markdown=True,
        )

    def acquire(self, query: str):
        result = self.agent.run(query)
        return result.content

    def load_knowledge_sources(self, knowledge_sources_config_file: str):
        return []
        #TODO YAML to parse different types of knowledge sources and their configurations
        