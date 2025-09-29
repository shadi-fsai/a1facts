import asyncio
import sys
import os
import time
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent

def main():
    load_dotenv()
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib', 'src'))
    sys.path.append(os.path.dirname(__file__))  # Add current directory for function sources

    try:
        from a1facts.knowledge_base import KnowledgeBase
    except ImportError as e:
        print(f"[IMPORT ERROR]: {e}")
        return

    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("[WARNING] OPENAI_API_KEY not found in environment variables.")
        print("Please provide your OpenAI API key:")
        openai_key = input("Enter OpenAI API key: ").strip()
        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
        else:
            print("[ERROR] No API key provided. Exiting.")
            return

    print("[INFO] Initializing Clinical Trials Knowledge Agent...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(base_dir, "trials.yaml")
    sources_path = os.path.join(base_dir, "sources.yaml")
    try:
        a1facts = KnowledgeBase(
            "clinical_trials_agent",
            ontology_path,
            sources_path,
            use_neo4j=False,
            disable_exa=True
        )
    except Exception as e:
        print(f"[ERROR initializing KnowledgeBase]: {e}")
        return

    try:
        agent = Agent(
            name="clinical_trials_agent",
            role="get clinical trials information",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=a1facts.get_tools(),
            instructions=dedent("""You are a clinical trials intelligence agent that provides REAL-TIME data from pharmaceutical APIs. You MUST:
            1. ALWAYS start with query_tool to search the knowledge graph
            2. If query_tool doesn't provide current/sufficient data, IMMEDIATELY use acquire_tool to fetch live API data
            3. When calling acquire_tool, explicitly mention you're "Fetching live data from [source] API..."
            4. For calculations like BMI, medical terminology, or health topics, ALWAYS use acquire_tool to call the healthcare MCP server
            5. NEVER use internal training knowledge for ANY calculations or medical information - only use tool results
            6. ALWAYS cite the specific API endpoints and data sources used
            7. Include data freshness indicators (e.g., "Data retrieved from ClinicalTrials.gov API on [date]")
            8. Show API call details to prove data authenticity
            Format your responses to clearly show:
            📡 API DATA SOURCE: [which API was called]
            [SEARCH QUERY]: [what was searched]
            [RESULTS]: [data with sources]
            ⏰ RETRIEVED: [when the data was fetched]"""),
            markdown=True,
            debug_mode=True,
        )
    except Exception as e:
        print(f"[ERROR initializing Agent]: {e}")
        return

    # Load all evaluation queries
    queries = [
        "Calculate the BMI for a person who is 5'10\" tall and weighs 180 lbs. Then find clinical trials for obesity treatments that have reported results in the last year, and explain what obesity-related health topics are covered by those trials using the health topics tool."
        "Find recruiting clinical trials for metastatic melanoma, then search PubMed for recent review articles about the lead sponsor of the first trial found.",
        "Calculate the BMI for a person who is 1.8 meters tall and weighs 85kg. Then, find recruiting clinical trials for conditions related to their resulting BMI category.",
        "What is the ICD-10 code for 'Rheumatoid arthritis'? Then, find ongoing clinical trials for this condition.",
        "Find a completed Phase 3 trial for a CAR-T therapy. Then, search the NCBI bookshelf for literature on the mechanism of action of CAR-T cells.",
        "Look up 'Keytruda' on the FDA database to see who makes it. Then, find all PubMed articles from the last 2 years that mention its use in non-small cell lung cancer.",
        "Find active clinical trials sponsored by 'BioNTech' and also search medRxiv for any recent pre-print articles they may have published.",
        "Find the most recent completed trial for Alzheimer's disease. Take the NCT ID of that trial and find its entry on PubMed.",
        "List the warnings on the FDA label for 'Lenvima' (lenvatinib). Then, search for ongoing trials for any of the conditions mentioned in the indications.",
        "Find a clinical trial related to DICOM imaging. Then, use the health topics tool to explain what DICOM is to a layperson.",
        "Find the manufacturer of 'Xalkori' (crizotinib) using the FDA tool, then find all clinical trials they are currently sponsoring.",
        "Search PubMed for recent articles on 'Osimertinib'. Take the first author of the top result and see if they are listed as an investigator in any recruiting clinical trials.",
        "What are the known drug interactions for 'Paxlovid'? Then, find any clinical trials studying its use for conditions other than COVID-19, such as Long COVID.",
        "Find a completed clinical trial for 'Adcetris' (brentuximab vedotin). Then, look up its full FDA label information, focusing on dosage and administration.",
        "Are there any open access articles on medRxiv about 'T-cell exhaustion'? If so, find any active clinical trials that mention this term.",
        "What is the mechanism of action described on the NCBI Bookshelf for 'monoclonal antibodies'? Then, find phase 3 trials for a specific monoclonal antibody like 'Dupilumab'.",
        "Find the ICD-10 code for 'Glioblastoma'. Then, search PubMed for review articles on treatment options published in the last 3 years.",
        "A person is 5'5\" and 150 lbs. After calculating their BMI, find health topics related to their BMI category using the health topics tool.",
        "Find a recruiting trial for pediatric acute lymphoblastic leukemia. Then, check the FDA database for any boxed warnings on drugs mentioned in that trial's intervention description.",
        "Search for DICOM-related tools on the NCBI bookshelf, then find clinical trials that explicitly mention using DICOM for analysis in their study design.",
        "List the adverse reactions for 'Imbruvica' (ibrutinib). Then, search PubMed for articles discussing management of these specific reactions.",
        "Find a Phase 2 trial sponsored by 'AstraZeneca' that was completed in the last year. Then, search medRxiv for any pre-print results with the trial's NCT ID.",
        "What are the indications for 'Opdivo' (nivolumab)? For the first indication, find the 5 most recent articles on PubMed.",
        "Find a trial that was terminated for safety reasons. Then, look up the FDA adverse event reports for the drug involved.",
        "What is the ICD-10 code for 'Parkinson's disease'? Then, find general information health topics on the condition.",
        "Find a trial using 'CRISPR'. Then search the NCBI bookshelf for an introduction to CRISPR technology.",
        "Look up the drug 'Stelara' (ustekinumab). Find its indications, and then search for recruiting trials for a different condition not on the label, like 'Lupus Nephritis', to find expansion trials.",
        "Find a trial for a medical device used in cardiology, for example a 'stent'. Then search PubMed for performance reviews of that device type.",
        "Calculate the BMI for a person who is 6'2\" and 220 lbs. Then find PubMed articles related to health risks for their BMI category.",
        "Find the manufacturer of 'Skyrizi' (risankizumab). Then check for any pre-print articles on medRxiv from that manufacturer."
    ]

    print("="*80)
    print("🧪 TESTING CLINICAL TRIALS KNOWLEDGE AGENT (ALL 30 EVALUATION QUERIES)")
    print("="*80)

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}/30:")
        print(f"{query}")
        print(f"{'-' * 60}")

        try:
            result = asyncio.run(agent.arun(query))
            print("[RESULT]:")
            print(result.content)
        except Exception as e:
            print(f"[ERROR running query {i}]: {e}")

        print(f"{'-' * 60}")
        # Optional: Add a small delay between queries to avoid rate limits
        time.sleep(1)

    # Ensure we request a clean shutdown of MCP resources
    try:
        if 'a1facts' in locals() and hasattr(a1facts, 'close'):
            a1facts.close()
            # allow background MCP threads time to stop and event loop to close
            time.sleep(1.0)
    except Exception as e:
        print(f"[ERROR during cleanup]: {e}")

if __name__ == "__main__":
    main()