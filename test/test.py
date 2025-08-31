import yaml
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from knowledge_ontology import KnowledgeOntology

ontology = KnowledgeOntology("test/company.yaml")
print(ontology)