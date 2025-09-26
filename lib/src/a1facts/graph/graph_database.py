from a1facts.ontology.rdfs_entity import RDFSEntity
from a1facts.ontology.rdfs_relationship import RDFSRelationship

class BaseGraphDatabase:
    """
    Base class for graph databases.
    """
    def __init__(self):
        pass

    def add_or_update_entity(self, entity: RDFSEntity):
        pass

    def add_relationship(self, relationship: RDFSRelationship):
        pass

    def get_all_entities_by_label(self, label):
        pass

    def get_entity_properties(self, label, pk_prop, primary_key_value):
        pass

    def get_relationship_entities(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_primary_key_prop):
        pass

    def save(self):
        pass

    def close(self):
        pass

