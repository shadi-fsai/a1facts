from neo4j import GraphDatabase
from datetime import date
from dotenv import load_dotenv
import os
from knowledge_ontology import KnowledgeOntology
from modelconfig import my_model
from agno.tools import tool
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
# Load environment variables from .env file
load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = ("neo4j", os.getenv("NEO4J_AUTH"))

class KnowledgeGraph:
    """
    A class to interact with a Neo4j graph database.
    It provides methods to add/update entities (nodes) and relationships
    based on a predefined ontology.
    """

    def __init__(self, ontology: KnowledgeOntology):
        """
        Initializes the KnowledgeGraph class and connects to the database.

        Args:
            uri (str): The URI for the Neo4j database (e.g., "bolt://localhost:7687").
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.ontology = ontology
        try:
            self.driver = GraphDatabase.driver(URI, auth=(AUTH[0], AUTH[1]))
            print("Successfully connected to Neo4j database.")
        except Exception as e:
            print(f"Failed to connect to Neo4j database: {e}")
            self.driver = None
        self.model = my_model
        self.query_agent = Agent(
            name="Knowledge Graph Agent",
            role="Interact with the knowledge graph",
            model=self.model,
            tools=[self.get_entity_from_graph,
            self.get_all_entities_by_label],
            instructions=dedent(f"""
                Get information from the knowledge base.
                Use the get_entity_from_graph tool to get information from the graph.
                If you can't find the information in the graph, use the get_all_entities_by_label tool to get all entity identifiers by label.
                The ontology on which this knowledge base is based is [{self.ontology}]
                Today is {datetime.now().strftime("%Y-%m-%d")}
                """),
                show_tool_calls=True,
                markdown=True,
            )
        self.update_agent = Agent(
            name="Knowledge Graph Update Agent",
            role="Update the knowledge graph",
            model=self.model,
            tools=[self.add_entity_to_graph,
            self.add_relationship_to_graph],
            instructions=dedent(f"""
                The user is providing you unstrucutred knowledge. Translate the knowledge into a structured format based on the ontology.
                Ontology:[{self.ontology}]
                Return the results in RDFS format.
                When you are done, add every entity and relationship to the graph using the add_entity_to_graph and add_relationship_to_graph tools 
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            show_tool_calls=True,
            markdown=True,
            debug_mode=True,
            )

    def query(self, query: str):
        result = self.query_agent.run(query)
        return result.content        

    def update_knowledge(self, knowledge: str):
        result = self.update_agent.run(knowledge)
        return result.content

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
        start_pk_field = "name" 
        end_pk_field = "name" 

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

        try:
            self._execute_query(query, parameters)
        except Exception as e:
            print(f"Error creating relationship: {e}")
            return False
        
        print(f"Successfully created relationship: ({start_node_pk_val})-[{relationship_type}]->({end_node_pk_val})")

    def _get_primary_key_field(self, label):
        """Helper to determine the primary key field for a given label."""
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
        Searches by label and identifier. Default is fuzzy search on identifier.

        Args:
            label (str): The label for the node (e.g., "Organization").
            entity_identifier (str): The name or title of the entity to query.
            exact_match (bool): If True, performs an exact match. Defaults to False (fuzzy).

        Returns:
            list: A list of dictionaries, each containing an entity's properties and relationships.
                  Returns an empty list if no entity is found.
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
        Retrieves all entities (nodes) with a specific label.

        Args:
            label (str): The label to search for (e.g., "Organization").

        Returns:
            list: A list of dictionaries, where each dictionary represents the properties of an entity.
        """
        query = f"MATCH (n:{label}) RETURN properties(n) AS properties"
        records = self._execute_read_query(query)

        if not records:
            print(f"No entities found with label '{label}'.")
            return []
        
        return [record["properties"] for record in records]



    @tool(show_result=False, stop_after_tool_call=False)
    def add_entity_to_graph(self, entity: dict) -> str:
        """
        Add entity to the graph.
        entity is a dictionary of properties.
        Args:
            entity (dict): A dictionary containing entity information with the following structure:
                - label (str): The type/label of the entity (e.g., "Company", "Person", "Stock")
                - primary_key_field (str): The field name that serves as the unique identifier
                - properties (dict): Key-value pairs of entity properties and their values
        
        Returns:
            str: Success message indicating the entity was added to the graph

        Examples:
            # Example 1: Adding a Company entity
            entity_example1 = {
                "label": "Company",
                "primary_key_field": "name",
                "properties": {
                    "name": "Apple Inc.",
                    "ticker": "AAPL",
                    "sector": "Technology",
                    "market_cap": 3000000000000,
                    "founded": 1976,
                    "headquarters": "Cupertino, CA"
                }
            }
            
            # Example 2: Adding a Person entity
            entity_example2 = {
                "label": "Person",
                "primary_key_field": "full_name",
                "properties": {
                    "full_name": "Tim Cook",
                    "position": "CEO",
                    "age": 63,
                    "nationality": "American"
                }
            }
            
            # Example 3: Adding a Stock entity
            entity_example3 = {
                "label": "Stock",
                "primary_key_field": "ticker",
                "properties": {
                    "ticker": "AAPL",
                    "current_price": 185.50,
                    "currency": "USD",
                    "exchange": "NASDAQ"
                }
            }
        """
        # Save knowledge to file with timestamp
        self.add_or_update_entity(entity["label"], entity["primary_key_field"], entity["properties"])
        return "Entity added to graph"

    @tool(show_result=False, stop_after_tool_call=False)
    def add_relationship_to_graph(self, relationship: dict) -> str:
        """
        Add relationship to the graph.
        
        Args:
            relationship (dict): A dictionary containing relationship properties with the following structure:
                - start_node_label (str): Label of the starting node
                - start_node_pk_val: Primary key value of the starting node
                - end_node_label (str): Label of the ending node
                - end_node_pk_val: Primary key value of the ending node
                - relationship_type (str): Type/name of the relationship
                - properties (dict): Additional properties for the relationship
        
        Returns:
            str: Success message indicating the relationship was added to the graph
        """
        # Save knowledge to file with timestamp    
        self.add_relationship(relationship["start_node_label"], relationship["start_node_pk_val"], relationship["end_node_label"], relationship["end_node_pk_val"], relationship["relationship_type"], relationship["properties"])
        return "Entity added to graph"
        
    @tool(show_result=False, stop_after_tool_call=False)
    def get_entity_from_graph(self, entity_label: str, entity_pk_val: str) -> dict:
        """
        Get entity from the graph.
        Args:
            entity_label (str): The label of the entity to get
            entity_pk_val (str): The primary key value of the entity to get
        Returns:
            dict: A dictionary containing the entity's properties and its relationships

        Examples:
            # Example 1: Getting an Organization entity
            entity_example1 = {
                "entity_label": "Organization",
                "entity_pk_val": "Apple Inc."
            }
            # Example 2: Getting a Person entity  
            entity_example2 = {
                "entity_label": "Person",
                "entity_pk_val": "Tim Cook"
            }
        """
        import time
        start_time = time.time()
        entity_info = self.get_entity_info(entity_label, entity_pk_val)
        end_time = time.time()
        print(f"get_entity_info took {end_time - start_time:.4f} seconds")

        
        if entity_info:
            return entity_info
        else:
            return "No entity found with label '{entity_label}' and primary key value '{entity_pk_val}'"


    @tool(show_result=False, stop_after_tool_call=False)
    def get_all_entities_by_label(self, entity_label: str) -> list:
        """
        Get all entities by label from the graph.
        Args:
            entity_label (str): The label of the entities to get
        Returns:
            list: A list of entity identifiers (primary key values).

        Examples:
            # Example 1: Getting all Organizations
            entity_example1 = {
                "entity_label": "Organization"
            }
            # Example 2: Getting all People
            entity_example2 = {
                "entity_label": "Person"
            }
        """

        all_entities = self.get_all_entities_by_label(entity_label)
        if all_entities:
            return all_entities
        else:
            return "No entities found with label '{entity_label}'" 
