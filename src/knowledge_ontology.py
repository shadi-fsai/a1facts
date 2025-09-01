import yaml
import sys
import os
from agno.tools.function import Function

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
        entity_str += f"{self.entity_class_name} ({self.description})\n"
        entity_str += "      Properties:\n"
        for prop in self.properties:
            entity_str += f"      - {prop}\n"
        return entity_str

    def get_add_or_update_tool(self, add_or_update_entity_func):
        primary_key_prop = next((prop for prop in self.properties if prop.primary_key), self.properties[0] if self.properties else None)
        if not primary_key_prop:
            return None

        def func(**kwargs):
            properties = kwargs.get('kwargs', kwargs)
            return add_or_update_entity_func(self.entity_class_name, primary_key_prop.property_name, properties)

        func.__name__ = "add_or_update_" + self.entity_class_name + "_information"
        func.__doc__ = f"Add or update a {self.entity_class_name} entity. Primary key: {primary_key_prop.property_name}"
        func.__parameters__ = self.get_tool_parameters_schema()
        return func

    def get_tool_parameters_schema(self):
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for prop in self.properties:
            prop_type = "string"
            if prop.type == "float":
                prop_type = "number"
            elif prop.type == "integer":
                prop_type = "integer"
            
            schema["properties"][prop.property_name] = {
                "type": prop_type,
                "description": prop.description
            }
            schema["required"].append(prop.property_name)
        return schema
    
    def get_get_all_entity_tool(self, get_all_entity_func):
        def func():
            return get_all_entity_func(self.entity_class_name)

        func.__name__ = "get_all_"+self.entity_class_name+"_entities"
        func.__doc__ = f"Get all {self.entity_class_name} entities."
        func.__parameters__ = {"type": "object", "properties": {}}
        return func

    def get_get_entity_properties_tool(self, get_entity_properties_func):
        def func(**kwargs):
            properties = kwargs.get('kwargs', kwargs)
            param_name = f"{self.entity_class_name}_{self.primary_key_prop.property_name}"
            primary_key_value = properties.get(param_name)
            return get_entity_properties_func(self.entity_class_name, primary_key_value)

        func.__name__ = "get_"+self.entity_class_name+"_properties"
        func.__doc__ = f"Get a {self.entity_class_name} properties."
        
        param_name = f"{self.entity_class_name}_{self.primary_key_prop.property_name}"
        func.__parameters__ = {
            "type": "object",
            "properties": {
                param_name: {
                    "type": "string",
                    "description": f"The {self.primary_key_prop.property_name} of the {self.entity_class_name}"
                }
            },
            "required": [param_name]
        }
        return func

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
        def func(**kwargs):
            properties = kwargs.get('kwargs', kwargs)
            domain_param_name, range_param_name = self._get_param_names()
            domain_primary_key_value = properties.get(domain_param_name)
            range_primary_key_value = properties.get(range_param_name)
            props = properties.get("properties")
            self.validate_properties(props)
            
            return add_or_update_relationship_func(
                self.domain_entity_class, 
                domain_primary_key_value, 
                self.range_entity_class,  
                range_primary_key_value, 
                self.relationship_name, 
                props, 
                self.symmetric
            )

        func.__name__ = f"add_link_{self.domain_entity_class}_{self.relationship_name}_{self.range_entity_class}"
        func.__doc__ = f"Add or update a [{self.relationship_name}] relationship between a [{self.domain_entity_class}] and [{self.range_entity_class}]\n"+\
            f"Domain Primary Key: from_{self.domain_entity_class}_{self.domain_primary_key_prop}\n"+\
            f"Range Primary Key: to_{self.range_entity_class}_{self.range_primary_key_prop}"+\
            (f"Properties: {self.properties}" if self.properties else "")
        func.__parameters__ = self.get_tool_parameters_schema()
        return func

    def _get_param_names(self):
        domain_param_name = f"from_{self.domain_entity_class}_{self.domain_primary_key_prop}"
        range_param_name = f"to_{self.range_entity_class}_{self.range_primary_key_prop}"
        return domain_param_name, range_param_name

    def get_tool_parameters_schema(self):
        domain_param_name, range_param_name = self._get_param_names()

        schema = {
            "type": "object",
            "properties": {
                domain_param_name: {
                    "type": "string",
                    "description": f"The {self.domain_primary_key_prop} of the FROM entity ({self.domain_entity_class})"
                },
                range_param_name: {
                    "type": "string",
                    "description": f"The {self.range_primary_key_prop} of the TO entity ({self.range_entity_class})"
                }
            },
            "required": [domain_param_name, range_param_name]
        }

        if self.properties:
            props_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            for prop in self.properties:
                prop_type = "string"
                if prop.type == "float":
                    prop_type = "number"
                elif prop.type == "integer":
                    prop_type = "integer"

                props_schema["properties"][prop.property_name] = {
                    "type": prop_type,
                    "description": prop.description
                }
                props_schema["required"].append(prop.property_name)
            
            schema["properties"]["properties"] = props_schema
        
        return schema

    def get_get_relationship_properties_tool(self, get_relationship_properties_func):
        def func(**kwargs):
            properties = kwargs.get('kwargs', kwargs)
            domain_param_name, range_param_name = self._get_param_names()
            domain_primary_key_value = properties.get(domain_param_name)
            range_primary_key_value = properties.get(range_param_name)
            return get_relationship_properties_func( self.domain_entity_class, domain_primary_key_value, self.range_entity_class, range_primary_key_value,self.relationship_name)

        func.__name__ = f"get_relationship_properties_{self.domain_entity_class}_{self.relationship_name}_{self.range_entity_class}"
        func.__doc__ = f"Get a {self.relationship_name} relationship properties."
        
        domain_param_name, range_param_name = self._get_param_names()
            
        func.__parameters__ = {
            "type": "object",
            "properties": {
                domain_param_name: {"type": "string", "description": f"The {self.domain_primary_key_prop} of the FROM entity ({self.domain_entity_class})"}, 
                range_param_name: {"type": "string", "description": f"The {self.range_primary_key_prop} of the TO entity ({self.range_entity_class})"}
            },
            "required": [domain_param_name, range_param_name]
        }
        return func

    def get_get_relationship_entities_tool(self, get_relationship_entities_func):
        def func(**kwargs):
            properties = kwargs.get('kwargs', kwargs)
            domain_param_name, _ = self._get_param_names()
            domain_primary_key_value = properties.get(domain_param_name)
            return get_relationship_entities_func( self.domain_entity_class, domain_primary_key_value, self.relationship_name, self.range_entity_class, self.range_primary_key_prop)

        func.__name__ = f"get_{self.range_entity_class}s_{self.domain_entity_class}_{self.relationship_name}"
        func.__doc__ = f"Get all {self.range_entity_class}s linked to a {self.domain_entity_class} in a {self.relationship_name} relationship."

        domain_param_name, _ = self._get_param_names()

        func.__parameters__ = {
            "type": "object",
            "properties": {
                domain_param_name: {"type": "string", "description": f"The {self.domain_primary_key_prop} of the FROM entity ({self.domain_entity_class})"}
            },
            "required": [domain_param_name]
        }
        return func


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

    def get_entity_get_all_entity_tool(self, get_all_entity_func):
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_get_all_entity_tool(get_all_entity_func))
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

    def get_relationship_get_relationship_entities_tools(self, get_relationship_entities_func):
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_get_relationship_entities_tool(get_relationship_entities_func))
        return tools

    def get_add_or_update_tools(self, add_entity_func, add_relationship_func):
        tools = []
        tools.extend(self.get_entity_add_or_update_tools(add_entity_func))
        tools.extend(self.get_relationship_add_or_update_tools(add_relationship_func))
        return tools

    def get_get_tools(self, get_all_entity_func, get_entity_properties_func, get_relationship_properties_func, get_relationship_entities_func):
        tools = []
        tools.extend(self.get_entity_get_all_entity_tool(get_all_entity_func))
        tools.extend(self.get_entity_get_entity_properties_tools(get_entity_properties_func))
        tools.extend(self.get_relationship_get_relationship_properties_tools(get_relationship_properties_func))
        tools.extend(self.get_relationship_get_relationship_entities_tools(get_relationship_entities_func))
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
