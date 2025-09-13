import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__),  '..', '..', 'src'))

from a1facts.graph.networkx_graph_database import NetworkxGraphDatabase

def main():
    """
    Loads the NetworkX graph from the default pickle file and prints its contents.
    """
    graph_db = NetworkxGraphDatabase()
    graph_db.print_graph()

if __name__ == "__main__":
    main()

