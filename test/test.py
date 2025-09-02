import sys
import os
import time
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
    start_time = time.time()

    ontology = KnowledgeOntology("test/company.yaml")
    graph = KnowledgeGraph(ontology)
    query = "Do you know who is the CEO of Cigna?"
    knowledge_base_response = graph.query(query)
    cprint(knowledge_base_response, 'yellow')

    print("*"*150)
    end_time = time.time()
    cprint(f"Knowledge base query took {end_time - start_time:.2f} seconds", 'red')
    
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



