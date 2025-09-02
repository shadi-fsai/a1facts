import yaml
import sys
import os
from agno.tools.function import Function

from colored import cprint
from ontology.property import Property
from ontology.entity_class import EntityClass
from ontology.relationship_class import RelationshipClass
from ontology.ontology_rewrite_agent import OntologyRewriteAgent


class KnowledgeOntology:
    """
    Represents the entire ontology, including all entity and relationship classes.
    It loads the ontology from a YAML file and provides methods to access its components.
    """
    def __init__(self, ontology_file: str):
        """
        Initializes the KnowledgeOntology object.

        Args:
            ontology_file (str): The path to the YAML file defining the ontology.
        """
        self.ontology_file = ontology_file
        self.entity_classes = []
        self.relationship_classes = []
        self.name = ""
        self.description = ""
        self.load_ontology()
        self.rewrite_agent = OntologyRewriteAgent(self.ontology_file, [])

    def find_entity_class(self, name):
        """
        Finds an entity class by name.

        Args:
            name (str): The name of the entity class to find.

        Returns:
            EntityClass or None: The found entity class, or None if not found.
        """
        for entity_class in self.entity_classes:
            if entity_class.entity_class_name == name:
                return entity_class
        return None   
 
    def load_ontology(self):
        """Loads the ontology from the specified YAML file."""
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
        """
        Gets a list of all add/update tools for all entity classes.

        Args:
            add_entity_func (function): The function to call to add/update an entity.

        Returns:
            list: A list of tool functions.
        """
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_add_or_update_tool(add_entity_func))
        return tools

    def get_entity_get_entity_properties_tools(self, get_entity_properties_func):
        """
        Gets a list of all 'get properties' tools for all entity classes.

        Args:
            get_entity_properties_func (function): The function to call to get entity properties.

        Returns:
            list: A list of tool functions.
        """
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_get_entity_properties_tool(get_entity_properties_func))
        return tools

    def get_entity_get_all_entity_tool(self, get_all_entity_func):
        """
        Gets a list of all 'get all' tools for all entity classes.

        Args:
            get_all_entity_func (function): The function to call to get all entities.

        Returns:
            list: A list of tool functions.
        """
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_get_all_entity_tool(get_all_entity_func))
        return tools

    def get_relationship_add_or_update_tools(self, add_relationship_func):
        """
        Gets a list of all add/update tools for all relationship classes.

        Args:
            add_relationship_func (function): The function to call to add/update a relationship.

        Returns:
            list: A list of tool functions.
        """
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_add_or_update_tool(add_relationship_func))
        return tools

    def get_relationship_get_relationship_properties_tools(self, get_relationship_properties_func):
        """
        Gets a list of all 'get properties' tools for all relationship classes.

        Args:
            get_relationship_properties_func (function): The function to call to get relationship properties.

        Returns:
            list: A list of tool functions.
        """
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_get_relationship_properties_tool(get_relationship_properties_func))
        return tools

    def get_relationship_get_relationship_entities_tools(self, get_relationship_entities_func):
        """
        Gets a list of all 'get related entities' tools for all relationship classes.

        Args:
            get_relationship_entities_func (function): The function to call to get related entities.

        Returns:
            list: A list of tool functions.
        """
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_get_relationship_entities_tool(get_relationship_entities_func))
        return tools

    def get_add_or_update_tools(self, add_entity_func, add_relationship_func):
        """
        Gets a combined list of all add/update tools for both entities and relationships.

        Args:
            add_entity_func (function): The function to call to add/update an entity.
            add_relationship_func (function): The function to call to add/update a relationship.

        Returns:
            list: A list of all add/update tool functions.
        """
        tools = []
        tools.extend(self.get_entity_add_or_update_tools(add_entity_func))
        tools.extend(self.get_relationship_add_or_update_tools(add_relationship_func))
        return tools

    def get_get_tools(self, get_all_entity_func, get_entity_properties_func, get_relationship_properties_func, get_relationship_entities_func):
        """
        Gets a combined list of all 'get' tools for both entities and relationships.

        Args:
            get_all_entity_func (function): Function to get all entities.
            get_entity_properties_func (function): Function to get entity properties.
            get_relationship_properties_func (function): Function to get relationship properties.
            get_relationship_entities_func (function): Function to get related entities.

        Returns:
            list: A list of all 'get' tool functions.
        """
        tools = []
        tools.extend(self.get_entity_get_all_entity_tool(get_all_entity_func))
        tools.extend(self.get_entity_get_entity_properties_tools(get_entity_properties_func))
        tools.extend(self.get_relationship_get_relationship_properties_tools(get_relationship_properties_func))
        tools.extend(self.get_relationship_get_relationship_entities_tools(get_relationship_entities_func))
        return tools

    def __str__(self):
        """Returns a string representation of the entire ontology."""
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
