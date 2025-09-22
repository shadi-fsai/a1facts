from __future__ import annotations
from a1facts.ontology.entity_class import EntityClass
from a1facts.ontology.property import Property
from a1facts.utils.logger import logger
import typing
if typing.TYPE_CHECKING:
    from a1facts.ontology.knowledge_ontology import KnowledgeOntology


class RelationshipClass:
    """Represents a class of relationships (edges) in the ontology."""
    def __init__(self, name: str, domain: EntityClass, range: EntityClass, description: str, symmetric: bool = False):
        """
        Initializes a RelationshipClass object.

        Args:
            name (str): The name of the relationship class (e.g., 'operates_in').
            domain (EntityClass): The domain (start node) entity class.
            range (EntityClass): The range (end node) entity class.
            description (str): A description of the relationship class.
            symmetric (bool): True if the relationship is symmetric.
        """

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
        """
        Adds a property to the relationship class.

        Args:
            property (Property): The property to add.
        """
        self.properties.append(property)
    
    def __str__(self):
        """Returns a string representation of the relationship class."""
        relationship_str = ""
        relationship_str += f"{self.relationship_name} ({self.description}) - Domain: {self.domain_entity_class} - Range: {self.range_entity_class}\n"
        for prop in self.properties:
            relationship_str += f"   - {prop}\n"
        if self.symmetric:
            relationship_str += "   (This relationship is symmetric)\n"
        return relationship_str

    def is_symmetric(self):
        """Returns True if the relationship is symmetric."""
        return self.symmetric

    def validate_properties(self, rdfs_properties: list, domain_name: str, error_messages: list, block_index: int):
        from a1facts.ontology.rdfs_property import check_type
        is_valid = True
        
        properties_dict = {prop.key: prop.value for prop in rdfs_properties}

        if properties_dict:
            defined_props = {p.property_name: p for p in self.properties}
            for prop, value in properties_dict.items():
                if prop not in defined_props:
                    error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: In relationship '{domain_name}->{self.relationship_name}', property '{prop}' is not defined.")
                    is_valid = False
                elif not check_type(value, defined_props[prop].type):
                    error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: In relationship '{domain_name}->{self.relationship_name}', property '{prop}' has wrong type. Expected '{defined_props[prop].type}' but value was '{value}'.")
                    is_valid = False
        return is_valid

    def validate_domain_and_range(self, domain_name: str, range_name: str, entities: dict, ontology: "KnowledgeOntology", error_messages: list, block_index: int):
        from a1facts.ontology.rdfs_entity import RDFSEntity
        is_valid = True
        domain_entity = entities.get(domain_name)
        range_entity = entities.get(range_name)
        
        if not domain_entity:
            error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Domain entity '{domain_name}' was never defined with a type.")
            is_valid = False
        elif domain_entity.properties.get('type') != self.domain_entity_class:
            error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: For relationship '{self.relationship_name}', domain '{domain_name}' of type '{domain_entity.properties.get('type')}' does not match expected domain '{self.domain_entity_class}'.")
            is_valid = False
        
        if not range_entity:
            # Stub undefined range entities
            range_entity_class = ontology.find_entity_class(self.range_entity_class)
            if not range_entity_class:
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Range entity class '{self.range_entity_class}' for relationship '{self.relationship_name}' not found in ontology.")
                is_valid = False
        elif range_entity.properties.get('type') != self.range_entity_class:
             error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: For relationship '{self.relationship_name}', range '{range_name}' of type '{range_entity.properties.get('type')}' does not match expected range '{self.range_entity_class}'.")
             is_valid = False
        return is_valid

    def get_tool_add_or_update_relationship(self, add_or_update_relationship_func):
        """
        Creates a tool function for adding or updating a relationship of this class.

        Args:
            add_or_update_relationship_func (function): The function to call to add/update the relationship.

        Returns:
            function: A tool function that can be used by an agent.
        """
        def func(**kwargs):
            logger.system(f"Adding or updating relationship for {self.relationship_name}")
            properties = kwargs.get('kwargs', kwargs)
            
            domain_param_name, range_param_name = self._get_param_names()
            domain_primary_key_value = properties.get(domain_param_name)
            range_primary_key_value = properties.get(range_param_name)
            props = properties.get("properties")
            self.validate_properties([], domain_primary_key_value, [], 0) # This is a placeholder, will be fixed later
            logger.system(f"Arguments for add_or_update_relationship_func: {self.domain_entity_class}, {self.domain_primary_key_prop}, {domain_primary_key_value}, {self.range_entity_class}, {self.range_primary_key_prop}, {range_primary_key_value}, {self.relationship_name}, {props}, {self.symmetric}")
            return add_or_update_relationship_func(
                self.domain_entity_class,
                self.domain_primary_key_prop,
                domain_primary_key_value, 
                self.range_entity_class,  
                self.range_primary_key_prop,
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
        """
        Gets the parameter names for the domain and range of the relationship tool.
        Handles the case of self-referential relationships to avoid name collisions.

        Returns:
            tuple: A tuple containing the domain and range parameter names.
        """
        domain_param_name = f"from_{self.domain_entity_class}_{self.domain_primary_key_prop}"
        range_param_name = f"to_{self.range_entity_class}_{self.range_primary_key_prop}"
        return domain_param_name, range_param_name

    def get_tool_parameters_schema(self):
        """
        Builds the JSON schema for the parameters of the relationship tool.

        Returns:
            dict: A dictionary representing the JSON schema.
        """
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

    def get_tool_get_relationship_properties(self, get_relationship_properties_func):
        """
        Creates a tool for getting the properties of a specific relationship instance.

        Args:
            get_relationship_properties_func (function): The function to call to get relationship properties.

        Returns:
            function: A tool function that can be used by an agent.
        """
        def func(**kwargs):
            logger.system(f"Getting relationship properties for {self.relationship_name}")
            properties = kwargs.get('kwargs', kwargs)
            domain_param_name, range_param_name = self._get_param_names()
            domain_primary_key_value = properties.get(domain_param_name)
            range_primary_key_value = properties.get(range_param_name)
            logger.system(f"Arguments for get_relationship_properties_func: {self.domain_entity_class}, {self.domain_primary_key_prop}, {domain_primary_key_value}, {self.relationship_name}, {self.range_entity_class}, {self.range_primary_key_prop}, {range_primary_key_value}")
            return get_relationship_properties_func( self.domain_entity_class, self.domain_primary_key_prop, domain_primary_key_value, self.relationship_name,self.range_entity_class, self.range_primary_key_prop, range_primary_key_value)

        domain_param_name, range_param_name = self._get_param_names()


        func.__name__ = f"get_{self.relationship_name}_properties"
        func.__doc__ = f"Get a {self.relationship_name} relationship properties between _{self.domain_entity_class}_{self.range_entity_class}.\n"+\
            f"Domain Primary Key: from_{self.domain_entity_class}_{self.domain_primary_key_prop}\n"+\
            f"Range Primary Key: to_{self.range_entity_class}_{self.range_primary_key_prop}"+\
            (f"Returns properties of the relationship: {self.properties}" if self.properties else "")
        
            
        func.__parameters__ = {
            "type": "object",
            "properties": {
                domain_param_name: {"type": "string", "description": f"The {self.domain_primary_key_prop} of the FROM entity ({self.domain_entity_class})"}, 
                range_param_name: {"type": "string", "description": f"The {self.range_primary_key_prop} of the TO entity ({self.range_entity_class})"}
            },
            "required": [domain_param_name, range_param_name]
        }
        return func

    def get_tool_get_relationship_entities(self, get_relationship_entities_func):
        """
        Creates a tool for getting all entities connected by a specific relationship.

        Args:
            get_relationship_entities_func (function): The function to call to get the related entities.

        Returns:
            function: A tool function that can be used by an agent.
        """
        def func(**kwargs):
            logger.system(f"Getting relationship entities for {self.relationship_name}")
            properties = kwargs.get('kwargs', kwargs)
            domain_param_name, _ = self._get_param_names()
            domain_primary_key_value = properties.get(domain_param_name)
            logger.system(f"Arguments for get_relationship_entities_func: {self.domain_entity_class}, {self.domain_primary_key_prop}, {domain_primary_key_value}, {self.relationship_name}, {self.range_entity_class}, {self.range_primary_key_prop}")
            return get_relationship_entities_func( self.domain_entity_class, self.domain_primary_key_prop, domain_primary_key_value, self.relationship_name, self.range_entity_class, self.range_primary_key_prop)

        func.__name__ = f"get_{self.range_entity_class}s_{self.domain_entity_class}_{self.relationship_name}"
        func.__doc__ = f"Get all {self.range_entity_class}s linked to a {self.domain_entity_class} in a {self.relationship_name} relationship.\n"+\
            f"Domain Primary Key: from_{self.domain_entity_class}_{self.domain_primary_key_prop}\n"+\
                "Returns a list of {self.range_entity_class}s"
 
        domain_param_name, _ = self._get_param_names()

        func.__parameters__ = {
            "type": "object",
            "properties": {
                domain_param_name: {"type": "string", "description": f"The {self.domain_primary_key_prop} of the FROM entity ({self.domain_entity_class})"}
            },
            "required": [domain_param_name]
        }
        return func
