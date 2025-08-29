from neo4j import GraphDatabase
from datetime import date
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = ("neo4j", os.getenv("NEO4J_AUTH"))

class Neo4jGraph:
    """
    A class to interact with a Neo4j graph database.
    It provides methods to add/update entities (nodes) and relationships
    based on a predefined ontology.
    """

    def __init__(self):
        """
        Initializes the Neo4jGraph class and connects to the database.

        Args:
            uri (str): The URI for the Neo4j database (e.g., "bolt://localhost:7687").
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        try:
            self.driver = GraphDatabase.driver(URI, auth=(AUTH[0], AUTH[1]))
            print("Successfully connected to Neo4j database.")
        except Exception as e:
            print(f"Failed to connect to Neo4j database: {e}")
            self.driver = None

    def close(self):
        """Closes the database connection."""
        if self.driver is not None:
            self.driver.close()
            print("Neo4j connection closed.")

    def _execute_query(self, query, parameters=None):
        """
        A private helper method to execute a Cypher query.

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
        A private helper method to execute a Cypher query that returns data.

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
        Adds a new entity (node) or updates an existing one.
        It uses MERGE to prevent creating duplicate nodes based on the primary key.

        Args:
            label (str): The label for the node (e.g., "Organization").
            primary_key_field (str): The property name to use as a unique identifier (e.g., "name").
            properties (dict): A dictionary of properties for the node. Must include the primary_key_field.
        Example:
            # Based on the company ontology, this could represent entities like:
            # Organization: "name": "Apple Inc.", "ticker_symbol": "AAPL", "organization_type": "Public Company"
            # Market: "name": "Consumer Electronics", "projected_growth_rate_CAGR": 0.05
            # Person: "name": "Tim Cook"
            # Role: "role_title": "CEO", "start_date": date(2011, 8, 24)
            # Corporate_Event: "name": "Apple Q4 2023 Earnings", "event_type": "Earnings Report", "event_date": date(2023, 10, 26)
        """
        if primary_key_field not in properties:
            print(f"Error: Primary key '{primary_key_field}' not found in properties.")
            return

        # Sanitize properties to handle different data types like datetime.date
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

    def add_relationship(self, start_node_label, start_node_pk_val, end_node_label, end_node_pk_val, relationship_type, properties=None):
        """
        Creates a relationship between two existing nodes.

        Args:
            start_node_label (str): The label of the starting node.
            start_node_pk_val (str): The primary key value of the starting node.
            end_node_label (str): The label of the ending node.
            end_node_pk_val (str): The primary key value of the ending node.
            relationship_type (str): The type of the relationship (e.g., "OPERATES_IN").
            properties (dict, optional): Properties for the relationship. Defaults to None.
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
        start_pk_field = "name" if start_node_label in ["Organization", "Market", "Person"] else "role_title"
        end_pk_field = "name" if end_node_label in ["Organization", "Market", "Person"] else "role_title"


        query = (
            f"MATCH (a:{start_node_label} {{{start_pk_field}: $start_val}}), "
            f"(b:{end_node_label} {{{end_pk_field}: $end_val}}) "
            f"MERGE (a)-[r:{relationship_type}]->(b) "
        )

        if properties:
            query += "SET r += $props"

        parameters = {
            "start_val": start_node_pk_val,
            "end_val": end_node_pk_val,
            "props": properties or {}
        }

        self._execute_query(query, parameters)
        print(f"Successfully created relationship: ({start_node_pk_val})-[{relationship_type}]->({end_node_pk_val})")


    def get_entity_info(self, entity_identifier):
        """
        Retrieves properties of an entity and the names of entities it's related to.
        Searches for entities by 'name' or 'role_title'.

        Args:
            entity_identifier (str): The name or title of the entity to query.

        Returns:
            dict: A dictionary containing the entity's properties and its relationships,
                  or None if the entity is not found.
        """
        query = (
            "MATCH (n) "
            "WHERE n.name = $identifier OR n.role_title = $identifier "
            "OPTIONAL MATCH (n)-[r]-(related) "
            "RETURN properties(n) AS properties, "
            "collect({relationship: type(r), related_entity: coalesce(related.name, related.role_title)}) AS relationships"
        )
        parameters = {"identifier": entity_identifier}
        records = self._execute_read_query(query, parameters)

        if not records or not records[0]['properties']:
            print(f"Entity '{entity_identifier}' not found.")
            return None

        properties = records[0]["properties"]
        # Filter out potential empty relationship objects if no relationships exist
        relationships = [rel for rel in records[0]["relationships"] if rel['relationship'] is not None]

        return {"properties": properties, "relationships": relationships}


