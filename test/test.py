import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from knowledge_ontology import KnowledgeOntology

def get_entity_func(label, primary_key_value):
    return(f"Entity found: {label}, {primary_key_value}")
def add_entity_func(label, primary_key_value, properties):
    return f"Entity added: {label}, {primary_key_value}, {properties}"
def add_relationship_func(label, domain, domain_primary_key_value, range, range_primary_key_value, properties, symmetric):
    return f"Relationship added: {label}, {domain}, {domain_primary_key_value}, {range}, {range_primary_key_value}, {properties}, {symmetric}"
def get_relationship_func(domain, domain_primary_key_value, range, range_primary_key_value, relationship_name):
    return f"Relationship found: {domain}, {domain_primary_key_value}, {relationship_name}, {range}, {range_primary_key_value} "
    #add_or_update_relationship_func(self.domain_entity_class, domain_primary_key_value, self.range_entity_class,  range_primary_key_value, self.relationship_name, properties, self.symmetric)

def get_relationship_properties_func(domain, domain_primary_key_value, range, range_primary_key_value, relationship_name):
    return f"Relationship properties found: {domain}, {domain_primary_key_value}, {relationship_name}, {range}, {range_primary_key_value} "
def get_relationship_entities_func(domain, domain_primary_key_value, relationship_name, range, range_primary_key_value):
    return f"Fetching {range}s linked to {domain} in {relationship_name} relationship: {domain}, {domain_primary_key_value} to {range}, {range_primary_key_value} "

ontology = KnowledgeOntology("test/company.yaml")
import inspect
#print(inspect.signature(tools[0]["func"]))
#print(tools[0])
#print(tools[0]["func"]("Apple Inc.", "Consumer Electronics", {}))
#exit()

tools = ontology.get_relationship_get_relationship_entities_tools(get_relationship_entities_func)
print(tools[0])
print(inspect.signature(tools[0]["func"]))

print(tools[0]["func"]("Apple Inc."))
#print(ontology.entity_classes)
#print(ontology)