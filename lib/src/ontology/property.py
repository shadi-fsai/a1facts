class Property:
    """Represents a property of an entity or relationship in the ontology."""
    def __init__(self, name: str, prop_type: str, description: str, primary_key: bool = False):
        """
        Initializes a Property object.

        Args:
            name (str): The name of the property.
            prop_type (str): The data type of the property (e.g., 'string', 'float').
            description (str): A description of the property.
            primary_key (bool): True if this property is the primary key for its entity.
        """
        self.property_name = name
        self.type = prop_type
        self.description = description
        self.primary_key = primary_key

    def __str__(self):
        """Returns a string representation of the property."""
        pk_str = " - Primary Key" if self.primary_key else ""
        return f"{self.property_name} ({self.type}) - {self.description}{pk_str}"
