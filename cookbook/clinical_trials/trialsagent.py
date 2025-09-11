import sys
import os
import time

from colored import cprint
from a1facts.knowledge_base import KnowledgeBase
from agno.agent import Agent
from textwrap import dedent
from a1facts.utils.modelconfig import my_model
import networkx as nx
import pickle


def main():
    a1facts = KnowledgeBase("clinical_trials_agent", "trials.yaml", "sources.yaml", use_neo4j=True)

    agent = Agent(
        name="clinical_trials_agent",
        role="get clinical trials information",
        model=my_model,
        tools=a1facts.get_tools(),
        instructions=dedent("""get clinical trials information, always start with query tool, if you don't get a satisfactory answer use the acquire tool to get new knowledge.
        never use your internal knowledge to answer the question, only use the tools to get information from the knowledge graph and the knowledge sources. - never make up information. Always provide sources"""),
        
        markdown=True,
        debug_mode=False,
    )
    query = """for each clinical trial, find the last endpoint data reported date, report their known cardivascular adverse events: [1) Maridebart cafraglutide (“MariTide”, Amgen) — GLP‑1R agonist + GIPR antagonist (monthly)
Trial / Phase / ID: Phase 2 obesity; randomized dose‑ranging; primary endpoint: % body‑weight change at 52 weeks. Read out June 2025 (NEJM + ADA). 


Result (primary): Mean weight change at 52 weeks ranged –12.3% to –16.2% (treatment‑policy estimand) vs –2.5% placebo; also robust HbA1c reduction in T2D cohort. Reported June 23, 2025. 


2) VK2735(Viking) — Dual GLP‑1/GIP receptor agonist, oral tablet
Trial / Phase / ID: VENTURE–Oral Dosing, Phase 2 obesity; primary endpoint: % body‑weight change at Week 13. Topline Aug 19, 2025. 


Result (primary): Up to –12.2% mean weight loss from baseline and up to –10.9% vs placebo at 13 weeks; met primary and secondary endpoints. 


3)  Pemvidutide (Altimmune) — Dual GLP‑1/glucagon receptor agonist, subcutaneous
Trial / Phase / ID: IMPACT Phase 2b in MASH (F2/F3); primary endpoint: MASH resolution without worsening of fibrosis at Week 24. Topline Jun 26, 2025. 


Result (primary): 59.1% (1.2 mg) and 52.1% (1.8 mg) achieved MASH resolution vs 19.1% placebo (p<0.0001); weight loss 5.0–6.2% at 24 wks. 



]"""
#    query = "List all Phase II clinical trials for drugs targeting GLP-1 that have reported primary endpoint data in the last 6 months, excluding those with known cardiovascular adverse events"
    result = agent.run(query)
    print(result.content)
    
if __name__ == "__main__":
    main()


'''graph = nx.DiGraph()
graph_file = "networkx_graph.pickle"
try:
    with open(graph_file, "rb") as f:
        graph = pickle.load(f)
except FileNotFoundError:
    pass
num_nodes = graph.number_of_nodes()
num_edges = graph.number_of_edges()
cprint(f"Successfully initialized Networkx database with {num_nodes} nodes, {num_edges} relationships.", "green")


print("All nodes in the graph:")
for node, data in graph.nodes(data=True):
    print(f"  Node: {node}, Data: {data}")

print("\nAll relationships in the graph:")
for start, end, data in graph.edges(data=True):
    print(f"  Edge: {start} -> {end}, Data: {data}")
'''