if __name__ == "__main__":
    # --- Configuration ---
    # IMPORTANT: Replace with your Neo4j database credentials.
    
    # Initialize the graph connection
    graph = Neo4jGraph()

    # --- Main Execution Logic ---
    if graph.driver:
        try:
            # 1. Add Organizations and a Market
            graph.add_or_update_entity("Organization", "name", {
                "name": "Apple Inc.",
                "ticker_symbol": "AAPL",
                "organization_type": "Public Company"
            })
            graph.add_or_update_entity("Organization", "name", {
                "name": "Samsung Electronics",
                "ticker_symbol": "005930.KS",
                "organization_type": "Public Company"
            })
            graph.add_or_update_entity("Market", "name", {
                "name": "Consumer Electronics",
                "projected_growth_rate_CAGR": 0.05
            })

            # 2. Add Relationships between Organizations and Market
            graph.add_relationship("Organization", "Apple Inc.", "Market", "Consumer Electronics", "OPERATES_IN")
            graph.add_relationship("Organization", "Samsung Electronics", "Market", "Consumer Electronics", "OPERATES_IN")
            graph.add_relationship("Organization", "Apple Inc.", "Organization", "Samsung Electronics", "COMPETES_WITH")

            # 3. Add a Person, a Role, and an Event
            graph.add_or_update_entity("Person", "name", {"name": "Tim Cook"})
            graph.add_or_update_entity("Role", "role_title", {
                "role_title": "CEO",
                "start_date": date(2011, 8, 24)
            })
            graph.add_or_update_entity("Corporate_Event", "name", {
                "name": "Apple Q4 2023 Earnings",
                "event_type": "Earnings Report",
                "event_date": date(2023, 10, 26)
            })

            # 4. Connect the Person, Role, and Organization
            graph.add_relationship("Organization", "Apple Inc.", "Person", "Tim Cook", "IS_LED_BY")
            graph.add_relationship("Person", "Tim Cook", "Role", "CEO", "HAS_ROLE")
            graph.add_relationship("Role", "CEO", "Organization", "Apple Inc.", "HELD_AT")

            # 5. Connect the Event to the Organization and Person
            graph.add_relationship("Organization", "Apple Inc.", "Corporate_Event", "Apple Q4 2023 Earnings", "IS_SUBJECT_OF")
            graph.add_relationship("Corporate_Event", "Apple Q4 2023 Earnings", "Person", "Tim Cook", "INVOLVES_PERSON")

            # 6. Query for entity information
            print("\n--- Querying for 'Apple Inc.' ---")
            apple_info = graph.get_entity_info("Apple Inc.")
            if apple_info:
                import json
                print("Properties:", json.dumps(apple_info["properties"], indent=2))
                print("Relationships:")
                for rel in apple_info["relationships"]:
                    print(f"  - [{rel['relationship']}]->({rel['related_entity']})")

            print("\n--- Querying for 'CEO' role ---")
            ceo_info = graph.get_entity_info("CEO")
            if ceo_info:
                import json
                print("Properties:", json.dumps(ceo_info["properties"], indent=2))
                print("Relationships:")
                for rel in ceo_info["relationships"]:
                    print(f"  - [{rel['relationship']}]->({rel['related_entity']})")

        finally:
            # Ensure the connection is closed
            graph.close()
