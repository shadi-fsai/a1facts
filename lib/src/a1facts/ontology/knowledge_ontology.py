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
import re
from a1facts.ontology.rdfs_entity import RDFSEntity
from a1facts.ontology.rdfs_relationship import RDFSRelationship
from a1facts.ontology.rdfs_property import RDFSProperty
from rdflib import Graph, Literal, BNode, URIRef
from rdflib.namespace import RDF

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
        self.main_entities = []
        logger.system(f"Loading ontology from {ontology_file}")
        self.load_ontology()
        logger.system(f"Ontology loaded from {ontology_file}")
        self.rewrite_agent = OntologyRewriteAgent(self.ontology_file, [])
        logger.system(f"Ontology rewrite agent initialized")
        nonblocking_send_telemetry_ping()
        logger.user(f"Ontology loaded: {self.ontology_file}")
        logger.user(f"Ontology parsed: {str(self)}")
        
    def find_relationship_class(self, relationship_class_name):
        """
        Finds a relationship class by name.

        Args:
            relationship_class_name (str): The name of the relationship class to find.
        """
        logger.system(f"Finding relationship class: {relationship_class_name}")
        for relationship_class in self.relationship_classes:
            if relationship_class.relationship_name == relationship_class_name:
                return relationship_class
        logger.system(f"Relationship class not found: {relationship_class_name}")
        return None
        
    def find_entity_class(self, entity_class_name):
        """
        Finds an entity class by name.

        Args:
            entity_class_name (str): The name of the entity class to find.

        Returns:
            EntityClass or None: The found entity class, or None if not found.
        """
        logger.system(f"Finding entity class: {entity_class_name}")
        for entity_class in self.entity_classes:
            if entity_class.entity_class_name == entity_class_name:
                return entity_class
        logger.system(f"Entity class not found: {entity_class_name}")
        return None   
 


    def load_ontology(self):
        """Loads the ontology from the specified YAML file."""
        logger.system(f"Loading ontology from {self.ontology_file}")
        with open(self.ontology_file, 'r') as file:
            ontology = yaml.load(file, Loader=yaml.FullLoader)
            world_data = ontology.get('world', {})
            self.name = world_data.get('name', 'N/A')
            self.description = world_data.get('description', 'N/A')
            self.main_entities = world_data.get('main_entities')
            if self.main_entities is None:
                raise ValueError(f"'main_entities' is a required field in the 'world' section of the ontology file: {self.ontology_file}")

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

    def get_tools_get_entity_and_relationship(self, get_all_entity_func, get_entity_properties_func, get_relationship_entities_func):
        """
        Gets a combined list of all 'get' tools for both entities and relationships.

        Args:
            get_all_entity_func (function): Function to get all entities.
            get_entity_properties_func (function): Function to get entity properties.
            get_relationship_entities_func (function): Function to get related entities.

        Returns:
            list: A list of all 'get' tool functions.
        """
        logger.system(f"Getting get tools")
        tools = []
        tools.extend(self.get_tools_get_all_entity(get_all_entity_func))
        tools.extend(self.get_tools_get_entity_properties(get_entity_properties_func))
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

    def parse_rdfs_with_validation(self, rdfs_content: str):
        """
        Parses and validates an RDFS string against the ontology using rdflib.
        
        Args:
            rdfs_content: A string containing the RDFS data in Turtle format.
        
        Returns:
            A tuple containing two lists: (entities, relationships)
        """
        entities = {}
        relationships = []
        error_messages = []

        # Find the base URI from prefixes, if it exists
        base_uri_match = re.search(r'@prefix\s*:\s*<([^>]+)>', rdfs_content)
        base_uri = base_uri_match.group(1) if base_uri_match else None

        processed_rdfs = rdfs_content.strip()
        if processed_rdfs.startswith('{') and processed_rdfs.endswith('}'):
            processed_rdfs = processed_rdfs[1:-1].strip()

        # Ensure essential prefixes are present
        if '@prefix rdfs:' not in processed_rdfs:
            processed_rdfs = '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n' + processed_rdfs
        if '@prefix xsd:' not in processed_rdfs:
            processed_rdfs = '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n' + processed_rdfs
        if base_uri and '@prefix :' not in processed_rdfs:
            processed_rdfs = f'@prefix : <{base_uri}> .\n' + processed_rdfs

        g = Graph()
        
        try:
            g.parse(data=processed_rdfs, format='turtle')
        except Exception as e:
            error_messages.append(f"RDFS parsing error: {e}")
            logger.system("\n--- ❌ Validation Errors ---")
            for msg in error_messages:
                logger.system(msg)
            return [], []


        def get_alias(term, graph):
            if isinstance(term, URIRef):
                return graph.qname(term)
            return str(term)

        # 1. First pass: identify and create all entities with their properties
        for s, o in g.subject_objects(predicate=RDF.type):
            entity_name = get_alias(s, g)
            entity_class_name = get_alias(o, g)
            entity_class = self.find_entity_class(entity_class_name)
            if not entity_class:
                error_messages.append(f"VALIDATION ERROR: Entity class '{entity_class_name}' not found in ontology for entity '{entity_name}'.")
                continue

            rdfs_properties = []
            for p_prop, o_prop in g.predicate_objects(subject=s):
                if isinstance(o_prop, Literal):  # This is a property
                    prop_key = get_alias(p_prop, g)
                    prop_value = str(o_prop)
                    rdfs_properties.append(RDFSProperty(prop_key, prop_value))
            if entity_class.validate_properties(rdfs_properties, entity_name, error_messages, 0):
                properties_dict = {prop.key: prop.value for prop in rdfs_properties}
                properties_dict['type'] = entity_class_name
                entity = RDFSEntity(entity_class=entity_class, entity_name=entity_name, properties=properties_dict)
                entities[entity_name] = entity
        # 2. Second pass: identify and create relationships
        for s, p, o in g:
            # Skip entity declarations and properties of entities
            if p == RDF.type or isinstance(o, Literal):
                continue

            relationship_name = get_alias(p, g)
            relationship_class = self.find_relationship_class(relationship_name)

            if relationship_class:
                domain_name = get_alias(s, g)
                domain_entity = entities.get(domain_name)
                
                range_entity = None
                rdfs_properties = []

                # This is a direct relationship without properties
                range_name = get_alias(o, g)
                range_entity = entities.get(range_name)


                if not domain_entity:
                    if domain_name not in entities:
                        error_messages.append(f"VALIDATION ERROR: Domain entity '{domain_name}' for relationship '{relationship_name}' not defined or failed validation.")
                    continue
                
                if not range_entity:
                    error_messages.append(f"VALIDATION ERROR: Range for relationship '{relationship_name}' must be an entity. Found '{range_name}'.")
                    continue

                valid = True
                if not relationship_class.validate_domain_and_range(domain_name, range_name, entities, self, error_messages, 0):
                    valid = False
                
                if valid:
                    symmetric = relationship_class.symmetric
                    rel = RDFSRelationship(domain_entity=domain_entity, relationship=relationship_name, range_entity=range_entity, symmetric=symmetric)
                    relationships.append(rel)

        # 3. Log results
        success_messages = [f"Created entity: {entity}" for entity in entities.values()]
        for rel in relationships:
            success_messages.append(f"Created relationship: {rel}")

        logger.system("\n--- ✅ Successful Operations ---")
        for msg in success_messages:
            logger.system(msg)

        if error_messages:
            logger.system("\n--- ❌ Validation Errors ---")
            for msg in error_messages:
                logger.system(msg)
        logger.system("\n--- Parsing and Validation Complete ---")

        return list(entities.values()), relationships
