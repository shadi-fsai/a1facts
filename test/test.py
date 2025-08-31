import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from knowledge_ontology import KnowledgeOntology

def get_entity_func(label, primary_key_value):
    print(f"Entity found: {label}, {primary_key_value}")
def add_entity_func(label, primary_key_value, properties):
    print(f"Entity added: {label}, {primary_key_value}, {properties}")
    return 1

def get_relationship_func(label, domain, range, primary_key_value):
    print(f"Relationship found: {label}, {domain}, {range}, {primary_key_value}")
def add_relationship_func(label, domain, range, properties):
    print(f"Relationship added: {label}, {domain}, {range}, {properties}")

ontology = KnowledgeOntology("test/company.yaml")
tools = ontology.get_entity_add_or_update_tools(add_entity_func)
#print(tools[0])
print(tools[0]["func"]({"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology", "market_cap": 3000000000000, "founded": 1976, "headquarters": "Cupertino, CA"}))
exit()
tools = ontology.get_entity_get_tools(get_entity_func)
print(tools[0])
print(tools[0]["func"]("Apple Inc."))

tools = ontology.get_relationship_add_or_update_tools(add_relationship_func)
print(tools[0])
print(tools[0]["func"]({"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology", "market_cap": 3000000000000, "founded": 1976, "headquarters": "Cupertino, CA"}))
tools = ontology.get_relationship_add_or_update_tools(add_relationship_func)
print(tools[0])
print(tools[0]["func"]({"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology", "market_cap": 3000000000000, "founded": 1976, "headquarters": "Cupertino, CA"}))
tools = ontology.get_relationship_get_tools(get_relationship_func)
print(tools[0])
print(tools[0]["func"]("Apple Inc.", "Organization", "Organization", "AAPL"))
#print(ontology.entity_classes)
#print(ontology)