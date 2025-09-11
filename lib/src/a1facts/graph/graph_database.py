class BaseGraphDatabase:
    """
    Base class for graph databases.
    """
    def __init__(self):
        pass

    def add_or_update_entity(self, label, primary_key_field, properties):
        pass

    def add_relationship(self, start_node_label, start_pk_field, start_node_pk_val, end_node_label, end_pk_field, end_node_pk_val, relationship_type, properties=None, symmetric=False):
        pass

    def get_all_entities_by_label(self, label):
        pass

    def get_entity_properties(self, label, pk_prop, primary_key_value):
        pass

    def get_relationship_entities(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_primary_key_prop):
        pass

    def get_relationship_properties(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_pk_prop, range_primary_key_value):
        pass

    def save(self):
        pass

    def close(self):
        pass

