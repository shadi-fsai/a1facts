from neo4j import GraphDatabase
from ontology.knowledge_ontology import KnowledgeOntology
from graph.query_agent import QueryAgent
from graph.update_agent import UpdateAgent
from graph.rewrite_agent import RewriteAgent
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = ("neo4j", os.getenv("NEO4J_AUTH"))

class KnowledgeGraph:
    """
    Manages interactions with a Neo4j graph database, including adding, updating,
    and querying entities and relationships based on a provided ontology.
    """

    def __init__(self, ontology: KnowledgeOntology):
        """
        Initializes the KnowledgeGraph, connects to the Neo4j database, and sets up
        the query and update agents with tools derived from the ontology.

        Args:
            ontology (KnowledgeOntology): The ontology defining the graph's structure.
        """
        self.ontology = ontology
        try:
            self.driver = GraphDatabase.driver(URI, auth=(AUTH[0], AUTH[1]))
            print("Successfully connected to Neo4j database.")
        except Exception as e:
            print(f"Failed to connect to Neo4j database: {e}")
            self.driver = None
        self.get_tools = self.ontology.get_get_tools(self.get_all_entities_by_label, self.get_entity_properties, self.get_relationship_properties, self.get_relationship_entities)
        self.add_or_update_tools = self.ontology.get_add_or_update_tools(self.add_or_update_entity, self.add_relationship)        
        self.query_agent = QueryAgent(self.ontology,self.get_tools ) 
        self.update_agent = UpdateAgent(self.ontology,self.add_or_update_tools)
        self.rewrite_agent = RewriteAgent(self.ontology,[])
        self.class_entity_pairs = {}

    def get_class_entity_pairs(self):
        for entity_class in self.ontology.entity_classes:
            self.class_entity_pairs[entity_class.entity_class_name] = []
            entities = self.get_all_entities_by_label(entity_class.entity_class_name)
            for entity in entities:
                self.class_entity_pairs[entity_class.entity_class_name].append(entity[entity_class.primary_key_prop.property_name])
            

    def rewrite_query(self, query: str):
        self.get_class_entity_pairs()
        return self.rewrite_agent.rewrite_query(query, self.class_entity_pairs)


    def query(self, query: str):
        """
        Executes a natural language query against the knowledge graph.

        Args:
            query (str): The natural language query to execute.

        Returns:
            str: The content of the agent's response.
        """
        query = self.rewrite_query(query)
        return self.query_agent.query(query)

    def update_knowledge(self, knowledge: str):
        """
        Updates the knowledge graph with new, unstructured information.

        Args:
            knowledge (str): A string of unstructured knowledge to add to the graph.

        Returns:
            str: The content of the agent's response.
        """
        rewrite_knowledge = self.rewrite_query(knowledge)
        result = self.update_agent.run("Translate the following knowledge into a structured format based on the ontology, then add every entity and relationship to the graph using the tools available to you.\n\n " + rewrite_knowledge)
        return result.content

    def close(self):
        """Closes the connection to the Neo4j database."""
        if self.driver is not None:
            self.driver.close()
            print("Neo4j connection closed.")

    def _execute_query(self, query, parameters=None):
        """
        Executes a Cypher query that writes data to the graph.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): Parameters for the query. Defaults to None.
        """
        if self.driver is None:
            print("Driver not initialized. Cannot execute query.")
            return

        with self.driver.session() as session:
            try:
                session.run(query, parameters)
            except Exception as e:
                print(f"Error executing query: {e}")

    def _execute_read_query(self, query, parameters=None):
        """
        Executes a Cypher query that reads data from the graph.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): Parameters for the query. Defaults to None.
        
        Returns:
            list: A list of records from the query result.
        """
        if self.driver is None:
            print("Driver not initialized. Cannot execute query.")
            return []

        with self.driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record for record in result]
            except Exception as e:
                print(f"Error executing read query: {e}")
                return []

    def add_or_update_entity(self, label, primary_key_field, properties):
        """
        Adds a new entity (node) to the graph or updates an existing one
        based on its primary key.

        Args:
            label (str): The label of the entity (e.g., 'Company').
            primary_key_field (str): The name of the primary key property.
            properties (dict): A dictionary of the entity's properties.
        """
        if primary_key_field not in properties:
            print(f"Error: Primary key '{primary_key_field}' not found in properties.")
            return

        sanitized_props = {}
        for key, value in properties.items():
            if isinstance(value, date):
                sanitized_props[key] = value.isoformat()
            else:
                sanitized_props[key] = value

        primary_value = sanitized_props[primary_key_field]

        # Cypher query to find a node by its label and primary key, or create it if it doesn't exist.
        # ON CREATE sets all properties when the node is first created.
        # ON MATCH updates all properties if the node already exists.
        query = (
            f"MERGE (n:{label} {{{primary_key_field}: $primary_value}}) "
            "ON CREATE SET n = $props "
            "ON MATCH SET n += $props"
        )

        parameters = {
            "primary_value": primary_value,
            "props": sanitized_props
        }

        self._execute_query(query, parameters)
        print(f"Successfully added/updated entity: {label} with {primary_key_field} = '{primary_value}'")

    def add_relationship(self, start_node_label, start_node_pk_val, end_node_label, end_node_pk_val, relationship_type, properties=None, symmetric=False):
        """
        Creates a relationship between two existing nodes in the graph.

        Args:
            start_node_label (str): The label of the starting node.
            start_node_pk_val (str): The primary key value of the starting node.
            end_node_label (str): The label of the ending node.
            end_node_pk_val (str): The primary key value of the ending node.
            relationship_type (str): The type of the relationship.
            properties (dict, optional): Properties for the relationship. Defaults to None.
            symmetric (bool): If True, creates a relationship in both directions.
        """
        print("\nDEBUG: add_relationship called with:")
        print(f"  start_node_label: {start_node_label}, start_node_pk_val: {start_node_pk_val}")
        print(f"  end_node_label: {end_node_label}, end_node_pk_val: {end_node_pk_val}")
        print(f"  relationship_type: {relationship_type}")
        """
        Creates a relationship between two existing nodes.

        Args:
            start_node_label (str): The label of the starting node.
            start_node_pk_val (str): The primary key value of the starting node.
            end_node_label (str): The label of the ending node.
            end_node_pk_val (str): The primary key value of the ending node.
            relationship_type (str): The type of the relationship (e.g., "OPERATES_IN").
            properties (dict, optional): Properties for the relationship. Defaults to None.
            symmetric (bool): If True, creates a two-way relationship. Defaults to False.
        Example:
            # Based on the company ontology, this could represent relationships like:
            # Organization -> Market: "OPERATES_IN"
            # Organization -> Organization: "COMPETES_WITH" 
            # Organization -> Person: "IS_LED_BY"
            # Person -> Role: "HAS_ROLE"
            # Role -> Organization: "HELD_AT"
            # Organization -> Product_Service: "PRODUCES"
            # Organization -> Corporate_Event: "IS_SUBJECT_OF"
            # Corporate_Event -> Financial_Metric: "REPORTS"
            # Organization -> Competitive_Advantage: "POSSESSES"
            # Organization -> Risk_Factor: "IS_EXPOSED_TO"
        """
        # Determine the primary key field based on the label, assuming 'name' as a default.
        # This could be made more robust if different labels use different primary keys.
        start_pk_field = "name" 
        end_pk_field = "name" 

        # Base query for a directional relationship
        query = (
            f"MATCH (a:{start_node_label} {{{start_pk_field}: $start_val}}), "
            f"(b:{end_node_label} {{{end_pk_field}: $end_val}}) "
            f"MERGE (a)-[r:{relationship_type}]->(b) "
        )
        if properties:
            query += "SET r += $props"

        # If the relationship is symmetric, create the reverse relationship as well
        if symmetric:
            reverse_query = (
                f"MATCH (a:{start_node_label} {{{start_pk_field}: $start_val}}), "
                f"(b:{end_node_label} {{{end_pk_field}: $end_val}}) "
                f"MERGE (b)-[r:{relationship_type}]->(a) "
            )
            if properties:
                reverse_query += "SET r += $props"
        
        parameters = {
            "start_val": start_node_pk_val,
            "end_val": end_node_pk_val,
            "props": properties or {}
        }

        try:
            self._execute_query(query, parameters)
            if symmetric:
                self._execute_query(reverse_query, parameters)
        except Exception as e:
            print(f"Error creating relationship: {e}")
            return False
        
        print(f"Successfully created relationship: ({start_node_pk_val})-[{relationship_type}]->({end_node_pk_val})")

    def _get_primary_key_field(self, label):
        """
        Determines the primary key field for a given entity label.

        Args:
            label (str): The label of the entity.

        Returns:
            str: The name of the primary key field.
        """
        if label == "Role":
            return "role_title"
        return "name"

    def find_entities_fuzzy(self, label, search_field, search_term):
        """
        Finds entities using a case-insensitive, partial string match.

        Args:
            label (str): The label of the node to search for.
            search_field (str): The property field to search within (e.g., "name").
            search_term (str): The term to search for.

        Returns:
            list: A list of nodes that match the search criteria.
        """
        query = (
            f"MATCH (n:{label}) "
            f"WHERE toLower(n.{search_field}) CONTAINS toLower($search_term) "
            "RETURN n"
        )
        parameters = {"search_term": search_term}
        
        results = self._execute_read_query(query, parameters)
        
        # Extract the node data from the result records
        if not results:
            return []
        nodes = [record["n"] for record in results]
        return nodes

    def get_entity_info(self, label, entity_identifier, exact_match=False):
        """
        Retrieves properties of an entity and the names of entities it's related to.

        Args:
            label (str): The label for the node (e.g., "Organization").
            entity_identifier (str): The name or title of the entity to query.
            exact_match (bool): If True, performs an exact match. Defaults to False (fuzzy).

        Returns:
            list: A list of dictionaries, each containing an entity's properties and relationships.
        """
        pk_field = self._get_primary_key_field(label)

        if exact_match:
            where_clause = f"n.{pk_field} = $identifier"
        else:
            where_clause = f"toLower(n.{pk_field}) CONTAINS toLower($identifier)"

        query = (
            f"MATCH (n:{label}) "
            f"WHERE {where_clause} "
            "OPTIONAL MATCH (n)-[r]-(related) "
            "RETURN properties(n) AS properties, "
            "collect({relationship: type(r), properties: properties(r), related_entity: coalesce(related.name, related.role_title)}) AS relationships"
        )
        parameters = {"identifier": entity_identifier}
        records = self._execute_read_query(query, parameters)

        if not records:
            print(f"No entity with label '{label}' and identifier '{entity_identifier}' found.")
            return []

        results = []
        for record in records:
            if record["properties"]:
                # Filter out potential empty relationship objects if no relationships exist
                relationships = [rel for rel in record["relationships"] if rel['relationship'] is not None]
                results.append({"properties": record["properties"], "relationships": relationships})
        
        return results

    def get_all_entities_by_label(self, label):
        """
        Retrieves all entities (nodes) with a specific label from the graph.

        Args:
            label (str): The label to search for (e.g., "Organization").

        Returns:
            list: A list of dictionaries, where each represents an entity's properties.
        """
        query = f"MATCH (n:{label}) RETURN properties(n) AS properties"
        records = self._execute_read_query(query)

        if not records:
            print(f"No entities found with label '{label}'.")
            return []
        
        return [record["properties"] for record in records]

    def get_relationship_entities(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_primary_key_prop):
        """
        Gets all range entities connected to a specific domain entity via a relationship.

        Args:
            domain_label (str): The label of the domain entity.
            domain_pk_prop (str): The primary key property of the domain entity.
            domain_primary_key_value (str): The primary key of the domain entity.
            relationship_type (str): The type of the relationship.
            range_label (str): The label of the range entities to retrieve.
            range_primary_key_prop (str): The primary key property of the range entity.

        Returns:
            list: A list of dictionaries, where each represents a range entity's properties.
        """
        # For a given domain, get all the range entities in a relationship
        query = f"MATCH (n:{domain_label} {{{domain_pk_prop}: $domain_primary_key_value}}) MATCH (n)-[r:{relationship_type}]->(m:{range_label}) RETURN properties(m) AS properties"
        parameters = {"domain_primary_key_value": domain_primary_key_value}
        records = self._execute_read_query(query, parameters)
        return [record["properties"] for record in records]
    
    def get_relationship_properties(self, domain_label, domain_pk_prop, domain_primary_key_value, relationship_type, range_label, range_pk_prop, range_primary_key_value):
        """
        Gets the properties of a specific relationship between two entities.

        Args:
            domain_label (str): The label of the domain entity.
            domain_pk_prop (str): The primary key property of the domain entity.
            domain_primary_key_value (str): The primary key of the domain entity.
            relationship_type (str): The type of the relationship.
            range_label (str): The label of the range entity.
            range_pk_prop (str): The primary key property of the range entity.
            range_primary_key_value (str): The primary key of the range entity.

        Returns:
            list: A list containing the properties of the relationship.
        """
        # For a given domain and range, get the properties of the relationship
        query = f"MATCH (n:{domain_label} {{{domain_pk_prop}: $domain_primary_key_value}}) MATCH (n)-[r:{relationship_type}]->(m:{range_label} {{{range_pk_prop}: $range_primary_key_value}}) RETURN properties(r) AS properties"
        parameters = {"domain_primary_key_value": domain_primary_key_value, "range_primary_key_value": range_primary_key_value}
        records = self._execute_read_query(query, parameters)
        return [record["properties"] for record in records]

    def get_entity_properties(self, label, pk_prop, primary_key_value):
        """
        Gets the properties of a single entity identified by its primary key.

        Args:
            label (str): The label of the entity.
            pk_prop (str): The primary key property of the entity.
            primary_key_value (str): The primary key value of the entity.

        Returns:
            list: A list containing the properties of the entity.
        """
        # For a given entity, get the properties
        query = f"MATCH (n:{label} {{{pk_prop}: $primary_key_value}}) RETURN properties(n) AS properties"
        parameters = {"primary_key_value": primary_key_value}
        records = self._execute_read_query(query, parameters)
        return [record["properties"] for record in records]

