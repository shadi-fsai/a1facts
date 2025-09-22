from __future__ import annotations
from a1facts.ontology.entity_class import EntityClass
from a1facts.ontology.property import Property
import typing
if typing.TYPE_CHECKING:
    from a1facts.ontology.knowledge_ontology import KnowledgeOntology


class RDFSEntity:
    """Represents an RDFS entity."""

    def __init__(self, entity_class: EntityClass, entity_name: str, properties: dict):
        """
        Initializes an RDFSEntity object.

        Args:
            entity_class (EntityClass): The entity class of the entity.
            entity_name (str): The name of the entity.
            properties (dict): A dictionary of properties for the entity.
        """
        self.entity_class = entity_class
        self.name = entity_name
        self.properties = properties

    def __str__(self):
        """Returns a string representation of the RDFS entity."""
        props_str = ", ".join(f"{k}: {v}" for k, v in self.properties.items())
        return f"RDFSEntity(name={self.name}, properties={{{props_str}}})"

    def print(self):
        """Prints the string representation of the RDFS entity."""
        print(str(self))

    @staticmethod
    def from_rdfs_block(subject, entity_class_name_str, rdfs_properties, ontology: "KnowledgeOntology", error_messages, block_index):
        entity_class_name = entity_class_name_str.strip(':')
        entity_class = ontology.find_entity_class(entity_class_name)

        if not entity_class:
            error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Entity class '{entity_class_name}' not found in ontology for entity '{subject}'.")
            return None
        
        if entity_class.validate_properties(rdfs_properties, subject, error_messages, block_index):
            properties_dict = {prop.key: prop.value for prop in rdfs_properties}
            properties_dict['type'] = entity_class_name
            return RDFSEntity(entity_class=entity_class, entity_name=subject, properties=properties_dict)
        
        return None
