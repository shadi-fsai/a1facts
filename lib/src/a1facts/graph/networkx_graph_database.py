from a1facts.graph.graph_database import BaseGraphDatabase
import networkx as nx
import pickle
from colored import cprint
from a1facts.utils.logger import logger
from io import open


class NetworkxGraphDatabase(BaseGraphDatabase):
    def __init__(self, graph_file="networkx_graph.pickle"):
        self.graph = nx.DiGraph()
        self.graph_file = graph_file
        try:
            with open(self.graph_file, "rb") as f:
                self.graph = pickle.load(f)
        except FileNotFoundError:
            pass
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        cprint(f"Successfully initialized Networkx database with {num_nodes} nodes, {num_edges} relationships.", "green")
        self.nodes_by_label = self._build_label_index()

    def _build_label_index(self):
        index = {}
        for node, data in self.graph.nodes(data=True):
            label = data.get('label')
            if label:
                if label not in index:
                    index[label] = set()
                index[label].add(node)
        return index

    def add_or_update_entity(self, label, primary_key_field, properties):
        logger.system(f"NWX: Adding or updating {label} entity with primary key {primary_key_field} and properties {properties}")
        if primary_key_field not in properties:
            logger.system(f"NWX: Primary key '{primary_key_field}' not found in properties.")
            return

        primary_key_value = properties[primary_key_field]
        
        # Index maintenance: remove from old label set if label changes
        if self.graph.has_node(primary_key_value):
            old_label = self.graph.nodes[primary_key_value].get('label')
            if old_label and old_label != label:
                if old_label in self.nodes_by_label:
                    self.nodes_by_label[old_label].discard(primary_key_value)
        
        node_properties = properties.copy()
        node_properties['label'] = label

        if self.graph.has_node(primary_key_value):
            self.graph.nodes[primary_key_value].update(node_properties)
        else:
            self.graph.add_node(primary_key_value, **node_properties)
            
        # Add to new label set in index
        if label not in self.nodes_by_label:
            self.nodes_by_label[label] = set()
        self.nodes_by_label[label].add(primary_key_value)


    def add_relationship(self, start_node_label, start_pk_field, start_node_pk_val, end_node_label, end_pk_field, end_node_pk_val, relationship_type, properties=None, symmetric=False):
        logger.system(f"NWX: Adding {relationship_type} relationship between {start_node_label} {start_node_pk_val} and {end_node_label} {end_node_pk_val}")
        edge_properties = properties.copy() if properties else {}
        edge_properties['type'] = relationship_type

        self.graph.add_edge(start_node_pk_val, end_node_pk_val, **edge_properties)
        if symmetric:
            self.graph.add_edge(end_node_pk_val, start_node_pk_val, **edge_properties)

    def get_all_entities_by_label(self, label):
        logger.system(f"NWX: Getting all {label} entities")
        if label in self.nodes_by_label:
            node_keys = self.nodes_by_label[label]
            return [self.graph.nodes[key] for key in node_keys]
        else:
            logger.system(f"NWX: No label found for {label}")
            return []

    def get_relationship_entities(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_primary_key_prop):
        logger.system(f"NWX: Getting {relationship_type} relationship entities for {domain_label} {domain_primary_key_value} and {range_label}")
        results = []
        if not self.graph.has_node(domain_primary_key_value):
            logger.system(f"NWX: No domain node found for {domain_label} {domain_primary_key_value}")
            return results

        if self.graph.nodes[domain_primary_key_value].get('label') != domain_label:
            logger.system(f"NWX: Domain node found for {domain_label} {domain_primary_key_value} but it is not the correct label")
            return results

        for neighbor in self.graph.successors(domain_primary_key_value):
            edge_data = self.graph.get_edge_data(domain_primary_key_value, neighbor)
            if (edge_data and edge_data.get('type') == relationship_type and
                    self.graph.nodes[neighbor].get('label') == range_label):
                results.append(self.graph.nodes[neighbor])
        return results

    def get_relationship_properties(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_pk_prop, range_primary_key_value):
        logger.system(f"NWX: Getting {relationship_type} relationship properties for {domain_label} {domain_primary_key_value} and {range_label} {range_primary_key_value}")
        if self.graph.has_edge(domain_primary_key_value, range_primary_key_value):
            return self.graph.get_edge_data(domain_primary_key_value, range_primary_key_value)
        else:
            logger.system(f"NWX: No relationship found for {domain_label} {domain_primary_key_value} and {range_label} {range_primary_key_value}")
            return None

    def get_entity_properties(self, label, pk_prop, primary_key_value):
        logger.system(f"NWX: Getting {label} properties for {primary_key_value}")
        if self.graph.has_node(primary_key_value):
            return self.graph.nodes[primary_key_value]
        else:
            logger.system(f"NWX: No node found for {label} {primary_key_value}")
            return None

    def print_graph(self):
        logger.system(f"NWX: Printing graph")
        print("All nodes in the graph:")
        for node, data in self.graph.nodes(data=True):
            print(f"  Node: {node}, Data: {data}")
        
        print("\nAll relationships in the graph:")
        for start, end, data in self.graph.edges(data=True):
            print(f"  Edge: {start} -> {end}, Data: {data}")

    def close(self):
        logger.system(f"NWX: Closing graph")
        self.graph = nx.DiGraph()
        self.nodes_by_label = {}
        #self.print_graph()

    def save(self):
        try:
            logger.system(f"NWX: Saving graph to {self.graph_file}")
            with open(self.graph_file, "wb") as f:
                pickle.dump(self.graph, f)
        except Exception as e:
            logger.system(f"Error saving graph to {self.graph_file}: {e}")
            print(f"Error saving graph to {self.graph_file}: {e}")