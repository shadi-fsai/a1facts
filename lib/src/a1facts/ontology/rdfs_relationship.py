from __future__ import annotations
from a1facts.ontology.rdfs_entity import RDFSEntity
import typing
if typing.TYPE_CHECKING:
    from a1facts.ontology.knowledge_ontology import KnowledgeOntology


class RDFSRelationship:
    """Represents an RDFS relationship."""

    def __init__(self, domain_entity: RDFSEntity, relationship: str, range_entity: RDFSEntity, properties: dict = None, symmetric: bool = False):
        """
        Initializes an RDFSRelationship object.

        Args:
            domain_entity (RDFSEntity): The domain of the relationship.
            relationship (str): The relationship itself.
            range_entity (RDFSEntity): The range of the relationship.
            properties (dict, optional): A dictionary of properties for the relationship. Defaults to None.
        """
        self.domain_entity = domain_entity
        self.relationship = relationship
        self.range_entity = range_entity
        self.properties = properties if properties is not None else {}
        self.symmetric = symmetric
        
    def __str__(self):
        """Returns a string representation of the RDFS relationship."""
        if self.properties:
            props_str = ", ".join(f"{k}: {v}" for k, v in self.properties.items())
            return f"RDFSRelationship(domain={self.domain_entity.name}, relationship={self.relationship}, range={self.range_entity.name}, properties={{{props_str}}})"
        return f"RDFSRelationship(domain={self.domain_entity.name}, relationship={self.relationship}, range={self.range_entity.name})"

    def print(self):
        """Prints the string representation of the RDFS relationship."""
        print(str(self))

    @staticmethod
    def from_rdfs_block(domain, relationship, range_str, rdfs_properties, ontology: "KnowledgeOntology", entities, error_messages, block_index):
        created_relationships = []
        is_valid = True
        
        raw_ranges = [r.strip() for r in range_str.split(',')]
        ranges = []
        for r in raw_ranges:
            if r.startswith('_:'):
                ranges.append(r[2:])
            elif r.startswith(':'):
                ranges.append(r[1:])
            else:
                ranges.append(r)
        
        relationship_class = ontology.find_relationship_class(relationship)

        if not relationship_class:
            error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Relationship '{relationship}' not found in ontology.")
            is_valid = False
        else:
            is_valid = relationship_class.validate_properties(rdfs_properties, domain, error_messages, block_index)
            for r in ranges:
                if not relationship_class.validate_domain_and_range(domain, r, entities, ontology, error_messages, block_index):
                    is_valid = False
        
        if is_valid:
            for r in ranges:
                domain_entity = entities.get(domain)
                range_entity = entities.get(r)
                if domain_entity and range_entity:
                    # get the relationship class from the ontology by relationship name, and find out if it is symmetric
                    relationship_class = ontology.find_relationship_class(relationship)
                    symmetric = relationship_class.symmetric
                    properties_dict = {prop.key: prop.value for prop in rdfs_properties}
                    created_relationships.append(RDFSRelationship(domain_entity=domain_entity, relationship=relationship, range_entity=range_entity, properties=properties_dict, symmetric=symmetric))
        
        return created_relationships
