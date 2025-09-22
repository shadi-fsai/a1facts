from a1facts.utils.validation import check_type

class RDFSEntity:
    """Represents an RDFS entity."""

    def __init__(self, name: str, properties: dict):
        """
        Initializes an RDFSEntity object.

        Args:
            name (str): The name of the entity.
            properties (dict): A dictionary of properties for the entity.
        """
        self.name = name
        self.properties = properties

    def __str__(self):
        """Returns a string representation of the RDFS entity."""
        props_str = ", ".join(f"{k}: {v}" for k, v in self.properties.items())
        return f"RDFSEntity(name={self.name}, properties={{{props_str}}})"

    def print(self):
        """Prints the string representation of the RDFS entity."""
        print(str(self))

    @staticmethod
    def from_rdfs_block(subject, entity_class_name_str, properties, ontology, error_messages, block_index):
        entity_class_name = entity_class_name_str.strip(':')
        entity_class = ontology.find_entity_class(entity_class_name)

        if not entity_class:
            error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Entity class '{entity_class_name}' not found in ontology for entity '{subject}'.")
            return None
        
        if entity_class.validate_properties(properties, subject, error_messages, block_index):
            properties['type'] = entity_class_name
            return RDFSEntity(name=subject, properties=properties)
        
        return None
