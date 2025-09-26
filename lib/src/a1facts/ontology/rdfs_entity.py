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
