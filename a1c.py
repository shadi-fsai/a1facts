from owlready2 import *
from knowledge_source import knowledge_source
from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://82a2920f.databases.neo4j.io"
AUTH = ("neo4j", "E_ytyeg3qZqfnZxXv7AgBUEljyo5pqfV_VxDOdFWQp0")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

class a1c:
    def __init__(self, name, ontology, knowledge_sources):
        self.name = name
        self.ontology = ontology
        self.knowledge_sources = knowledge_sources

    def printOntology(self):
        print("Classes:")
        for cls in self.ontology.classes():
            print(f"  {cls.name}")
        
        print("Properties:")
        for prop in self.ontology.properties():
            domain_classes = prop.domain if prop.domain else []
            domain_names = [cls.name for cls in domain_classes] if domain_classes else ["No domain"]
            range_classes = prop.range if prop.range else []
            range_names = [cls.__name__ if hasattr(cls, '__name__') else str(cls) for cls in range_classes] if range_classes else ["No range"]
            print(f"  {prop.name} - Domain: {', '.join(domain_names)}, Range: {', '.join(range_names)}")
        
        print("Individuals:")
        for individual in self.ontology.individuals():
            print(f"  {individual.name}")

    def query(self, query):
        return "query"

    def __str__(self):
        ks_names = [ks.name for ks in self.knowledge_sources]
        return f"a1c('{self.name}', ontology='{self.ontology.name}', knowledge_sources={ks_names})"
