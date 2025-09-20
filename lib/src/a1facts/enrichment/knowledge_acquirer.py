from a1facts.graph.knowledge_graph import KnowledgeGraph
from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.enrichment.knowledge_source import KnowledgeSource
from a1facts.enrichment.function_knowledge_source.knowledge_source import FunctionKnowledgeSource
from a1facts.enrichment.mcp_knowledge_source.knowledge_source import MCPKnowledgeSource
from a1facts.utils.modelconfig import my_high_precision_model
from agno.agent import Agent
from textwrap import dedent
from agno.tools.exa import ExaTools
from datetime import datetime
import yaml
from colored import cprint
from a1facts.utils.logger import logger
import pickle
import os
import hashlib


class KnowledgeAcquirer:
    def __init__(self, graph: KnowledgeGraph, ontology: KnowledgeOntology, knowledge_sources_config_file: str, disable_exa: bool = False):
        logger.user(f"Initializing Knowledge Sources for {knowledge_sources_config_file} with disable_exa: {disable_exa}")
        self.ontology = ontology
        self.graph = graph
        self.knowledge_sources = self.load_knowledge_sources(knowledge_sources_config_file)
        logger.system(f"Knowledge sources loaded")
        for source in self.knowledge_sources:
            logger.system(f"Knowledge source loaded: {source.name}")
        self.tools = []
        if not disable_exa:
            self.tools.append(ExaTools(num_results=20, summary=True))
            logger.system(f"Exa tools loaded")
        for source in self.knowledge_sources:
            self.tools.append(source.query_tool())
            logger.system(f"Knowledge source query tool loaded: {source.name}")
        self.tools.append(self.graph.get_tools)
        self.agent = Agent(
            name="Knowledge Acquirer",
            role=dedent("""Enrich and update the knowledge graph with validated information from the knowledge sources.
            Always provide the sources for the answer. Never make up sources.
            If the sources come from the knowledge graph, provide the actual content of the "sources" property of the entity/relationship.
            Never cite the knowledge graph itself as a source.
            """),
            model=my_high_precision_model,
            tools=self.tools,
            instructions=self.get_acquisition_instructions(),
            markdown=True,
            debug_mode=False,
        )
        logger.user(f"KnowledgeAcquirer initialized")
        cprint(f"KnowledgeAcquirer initialized", "green")

    def get_acquisition_instructions(self):

        cache_file = 'acquirer_instructions.pickle'
        ontology_str = str(self.ontology)
        current_ontology_hash = hashlib.sha256(ontology_str.encode('utf-8')).hexdigest()
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)

                if cached_data.get('ontology_hash') == current_ontology_hash:
                    logger.system(f"Using cached acquisition instructions")
                    return cached_data['instructions']
            except (pickle.UnpicklingError, EOFError, KeyError) as e:
                # Handle cases where the pickle file is corrupt or has unexpected format
                print(f"Cache file {cache_file} is invalid, regenerating. Error: {e}")
        # Cache miss or invalid cache file
        instructions = self.ontology.rewrite_agent.rewrite_query(self.get_template())
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'ontology_hash': current_ontology_hash,
                'instructions': instructions
            }, f)
        logger.system(f"Acquisition instructions cached")

        return instructions

    def acquire(self, query: str):
        result = self.agent.run(query)
        cprint(f"KnowledgeAcquirer result: {result.content}", "green")
        return result.content

    def load_knowledge_sources(self, knowledge_sources_config_file: str):
        knowledge_sources = []
        logger.system(f"Loading knowledge sources from {knowledge_sources_config_file}")
        with open(knowledge_sources_config_file, 'r') as file:
            knowledge_sources_config = yaml.load(file, Loader=yaml.FullLoader)
            logger.system(f"Knowledge sources config loading from {knowledge_sources_config}")
            if knowledge_sources_config.get('knowledge_sources'):
                for source in knowledge_sources_config['knowledge_sources']:
                    if 'type' not in knowledge_sources_config['knowledge_sources'][source]:
                        logger.warning(f"Your knowledge source config is missing the 'type' field for source: {source}")
                        raise ValueError(f"Your knowledge source config is missing the 'type' field for source: {source}")
                    source_type = knowledge_sources_config['knowledge_sources'][source]['type']
                    if source_type == 'function':
                        source_config = knowledge_sources_config['knowledge_sources'][source]
                        source = FunctionKnowledgeSource(source_config)
                        knowledge_sources.append(source)
                    elif source_type == 'mcp':
                        source_config = knowledge_sources_config['knowledge_sources'][source]
                        source = MCPKnowledgeSource(source_config)
                        knowledge_sources.append(source)
                    else: 
                        logger.warning(f"Unknown knowledge source type: {source_type}")
            else: 
                logger.warning(f"No knowledge sources found in {knowledge_sources_config_file}")
        return knowledge_sources

    def get_template(self):
        return dedent(f"""(Template Instructions: Before use, replace the bracketed placeholders [...] with the specific details relevant to your target ontology and knowledge base.)

Goal:
Expand the knowledge graph to answer the user's query with validated and reliable information.
Return the full answer to the user's query.

Procedure:
1. Query the knowledge graph to retrieve relevant entities and relationships.    
1.2. If the knowledge graph lacks the necessary information(entities, properties, relationships or outdated information), query the knowledge sources (including the web) to supplement the knowledge graph.
1.3. If the knowledge graph has the necessary information, and the information is guaranteed to be current, return the answer to the user's query.
1.4. If the knowledge graph has the necessary information, but the information is not guaranteed to be current, query the knowledge sources (including the web) to supplement the knowledge graph.
1.5. If the knowledge graph lacks the necessary information, and the information is not guaranteed to be current, query the knowledge sources (including the web) to supplement the knowledge graph.
1.6. If the knowledge sources lack the necessary information, return "A verifiable answer is not available".

2. Data Supplementation & Vetting
Prioritization: Always prioritize foundational data that pertains to [Main entity classes] and [Main relationship types] from the [knowledge graph]

Web Search Scope: Use web searches to find:
1. Real-time or very recent data not available in the knowledge base.
2. The latest news, press releases, or official filings.
3. Broader contextual information (e.g., economic indicators, industry trends).
4. Third-party analysis (e.g., analyst ratings, reviews).

For information coming from knowledge sources that have a reliability rating of A or B, you can use the information directly.

IMPORTANT:
3. Source Reliability Assessment: Evaluate each web source using the following scale: [Keep these verbatim in your transformation to the ontology given]
    A: Completely reliable - The source is undoubtedly authentic and trustworthy.
    B: Usually reliable - Minor doubts exist, but the source is historically valid.
    C: Fairly reliable - Doubts exist, but the source has provided valid information before.
    D: Not usually reliable - Significant doubts about the source's reliability.
    E: Unreliable - The source has a history of providing invalid information.
    F: Reliability cannot be judged - Insufficient information for evaluation.
Constraint: Never use sources rated D, E, or F.

IMPORTANT:
4. Information Synthesis & Validation [Keep these verbatim in your transformation to the ontology given]
Information Validity Assessment: After gathering information, assess each piece of data across all sources using this scale:
    1. Confirmed: Corroborated by multiple, independent, reliable sources.
    2. Probably true: Logical and consistent with other data, but not fully corroborated.
    3. Possibly true: Plausible but lacks strong corroboration.
    4. Doubtful: Not logical or may be contradicted by other information.
    5. Improbable: Illogical and contradicted by other information.
    6. Cannot be judged: Insufficient information to assess validity.
Constraint: Only use information assessed as Confirmed, Probably true, or Possibly true.

Timeliness: Ensure all data is current relative to the date below.

5. Output Formatting
Data Display: Use tables to present quantitative and comparative data.
Use bullet points to present qualitative and descriptive data.

Citation: When information is Confirmed by multiple sources, cite those sources in your response.
Always provide sources for your answer, the sources should be extracted from the properties of the entities in the knowledge graph; you should get them when you get the information from the graph.          
Current Date: {datetime.now().strftime("%Y-%m-%d")}
""")
