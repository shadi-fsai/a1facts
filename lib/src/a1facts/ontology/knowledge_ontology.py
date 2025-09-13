import yaml
import sys
import os
from agno.tools.function import Function

from colored import cprint
from a1facts.ontology.property import Property
from a1facts.ontology.entity_class import EntityClass
from a1facts.ontology.relationship_class import RelationshipClass
from a1facts.ontology.ontology_rewrite_agent import OntologyRewriteAgent
from a1facts.utils.telemetry import nonblocking_send_telemetry_ping
from a1facts.utils.logger import logger

class KnowledgeOntology:
    """
    Represents the entire ontology, including all entity and relationship classes.
    It loads the ontology from a YAML file and provides methods to access its components.
    """
    def __init__(self, ontology_file: str):
        logger.system(f"Initializing KnowledgeOntology for {ontology_file}")
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
        logger.system(f"Loading ontology from {ontology_file}")
        self.load_ontology()
        logger.system(f"Ontology loaded from {ontology_file}")
        self.rewrite_agent = OntologyRewriteAgent(self.ontology_file, [])
        logger.system(f"Ontology rewrite agent initialized")
        nonblocking_send_telemetry_ping()
        logger.user(f"Ontology loaded: {self.ontology_file}")
        logger.user(f"Ontology parsed: {str(self)}")
        

    def find_entity_class(self, name):
        """
        Finds an entity class by name.

        Args:
            name (str): The name of the entity class to find.

        Returns:
            EntityClass or None: The found entity class, or None if not found.
        """
        logger.system(f"Finding entity class: {name}")
        for entity_class in self.entity_classes:
            if entity_class.entity_class_name == name:
                return entity_class
        logger.system(f"Entity class not found: {name}")
        return None   
 
    def load_ontology(self):
        """Loads the ontology from the specified YAML file."""
        logger.system(f"Loading ontology from {self.ontology_file}")
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
                    relationship_class.add_property(Property(prop.get('name', 'N/A'), prop.get('type', 'N/A'), prop.get('description', 'N/A'), prop.get('primary_key', False)))
                self.relationship_classes.append(relationship_class)
        logger.system(f"Ontology loaded from {self.ontology_file}")

    def get_tools_add_or_update_entity(self, add_entity_func):
        """
        Gets a list of all add/update tools for all entity classes.

        Args:
            add_entity_func (function): The function to call to add/update an entity.

        Returns:
            list: A list of tool functions.
        """
        logger.system(f"Getting entity add/update tools")
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_tool_add_or_update_entity(add_entity_func))
        logger.system(f"Entity add/update tools returned")
        return tools

    def get_tools_get_entity_properties(self, get_entity_properties_func):
        """
        Gets a list of all 'get properties' tools for all entity classes.

        Args:
            get_entity_properties_func (function): The function to call to get entity properties.

        Returns:
            list: A list of tool functions.
        """
        logger.system(f"Getting entity get properties tools")
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_tool_get_entity_properties(get_entity_properties_func))
        logger.system(f"Entity get properties tools returned")
        return tools

    def get_tools_get_all_entity(self, get_all_entity_func):
        """
        Gets a list of all 'get all' tools for all entity classes.

        Args:
            get_all_entity_func (function): The function to call to get all entities.

        Returns:
            list: A list of tool functions.
        """
        logger.system(f"Getting entity get all tools")
        tools = []
        for entity_class in self.entity_classes:
            tools.append(entity_class.get_tool_get_all_entity(get_all_entity_func))
        logger.system(f"Entity get all tools returned")
        return tools

    def get_tools_add_or_update_relationship(self, add_relationship_func):
        """
        Gets a list of all add/update tools for all relationship classes.

        Args:
            add_relationship_func (function): The function to call to add/update a relationship.

        Returns:
            list: A list of tool functions.
        """
        logger.system(f"Getting relationship add/update tools")
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_tool_add_or_update_relationship(add_relationship_func))
        logger.system(f"Relationship add/update tools returned")
        return tools

    def get_tools_get_relationship_properties(self, get_relationship_properties_func):
        """
        Gets a list of all 'get properties' tools for all relationship classes.

        Args:
            get_relationship_properties_func (function): The function to call to get relationship properties.

        Returns:
            list: A list of tool functions.
        """
        logger.system(f"Getting relationship get relationship entities tools")
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_tool_get_relationship_properties(get_relationship_properties_func))
        logger.system(f"Relationship get relationship entities tools returned")
        return tools

    def get_tools_get_relationship_entities(self, get_relationship_entities_func):
        """
        Gets a list of all 'get related entities' tools for all relationship classes.

        Args:
            get_relationship_entities_func (function): The function to call to get related entities.

        Returns:
            list: A list of tool functions.
        """
        logger.system(f"Getting relationship get relationship entities tools")
        tools = []
        for relationship_class in self.relationship_classes:
            tools.append(relationship_class.get_tool_get_relationship_entities(get_relationship_entities_func))
        logger.system(f"Relationship get relationship entities tools returned")
        return tools

    def get_tools_add_or_update_entity_and_relationship(self, add_entity_func, add_relationship_func):
        """
        Gets a combined list of all add/update tools for both entities and relationships.

        Args:
            add_entity_func (function): The function to call to add/update an entity.
            add_relationship_func (function): The function to call to add/update a relationship.

        Returns:
            list: A list of all add/update tool functions.
        """
        logger.system(f"Getting add/update tools")
        tools = []
        tools.extend(self.get_tools_add_or_update_entity(add_entity_func))
        tools.extend(self.get_tools_add_or_update_relationship(add_relationship_func))
        logger.system(f"Add/update tools returned")
        return tools

    def get_tools_get_entity_and_relationship(self, get_all_entity_func, get_entity_properties_func, get_relationship_properties_func, get_relationship_entities_func):
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
        logger.system(f"Getting get tools")
        tools = []
        tools.extend(self.get_tools_get_all_entity(get_all_entity_func))
        tools.extend(self.get_tools_get_entity_properties(get_entity_properties_func))
        tools.extend(self.get_tools_get_relationship_properties(get_relationship_properties_func))
        tools.extend(self.get_tools_get_relationship_entities(get_relationship_entities_func))
        logger.system(f"Get tools returned")
        return tools

    def __str__(self):
        """Returns a string representation of the entire ontology."""
        logger.system(f"Getting string representation of ontology")
        ontology_str = ""
        ontology_str += f"Ontology Name: {self.name}\n"
        ontology_str += f"Ontology Description: {self.description}\n"
        ontology_str += "Entity Classes:\n"
        for entity_class in self.entity_classes:
            ontology_str += f"   {entity_class}\n"
        ontology_str += "Relationship Classes:\n"
        for relationship_class in self.relationship_classes:
            ontology_str += f"   {relationship_class}"
        return ontology_str
