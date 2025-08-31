import yaml
import sys
import os

class Property:
    def __init__(self, name: str, prop_type: str, description: str):
        self.name = name
        self.type = prop_type
        self.description = description
    
    def __str__(self):
        return f"{self.name} ({self.type}) - {self.description}"

class EntityClass:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.properties = []
    def add_property(self, property: Property):
        self.properties.append(property)

    def __str__(self):
        entity_str = ""
        entity_str += f"{self.name} ({self.description})\n"
        entity_str += "      Properties:\n"
        for prop in self.properties:
            entity_str += f"      - {prop}\n"
        return entity_str

class RelationshipClass:
    def __init__(self, name: str, domain: EntityClass, range: EntityClass, description: str):
        self.name = name
        self.domain = domain
        self.range = range
        self.description = description
        self.properties = []

    def add_property(self, property: Property):
        self.properties.append(property)
    
    def __str__(self):
        relationship_str = ""
        relationship_str += f"{self.name} ({self.description}) - Domain: {self.domain} - Range: {self.range}\n"
        for prop in self.properties:
            relationship_str += f"   - {prop}\n"
        return relationship_str


class KnowledgeOntology:
    def __init__(self, ontology_file: str):
        self.ontology_file = ontology_file
        self.entity_classes = []
        self.relationship_classes = []
        self.name = ""
        self.description = ""
        self.load_ontology()

    def load_ontology(self):
        with open(self.ontology_file, 'r') as file:
            ontology = yaml.load(file, Loader=yaml.FullLoader)
            self.name = ontology.get('world', {}).get('name', 'N/A')
            self.description = ontology.get('world', {}).get('description', 'N/A')
            for name, details in ontology.get('entity_classes', {}).items():
                entity_class = EntityClass(name, details.get('description', 'N/A'))
                entity_class.properties = []                
                for prop in details.get('properties', []):
                    entity_class.add_property(Property(prop.get('name', 'N/A'), prop.get('type', 'N/A'), prop.get('description', 'N/A')))
                self.entity_classes.append(entity_class)
            for name, details in ontology.get('relationships', {}).items():
                relationship_class = RelationshipClass(name, details.get('domain', 'N/A'), details.get('range', 'N/A'), details.get('description', 'N/A'))
                relationship_class.properties = []                
                for prop in details.get('properties', []):
                    relationship_class.add_property(Property(prop.get('name', 'N/A'), prop.get('type', 'N/A'), prop.get('description', 'N/A')))
                self.relationship_classes.append(relationship_class)

    def __str__(self):
        ontology_str = ""
        ontology_str += f"Ontology Name: {self.name}\n"
        ontology_str += f"Ontology Description: {self.description}\n"
        ontology_str += "Entity Classes:\n"
        for entity_class in self.entity_classes:
            ontology_str += f"   {entity_class}\n"
        ontology_str += "Relationship Classes:\n"
        for relationship_class in self.relationship_classes:
            ontology_str += f"   {relationship_class}\n"
        return ontology_str
