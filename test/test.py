import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from colored import cprint
from graph.knowledge_graph import KnowledgeGraph
from ontology.knowledge_ontology import KnowledgeOntology
from enrichment.knowledge_acquirer import KnowledgeAcquirer
#from agno.models.google import Gemini
from a1c import A1C

import cProfile
import pstats
import io

def main():
    start_time = time.time()
    knowledge_sources_config_file = "test/sources.yaml"
    ontology_file = "test/company.yaml"
    a1c = A1C("a1c", ontology_file, knowledge_sources_config_file)
    knowledge_acquirer = a1c.knowledge_acquirer
    print(knowledge_acquirer.acquire("How many employees does Apple have?"))
    graph = a1c.graph
    print(graph.query("How many employees does Apple have?"))
    exit()
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



