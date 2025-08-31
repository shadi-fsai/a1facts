import yaml
import sys
import os

from colored import cprint

class Property:
    def __init__(self, name: str, prop_type: str, description: str, primary_key: bool = False):
        self.property_name = name
        self.type = prop_type
        self.description = description
        self.primary_key = primary_key

    def __str__(self):
        pk_str = " - Primary Key" if self.primary_key else ""
        return f"{self.property_name} ({self.type}) - {self.description}{pk_str}"

class EntityClass:
    def __init__(self, name: str, description: str):
        self.entity_class_name = name
        self.description = description
        self.properties = []
        self.primary_key_prop = None

    def add_property(self, property: Property):
        self.properties.append(property)
        if property.primary_key:
            self.primary_key_prop = property

    def __str__(self):
        entity_str = ""
        entity_str += f"{self.name} ({self.description})\n"
        entity_str += "      Properties:\n"
        for prop in self.properties:
            entity_str += f"      - {prop}\n"
        return entity_str

    def get_add_or_update_tool(self, add_or_update_entity_func):
        if not self.primary_key_prop:
            raise Exception(f"Primary key property not found for entity: {self.name}")

        description = f"Add or update a {self.name} entity. \n"
        description += f"Primary Key: {self.primary_key_prop.name}\n"
        for prop in self.properties:
            description += f"      - {prop}\n"

        def func(properties: dict):
            return add_or_update_entity_func(self.name, properties[self.primary_key_prop.name], properties)

        return {
            "name": "add_or_update_"+self.name+"_information",
            "description": description,
            "func": func
        }
    
    def get_get_entity_properties_tool(self, get_entity_properties_func):
        description = f"Get a {self.name} entity. \n"
        for prop in self.properties:
            description += f"      - {prop}\n"

        def func(primary_key_value: str):
            return get_entity_properties_func(self.name, primary_key_value)

        return {
            "name": "get_entity_properties_"+self.name,
            "description": description,
            "func": func
        }

class RelationshipClass:
    def __init__(self, name: str, domain: EntityClass, range: EntityClass, description: str, symmetric: bool = False):
        self.relationship_name = name
        self.domain_entity_class = domain.entity_class_name
        self.domain_primary_key_prop = domain.primary_key_prop.property_name
        self.domain_primary_key_type = domain.primary_key_prop.type
        self.range_entity_class = range.entity_class_name
        self.range_primary_key_prop = range.primary_key_prop.property_name
        self.range_primary_key_type = range.primary_key_prop.type
        self.description = description
        self.properties = []
        self.symmetric = symmetric

    def add_property(self, property: Property):
        self.properties.append(property)
    
    def __str__(self):
        relationship_str = ""
        relationship_str += f"{self.relationship_name} ({self.description}) - Domain: {self.domain_entity_class} - Range: {self.range_entity_class}\n"
        for prop in self.properties:
            relationship_str += f"   - {prop}\n"
        if self.symmetric:
            relationship_str += "   (This relationship is symmetric)\n"
        return relationship_str

    def is_symmetric(self):
        return self.symmetric

    def validate_properties(self, properties):
        if properties:
            for prop in self.properties:
                if prop.property_name not in properties:
                    raise Exception(f"Property {prop.property_name} not found in properties, you need to change the world model")

    def get_add_or_update_tool(self, add_or_update_relationship_func):
        description = f"Add or update a [{self.relationship_name}] relationship. between a [{self.domain_entity_class}] and [{self.range_entity_class}] {'symmetrically' if self.symmetric else 'asymmetrically'}\n"
        description += f"Args: domain_primary_key_value: [{self.domain_entity_class}]'s [{self.domain_primary_key_prop}]: {self.domain_primary_key_type}\n" 
        description += f"      range_primary_key_value: [{self.range_entity_class}]'s [{self.range_primary_key_prop}]: {self.range_primary_key_type}\n"
        if self.properties:
            description += f"      properties: dictionary of properties to add to the relationship. \n"
            for prop in self.properties:
                description += f"   - {prop.property_name}: {prop.type}\n"
        
        def func(domain_primary_key_value: str, range_primary_key_value: str, properties: dict = None):
            self.validate_properties(properties)
            return add_or_update_relationship_func(self.domain_entity_class, domain_primary_key_value, self.range_entity_class,  range_primary_key_value, self.relationship_name, properties, self.symmetric)

        return {
            "name": "add_link_"+self.domain_entity_class+"_"+self.relationship_name+"_"+self.range_entity_class,
            "description": description,
            "func": func
        }

    def get_get_relationship_properties_tool(self, get_relationship_properties_func):
        description = f"Get a {self.relationship_name} relationship properties. \n"
        description += f"Domain: {self.domain_entity_class} - Range: {self.range_entity_class}\n"
        for prop in self.properties:
            description += f"   - {prop}\n"
        def func(domain_primary_key_value: str, range_primary_key_value: str):
            return get_relationship_properties_func( self.domain_entity_class, domain_primary_key_value, self.range_entity_class, range_primary_key_value,self.relationship_name)

        return {
            "name": "get_relationship_properties_"+self.domain_entity_class+"_"+self.relationship_name+"_"+self.range_entity_class,
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

    def find_entity_class(self, name):
        for entity_class in self.entity_classes:
            if entity_class.entity_class_name == name:
                return entity_class
        return None   
 
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
                domain = self.find_entity_class(details.get('domain', 'N/A'))
                range = self.find_entity_class(details.get('range', 'N/A'))
                symmetric = details.get('symmetric', False)
                relationship_class = RelationshipClass(name, domain, range, details.get('description', 'N/A'), symmetric)
                relationship_class.properties = []                
                for prop in details.get('properties', []):
                    relationship_class.add_property(Property(prop.get('property_name', 'N/A'), prop.get('type', 'N/A'), prop.get('description', 'N/A'), prop.get('primary_key', False)))
                self.relationship_classes.append(relationship_class)

    def get_entity_add_or_update_tools(self, add_entity_func):
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_add_or_update_tool(add_entity_func))
        return tools

    def get_entity_get_entity_properties_tools(self, get_entity_properties_func):
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_get_entity_properties_tool(get_entity_properties_func))
        return tools

    def get_relationship_add_or_update_tools(self, add_relationship_func):
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_add_or_update_tool(add_relationship_func))
        return tools

    def get_relationship_get_relationship_properties_tools(self, get_relationship_properties_func):
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_get_relationship_properties_tool(get_relationship_properties_func))
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
