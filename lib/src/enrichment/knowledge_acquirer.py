from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_source import KnowledgeSource
from utils.modelconfig import my_model
from agno.agent import Agent
from textwrap import dedent
from agno.tools.exa import ExaTools
from datetime import datetime
import yaml
from colored import cprint

class KnowledgeAcquirer:
    def __init__(self, graph: KnowledgeGraph, ontology: KnowledgeOntology, knowledge_sources_config_file: str):
        self.ontology = ontology
        self.graph = graph
        self.knowledge_sources = self.load_knowledge_sources(knowledge_sources_config_file)
        self.tools = [ExaTools(num_results=20, summary=True)]
        for source in self.knowledge_sources:
            self.tools.append(source.query_tool())
        self.tools.append(self.graph.get_tools)
        self.agent = Agent(
            name="Knowledge Acquirer",
            role="Get high reliability and credibility information from the knowledge sources",
            model=my_model,
            tools=self.tools,
            instructions=self.ontology.rewrite_agent.rewrite_query(self.get_template()),
            show_tool_calls=True,
            markdown=True,
            debug_mode=False,
        )
        cprint(f"KnowledgeAcquirer initialized", "green")

    def acquire(self, query: str):
        result = self.agent.run(query)
        return result.content

    def load_knowledge_sources(self, knowledge_sources_config_file: str):
        knowledge_sources = []
        with open(knowledge_sources_config_file, 'r') as file:
            knowledge_sources_config = yaml.load(file, Loader=yaml.FullLoader)
            for source in knowledge_sources_config['knowledge_sources']:
                source_config = knowledge_sources_config['knowledge_sources'][source]
                source = KnowledgeSource(source_config['name'], source_config['description'], source_config['functions_file'], source_config['override_reliability'], source_config['override_credibility'])
                knowledge_sources.append(source)
        return knowledge_sources

    def get_template(self):
        return dedent(f"""(Template Instructions: Before use, replace the bracketed placeholders [...] with the specific details relevant to your target ontology and knowledge base.)

Objective
Answer user queries by synthesizing information from a structured knowledge base and supplementing it with verified web search results when necessary.

1. Information Retrieval Strategy
Primary Source: Your primary data source is the [Knowledge_Base_Name].

Initial Search: First, query the [Knowledge_Base_Name] to retrieve relevant [entities] and [relationships]. Prioritize searching for key entity types such as [e.g., Company, Product, Event].

Web Search Trigger: Conduct a web search only if:

The [Knowledge_Base_Name] lacks the necessary data (e.g., is missing entities, properties, or contains outdated information).

The user specifically requests real-time data or very recent news.

2. Data Supplementation & Vetting
Prioritization: Always prioritize foundational data (e.g., [describe the types of data in the KB, like fundamental data, historical performance, etc.]) from the [Knowledge_Base_Name] over web search results.

Web Search Scope: Use web searches to find:

Real-time or very recent data not available in the knowledge base.

The latest news, press releases, or official filings.

Broader contextual information (e.g., economic indicators, industry trends).

Third-party analysis (e.g., analyst ratings, reviews).

Source Reliability Assessment: Evaluate each web source using the following scale:

A: Completely reliable - The source is undoubtedly authentic and trustworthy.

B: Usually reliable - Minor doubts exist, but the source is historically valid.

C: Fairly reliable - Doubts exist, but the source has provided valid information before.

D: Not usually reliable - Significant doubts about the source's reliability.

E: Unreliable - The source has a history of providing invalid information.

F: Reliability cannot be judged - Insufficient information for evaluation.

Constraint: Never use sources rated D, E, or F.

3. Information Synthesis & Validation
Information Validity Assessment: After gathering information, assess each piece of data using this scale:

1. Confirmed: Corroborated by multiple, independent, reliable sources.

2. Probably true: Logical and consistent with other data, but not fully corroborated.

3. Possibly true: Plausible but lacks strong corroboration.

4. Doubtful: Not logical or may be contradicted by other information.

5. Improbable: Illogical and contradicted by other information.

6. Cannot be judged: Insufficient information to assess validity.

Constraint: Only use information assessed as Confirmed, Probably true, or Possibly true.

Timeliness: Ensure all data is current relative to the date below.

4. Output Formatting
Data Display: Use tables to present quantitative and comparative data.

Citation: When information is Confirmed by multiple sources, cite those sources in your response.

Current Date: {datetime.now().strftime("%Y-%m-%d")}""")
