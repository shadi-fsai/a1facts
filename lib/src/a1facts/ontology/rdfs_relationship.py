from a1facts.ontology.rdfs_entity import RDFSEntity
from a1facts.utils.validation import check_type


class RDFSRelationship:
    """Represents an RDFS relationship."""

    def __init__(self, domain: RDFSEntity, relationship: str, range: RDFSEntity, properties: dict = None):
        """
        Initializes an RDFSRelationship object.

        Args:
            domain (RDFSEntity): The domain of the relationship.
            relationship (str): The relationship itself.
            range (RDFSEntity): The range of the relationship.
            properties (dict, optional): A dictionary of properties for the relationship. Defaults to None.
        """
        self.domain = domain
        self.relationship = relationship
        self.range = range
        self.properties = properties if properties is not None else {}

    def __str__(self):
        """Returns a string representation of the RDFS relationship."""
        if self.properties:
            props_str = ", ".join(f"{k}: {v}" for k, v in self.properties.items())
            return f"RDFSRelationship(domain={self.domain.name}, relationship={self.relationship}, range={self.range.name}, properties={{{props_str}}})"
        return f"RDFSRelationship(domain={self.domain.name}, relationship={self.relationship}, range={self.range.name})"

    def print(self):
        """Prints the string representation of the RDFS relationship."""
        print(str(self))

    @staticmethod
    def from_rdfs_block(domain, relationship, range_str, properties, ontology, entities, error_messages, block_index):
        created_relationships = []
        is_valid = True
        ranges = [r.strip().strip(':') for r in range_str.split(',')]
        
        relationship_class = next((rc for rc in ontology.relationship_classes if rc.relationship_name == relationship), None)

        if not relationship_class:
            error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Relationship '{relationship}' not found in ontology.")
            is_valid = False
        else:
            is_valid = relationship_class.validate_properties(properties, domain, error_messages, block_index)
            for r in ranges:
                if not relationship_class.validate_domain_and_range(domain, r, entities, error_messages, block_index):
                    is_valid = False
        
        if is_valid:
            for r in ranges:
                domain_entity = entities.get(domain)
                range_entity = entities.get(r)
                if domain_entity and range_entity:
                    created_relationships.append(RDFSRelationship(domain=domain_entity, relationship=relationship, range=range_entity, properties=properties))
        
        return created_relationships
