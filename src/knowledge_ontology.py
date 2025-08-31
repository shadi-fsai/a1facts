import yaml
import sys
import os

class Property:
    def __init__(self, name: str, prop_type: str, description: str, primary_key: bool = False):
        self.name = name
        self.type = prop_type
        self.description = description
        self.primary_key = primary_key

    def __str__(self):
        pk_str = " - Primary Key" if self.primary_key else ""
        return f"{self.name} ({self.type}) - {self.description}{pk_str}"

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

    def get_add_or_update_tool(self, add_or_update_entity_func):
        primary_key_prop = next((prop for prop in self.properties if prop.primary_key), self.properties[0] if self.properties else None)

        if not primary_key_prop:
            return None

        description = f"Add or update a {self.name} entity. \n"
        description += f"Primary Key: {primary_key_prop.name}\n"
        for prop in self.properties:
            description += f"      - {prop}\n"

        def func(properties: dict):
            return add_or_update_entity_func(self.name, primary_key_prop.name, properties)

        return {
            "name": "add_or_update_entity_"+self.name,
            "description": description,
            "func": func
        }
    
    def get_get_tool(self, get_entity_func):
        description = f"Get a {self.name} entity. \n"
        for prop in self.properties:
            description += f"      - {prop}\n"

        def func(primary_key_value: str):
            return get_entity_func(self.name, primary_key_value)

        return {
            "name": "get_entity_"+self.name,
            "description": description,
            "func": func
        }

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

    def get_add_or_update_tool(self, add_or_update_relationship_func):
        description = f"Add or update a {self.name} relationship. \n"
        description += f"Domain: {self.domain} - Range: {self.range}\n"
        for prop in self.properties:
            description += f"   - {prop}\n"
            
        def func(properties: dict):
            return add_or_update_relationship_func(self.name, self.domain, self.range, properties)

        return {
            "name": "add_or_update_relationship_"+self.name,
            "description": description,
            "func": func
        }

    def get_get_tool(self, get_relationship_func):
        description = f"Get a {self.name} relationship. \n"
        description += f"Domain: {self.domain} - Range: {self.range}\n"
        for prop in self.properties:
            description += f"   - {prop}\n"
        def func(primary_key_value: str):
            return get_relationship_func(self.name, self.domain, self.range, primary_key_value)

        return {
            "name": "get_relationship_"+self.name,
            "description": description,
            "func": func
        }

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
                    entity_class.add_property(Property(prop.get('name', 'N/A'), prop.get('type', 'N/A'), prop.get('description', 'N/A'), prop.get('primary_key', False)))
                self.entity_classes.append(entity_class)
            for name, details in ontology.get('relationships', {}).items():
                relationship_class = RelationshipClass(name, details.get('domain', 'N/A'), details.get('range', 'N/A'), details.get('description', 'N/A'))
                relationship_class.properties = []                
                for prop in details.get('properties', []):
                    relationship_class.add_property(Property(prop.get('name', 'N/A'), prop.get('type', 'N/A'), prop.get('description', 'N/A'), prop.get('primary_key', False)))
                self.relationship_classes.append(relationship_class)

    def get_entity_add_or_update_tools(self, add_entity_func):
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_add_or_update_tool(add_entity_func))
        return tools

    def get_entity_get_tools(self, get_entity_func):
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_get_tool(get_entity_func))
        return tools

    def get_relationship_add_or_update_tools(self, add_relationship_func):
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_add_or_update_tool(add_relationship_func))
        return tools

    def get_relationship_get_tools(self, get_relationship_func):
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_get_tool(get_relationship_func))
        return tools

    def get_add_or_update_tools(self, add_entity_func, add_relationship_func):
        tools = []
        tools.extend(self.get_entity_add_or_update_tools(add_entity_func))
        tools.extend(self.get_relationship_add_or_update_tools(add_relationship_func))
        return tools

    def get_get_tools(self, get_entity_func, get_relationship_func):
        tools = []
        tools.extend(self.get_entity_get_tools(get_entity_func))
        tools.extend(self.get_relationship_get_tools(get_relationship_func))
        return tools

    def get_tools(self, get_entity_func, get_relationship_func, add_entity_func, add_relationship_func):
        tools = []
        tools.extend(self.get_entity_get_tools(get_entity_func))
        tools.extend(self.get_relationship_get_tools(get_relationship_func))
        tools.extend(self.get_entity_add_or_update_tools(add_entity_func))
        tools.extend(self.get_relationship_add_or_update_tools(add_relationship_func))
        return tools

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
