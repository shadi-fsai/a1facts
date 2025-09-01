import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from colored import cprint
from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_acquirer import KnowledgeAcquirer
#from agno.models.google import Gemini

import cProfile
import pstats
import io

def main():
    ontology = KnowledgeOntology("test/company.yaml")
    graph = KnowledgeGraph(ontology)
    finance_info_agent = KnowledgeAcquirer(graph, ontology, "test/knowledge_sources.yaml")
    query = "what do you know about how UnitedHealth competes with CVS?"
    #financeresponse = finance_info_agent.acquire(query)
    #cprint(financeresponse, 'blue')
    #exit()

    financeresponse = """
    UnitedHealth Group is one of the largest health insurance and managed care companies in the world. Its primary competitors include companies that operate in the health insurance and healthcare services sectors, both in the United States and, in some cases, internationally.

    Below is a table of UnitedHealth Group’s major competitors:

    | Company Name         | Description                                                               | Primary Segments                   |
    |----------------------|---------------------------------------------------------------------------|------------------------------------|
    | Anthem (Elevance Health)   | One of the largest health benefit companies in the US.                  | Health insurance, Medicaid/Medicare|
    | CVS Health (Aetna)    | Diversified health services with Aetna insurance and retail pharmacies.   | Health insurance, Pharmacy         |
    | Cigna                 | Global health services organization.                                      | Health insurance, Pharmacy benefits|
    | Humana                | Focuses primarily on Medicare Advantage plans.                            | Health insurance, Medicare         |
    | Centene Corporation   | Major provider of Medicaid and government-sponsored plans.                | Medicaid, Medicare, Marketplace    |
    | Molina Healthcare     | Specializes in government-sponsored health care programs.                 | Medicaid, Medicare                 |
    | Kaiser Permanente     | Integrated managed care consortium (insurer and provider).                | Health insurance, Healthcare delivery|
    | Blue Cross Blue Shield Association | Federation of independent health insurance organizations in the US. | Health insurance                   |

    ### Additional Noteworthy Competitors
    - **Magellan Health**: Specialty health care management.
    - **Health Care Service Corporation (HCSC)**: Operates several Blue Cross/Blue Shield plans.
    - **Oscar Health**: Technology-driven health insurance.
    - **Bright Health Group**: Focuses on tailored health insurance plans.

    ### Notes:
    - The competitive landscape changes as providers and insurers expand vertically (e.g., acquisitions by CVS, Cigna) and through new health tech entrants.
    - UnitedHealth also competes with regional insurers and, to a lesser extent, with companies providing health services, analytics, and pharmacy benefits management.

    **Information confirmed by:**
    - [UnitedHealth Group 2024 Annual Report] (Confirmed)
    - [Yahoo Finance - UnitedHealth Competitors] (Confirmed)
    - [Morningstar Sector Analysis] (Confirmed)"""

    #ontoresponse = graph.update_knowledge(financeresponse)
    #cprint(ontoresponse, 'green')

    #exit()  


    import time
    start_time = time.time()
    knowledge_base_response = graph.query(query)
    end_time = time.time()
    cprint(f"Knowledge base query took {end_time - start_time:.2f} seconds", 'red')
    cprint(knowledge_base_response, 'yellow')
    print("*"*150)
    #exit()
    return
    start_time = time.time()
    financeresponse = finance_info_agent.acquire(query)
    end_time = time.time()
    cprint(f"Finance info query took {end_time - start_time:.2f} seconds", 'red')
    cprint(financeresponse, 'blue')
    print("*"*150)
    start_time = time.time()
    ontoresponse = graph.update_knowledge(financeresponse)
    cprint(ontoresponse, 'green')
    #cprint(ontoresponse.content, 'green')
    end_time = time.time()
    cprint(f"Ontology & knoweldge graph update {end_time - start_time:.2f} seconds", 'red')

    graph.close()

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats(50)
    print(s.getvalue())
