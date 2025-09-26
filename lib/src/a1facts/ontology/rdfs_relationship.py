from __future__ import annotations
from a1facts.ontology.rdfs_entity import RDFSEntity
import typing
if typing.TYPE_CHECKING:
    from a1facts.ontology.knowledge_ontology import KnowledgeOntology


class RDFSRelationship:
    """Represents an RDFS relationship."""

    def __init__(self, domain_entity: RDFSEntity, relationship: str, range_entity: RDFSEntity, symmetric: bool = False):
        """
        Initializes an RDFSRelationship object.

        Args:
            domain_entity (RDFSEntity): The domain of the relationship.
            relationship (str): The relationship itself.
            range_entity (RDFSEntity): The range of the relationship.
        """
        self.domain_entity = domain_entity
        self.relationship = relationship
        self.range_entity = range_entity
        self.symmetric = symmetric
        
    def __str__(self):
        """Returns a string representation of the RDFS relationship."""
        return f"RDFSRelationship(domain={self.domain_entity.name}, relationship={self.relationship}, range={self.range_entity.name})"

    def print(self):
        """Prints the string representation of the RDFS relationship."""
        print(str(self))
