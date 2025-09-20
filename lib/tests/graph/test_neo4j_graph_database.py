import pytest
from neo4j import GraphDatabase
from a1facts.graph.neo4j_graph_database import Neo4jGraphDatabase
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def neo4j_db(neo4j_service):
    """
    Fixture to set up a connection to the Dockerized Neo4j database
    and clear it after each test.
    """
    uri = neo4j_service["uri"]
    user = neo4j_service["user"]
    password = neo4j_service["password"]
    
    db = Neo4jGraphDatabase(uri=uri, user=user, password=password)
    
    # Ensure the database is clean before the test
    with db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        
    yield db  # Provide the database object to the test
    
    # Teardown: Clean the database after the test
    with db.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    db.close()

def test_add_entity(neo4j_db):
    """
    Tests adding a new entity to the graph.
    """
    properties = {"name": "Alice", "age": 30}
    neo4j_db.add_or_update_entity("Person", "name", properties)
    
    with neo4j_db.driver.session() as session:
        result = session.run("MATCH (p:Person {name: 'Alice'}) RETURN p.name AS name, p.age AS age")
        record = result.single()
        assert record is not None
        assert record["name"] == "Alice"
        assert record["age"] == 30

def test_update_entity(neo4j_db):
    """
    Tests updating an existing entity's properties.
    """
    # First, add an entity
    initial_properties = {"name": "Bob", "age": 40}
    neo4j_db.add_or_update_entity("Person", "name", initial_properties)
    
    # Now, update it
    updated_properties = {"name": "Bob", "age": 41, "city": "New York"}
    neo4j_db.add_or_update_entity("Person", "name", updated_properties)
    
    with neo4j_db.driver.session() as session:
        result = session.run("MATCH (p:Person {name: 'Bob'}) RETURN p.name AS name, p.age AS age, p.city AS city")
        record = result.single()
        assert record is not None
        assert record["age"] == 41
        assert record["city"] == "New York"

def test_add_relationship(neo4j_db):
    """
    Tests adding a relationship between two entities.
    """
    # Add two entities
    neo4j_db.add_or_update_entity("Person", "name", {"name": "Charlie"})
    neo4j_db.add_or_update_entity("City", "name", {"name": "Paris"})
    
    # Add a relationship between them
    neo4j_db.add_relationship("Person", "name", "Charlie", "City", "name", "Paris", "LIVES_IN", {"since": 2020})
    
    with neo4j_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Person {name: 'Charlie'})-[r:LIVES_IN]->(c:City {name: 'Paris'})
            RETURN r.since AS since
        """)
        record = result.single()
        assert record is not None
        assert record["since"] == 2020

def test_get_entity_properties(neo4j_db):
    """
    Tests retrieving properties of a specific entity.
    """
    properties = {"name": "David", "occupation": "Engineer"}
    neo4j_db.add_or_update_entity("Person", "name", properties)
    
    retrieved_props = neo4j_db.get_entity_properties("Person", "name", "David")
    assert retrieved_props is not None
    # The method returns the properties dict directly.
    assert retrieved_props['name'] == "David"
    assert retrieved_props['occupation'] == "Engineer"

def test_get_all_entities_by_label(neo4j_db):
    """
    Tests retrieving all entities with a specific label.
    """
    neo4j_db.add_or_update_entity("Person", "name", {"name": "Eve"})
    neo4j_db.add_or_update_entity("Person", "name", {"name": "Frank"})
    
    all_persons = neo4j_db.get_all_entities_by_label("Person")
    assert len(all_persons) == 2
    # The method returns a list of property dicts, so we access 'name' directly.
    names = {p['name'] for p in all_persons}
    assert names == {"Eve", "Frank"}

def test_get_relationship_properties(neo4j_db):
    """
    Tests retrieving properties of a specific relationship.
    """
    neo4j_db.add_or_update_entity("Person", "name", {"name": "Grace"})
    neo4j_db.add_or_update_entity("Company", "name", {"name": "InnovateCorp"})
    neo4j_db.add_relationship("Person", "name", "Grace", "Company", "name", "InnovateCorp", "WORKS_AT", {"role": "Developer"})
    
    # Corrected the order of arguments to match the method signature.
    rel_props = neo4j_db.get_relationship_properties("Person", "name", "Grace", "WORKS_AT", "Company", "name", "InnovateCorp")
    assert rel_props is not None
    assert len(rel_props) == 1
    # Corrected the assertion to match the actual return format (a list of property dicts).
    assert rel_props[0]['role'] == "Developer"

def test_get_relationship_entities(neo4j_db):
    """
    Tests retrieving entities connected by a specific relationship.
    """
    neo4j_db.add_or_update_entity("Person", "name", {"name": "Heidi"})
    neo4j_db.add_or_update_entity("Project", "name", {"name": "Alpha"})
    neo4j_db.add_or_update_entity("Project", "name", {"name": "Beta"})
    neo4j_db.add_relationship("Person", "name", "Heidi", "Project", "name", "Alpha", "MANAGES", {})
    neo4j_db.add_relationship("Person", "name", "Heidi", "Project", "name", "Beta", "MANAGES", {})
    
    related_projects = neo4j_db.get_relationship_entities("Person", "name", "Heidi", "MANAGES", "Project")
    assert len(related_projects) == 2
    # The method returns a list of property dicts, so we access the 'name' key directly.
    project_names = {p['name'] for p in related_projects}
    assert project_names == {"Alpha", "Beta"}

def test_entity_not_found(neo4j_db):
    """
    Tests that getting properties of a non-existent entity returns None.
    """
    retrieved_props = neo4j_db.get_entity_properties("Person", "name", "Zoe")
    assert retrieved_props is None

def test_relationship_not_found(neo4j_db):
    """
    Tests that getting properties of a non-existent relationship returns an empty list.
    """
    neo4j_db.add_or_update_entity("Person", "name", {"name": "Ivan"})
    neo4j_db.add_or_update_entity("City", "name", {"name": "Tokyo"})
    
    rel_props = neo4j_db.get_relationship_properties("Person", "name", "Ivan", "City", "name", "Tokyo", "LIVES_IN")
    assert rel_props == []
