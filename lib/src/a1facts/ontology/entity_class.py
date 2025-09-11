from a1facts.ontology.property import Property
from a1facts.utils.logger import logger

class EntityClass:
    """Represents a class of entities (nodes) in the ontology."""
    def __init__(self, name: str, description: str):
        """
        Initializes an EntityClass object.

        Args:
            name (str): The name of the entity class (e.g., 'Company').
            description (str): A description of the entity class.
        """
        self.entity_class_name = name
        self.description = description
        self.properties = []
        self.primary_key_prop = None

    def add_property(self, property: "Property"):
        """
        Adds a property to the entity class.

        Args:
            property (Property): The property to add.
        """
        self.properties.append(property)
        if property.primary_key:
            self.primary_key_prop = property

    def __str__(self):
        """Returns a string representation of the entity class."""
        entity_str = ""
        entity_str += f"{self.entity_class_name} ({self.description})\n"
        entity_str += "      Properties:\n"
        for prop in self.properties:
            entity_str += f"      - {prop}\n"
        return entity_str

    def get_tool_add_or_update_entity(self, add_or_update_entity_func):
        """
        Creates a tool function for adding or updating an entity of this class.

        Args:
            add_or_update_entity_func (function): The function to call to add/update the entity in the graph.

        Returns:
            function: A tool function that can be used by an agent.
        """
        primary_key_prop = next((prop for prop in self.properties if prop.primary_key), self.properties[0] if self.properties else None)
        if not primary_key_prop:
            return None

        def func(**kwargs):
            logger.system(f"Adding or updating {self.entity_class_name} entity")
            properties = kwargs.get('kwargs', kwargs)
            logger.system(f"Arguments for add_or_update_entity_func: {self.entity_class_name}, {primary_key_prop.property_name}, {properties}")
            return add_or_update_entity_func(self.entity_class_name, primary_key_prop.property_name, properties)

        func.__name__ = "add_or_update_" + self.entity_class_name + "_information"
        func.__doc__ = f"Add or update a {self.entity_class_name} entity. Primary key: {primary_key_prop.property_name} \n" + (f"Properties: {self.properties}" if self.properties else "") + "\n"
        func.__parameters__ = self._get_tool_parameters_schema()
        return func

    def _get_tool_parameters_schema(self):
        """
        Builds the JSON schema for the parameters of the add/update tool.

        Returns:
            dict: A dictionary representing the JSON schema.
        """
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
    
    def get_tool_get_all_entity(self, get_all_entity_func):
        """
        Creates a tool function for getting all entities of this class.

        Args:
            get_all_entity_func (function): The function to call to get all entities from the graph.

        Returns:
            function: A tool function that can be used by an agent.
        """
        def func():
            logger.system(f"Getting all {self.entity_class_name} entities")
            return get_all_entity_func(self.entity_class_name)

        func.__name__ = "get_all_"+self.entity_class_name+"_entities"
        func.__doc__ = f"Get all {self.entity_class_name} entities."
        func.__parameters__ = {"type": "object", "properties": {}}
        return func

    def get_tool_get_entity_properties(self, get_entity_properties_func):
        """
        Creates a tool function for getting the properties of a specific entity.

        Args:
            get_entity_properties_func (function): The function to call to get entity properties.

        Returns:
            function: A tool function that can be used by an agent.
        """
        def func(**kwargs):
            logger.system(f"Getting {self.entity_class_name} properties")
            properties = kwargs.get('kwargs', kwargs)
            param_name = f"{self.entity_class_name}_{self.primary_key_prop.property_name}"
            primary_key_value = properties.get(param_name)
            logger.system(f"Arguments for get_entity_properties_func: {self.entity_class_name}, {self.primary_key_prop.property_name}, {primary_key_value}")
            return get_entity_properties_func(self.entity_class_name, self.primary_key_prop.property_name, primary_key_value)

        func.__name__ = "get_"+self.entity_class_name+"_properties"
        func.__doc__ = f"Get a {self.entity_class_name} properties. \n" + (f"Returns properties: {self.properties}" if self.properties else "") + "\n"
        
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
