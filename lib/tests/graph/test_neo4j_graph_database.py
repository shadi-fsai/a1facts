import pytest
from a1facts.graph.neo4j_graph_database import Neo4jGraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Prefix for test labels to avoid conflicts with existing data
TEST_LABEL_PREFIX = "Test"

def get_test_label(label):
    """Appends the test prefix to a label."""
    return f"{TEST_LABEL_PREFIX}{label}"

# Ensure that the Neo4j connection details are available as environment variables
# NEO4J_URI, NEO4J_USER, NEO4J_AUTH

@pytest.fixture(scope="module")
def db():
    """
    Fixture to set up a connection to the Neo4j database for the test module.
    It clears any previous test data before running the tests.
    """
    database = Neo4jGraphDatabase()
    # Clean up any leftover test data from previous runs
    database._execute_query(f"MATCH (n) WHERE any(l in labels(n) WHERE l STARTS WITH '{TEST_LABEL_PREFIX}') DETACH DELETE n")
    yield database
    # Teardown: clean up test data and close the connection
    database._execute_query(f"MATCH (n) WHERE any(l in labels(n) WHERE l STARTS WITH '{TEST_LABEL_PREFIX}') DETACH DELETE n")
    database.close()

@pytest.fixture(autouse=True)
def clean_db_between_tests(db):
    """
    Fixture to clean the database before each test function.
    """
    db._execute_query(f"MATCH (n) WHERE any(l in labels(n) WHERE l STARTS WITH '{TEST_LABEL_PREFIX}') DETACH DELETE n")

def test_initialization(db):
    """
    Test that the database driver is initialized.
    """
    assert db.driver is not None

def test_add_or_update_entity_add_new(db):
    """
    Test adding a new entity with a test label.
    """
    label = get_test_label("Company")
    properties = {"id": "company1", "name": "TestCorp", "value": 100}
    db.add_or_update_entity(label, "id", properties)
    
    result = db._execute_read_query(f"MATCH (n:{label} {{id: 'company1'}}) RETURN n")
    assert len(result) == 1
    node = result[0]['n']
    assert node['name'] == "TestCorp"
    assert node['value'] == 100

def test_add_or_update_entity_update_existing(db):
    """
    Test updating properties of an existing entity with a test label.
    """
    label = get_test_label("Person")
    properties1 = {"id": "p1", "name": "Person 1", "age": 30}
    db.add_or_update_entity(label, "id", properties1)
    
    properties2 = {"id": "p1", "name": "Person One", "age": 31}
    db.add_or_update_entity(label, "id", properties2)
    
    result = db._execute_read_query(f"MATCH (n:{label} {{id: 'p1'}}) RETURN n.name AS name, n.age AS age")
    assert len(result) == 1
    record = result[0]
    assert record['name'] == "Person One"
    assert record['age'] == 31

def test_add_or_update_entity_missing_pk(db):
    """
    Test adding an entity with a missing primary key field with a test label.
    """
    label = get_test_label("Company")
    properties = {"name": "TestCorp"}
    db.add_or_update_entity(label, "id", properties)

    result = db._execute_read_query(f"MATCH (n:{label} {{name: 'TestCorp'}}) RETURN n")
    assert len(result) == 0

@pytest.fixture
def populated_db(db):
    """
    Pre-populate the database with some entities and relationships for testing retrieval functions,
    using test-specific labels.
    """
    person_label = get_test_label("Person")
    company_label = get_test_label("Company")

    db.add_or_update_entity(person_label, "id", {"id": "p1", "name": "Alice"})
    db.add_or_update_entity(person_label, "id", {"id": "p2", "name": "Bob"})
    db.add_or_update_entity(company_label, "id", {"id": "c1", "name": "AlphaInc"})
    db.add_or_update_entity(company_label, "id", {"id": "c2", "name": "BetaCorp"})
    
    db.add_relationship(person_label, "id", "p1", company_label, "id", "c1", "WORKS_FOR", {"role": "Engineer"})
    db.add_relationship(person_label, "id", "p2", company_label, "id", "c1", "WORKS_FOR", {"role": "Manager"})
    db.add_relationship(company_label, "id", "c1", company_label, "id", "c2", "PARTNERS_WITH", symmetric=True)
    return db

def test_add_relationship(populated_db):
    """
    Test adding directional and symmetric relationships with test labels.
    """
    person_label = get_test_label("Person")
    company_label = get_test_label("Company")

    # Test directional relationship
    result = populated_db._execute_read_query(
        f"MATCH (:{person_label} {{id: 'p1'}})-[r:WORKS_FOR]->(:{company_label} {{id: 'c1'}}) RETURN r.role AS role"
    )
    assert len(result) == 1
    assert result[0]['role'] == "Engineer"

    # Test symmetric relationship
    result1 = populated_db._execute_read_query(
        f"MATCH (:{company_label} {{id: 'c1'}})-[:PARTNERS_WITH]->(:{company_label} {{id: 'c2'}}) RETURN count(*) AS count"
    )
    assert result1[0]['count'] == 1
    
    result2 = populated_db._execute_read_query(
        f"MATCH (:{company_label} {{id: 'c2'}})-[:PARTNERS_WITH]->(:{company_label} {{id: 'c1'}}) RETURN count(*) AS count"
    )
    assert result2[0]['count'] == 1

def test_get_all_entities_by_label(populated_db):
    """
    Test retrieving all entities for a given test label.
    """
    person_label = get_test_label("Person")
    company_label = get_test_label("Company")
    location_label = get_test_label("Location")

    persons = populated_db.get_all_entities_by_label(person_label)
    companies = populated_db.get_all_entities_by_label(company_label)
    non_existent = populated_db.get_all_entities_by_label(location_label)
    
    assert len(persons) == 2
    assert len(companies) == 2
    assert len(non_existent) == 0
    
    person_names = {p["name"] for p in persons}
    assert person_names == {"Alice", "Bob"}

def test_get_relationship_entities(populated_db):
    """
    Test getting entities connected by a specific relationship with test labels.
    """
    person_label = get_test_label("Person")
    company_label = get_test_label("Company")

    # Test a directional relationship (Person -> Company)
    company = populated_db.get_relationship_entities(person_label, "id", "p1", "WORKS_FOR", company_label, "id")
    assert len(company) == 1
    assert company[0]["name"] == "AlphaInc"

    # Test for non-existent relationship from the other direction
    no_one = populated_db.get_relationship_entities(company_label, "id", "c1", "WORKS_FOR", person_label, "id")
    assert len(no_one) == 0

    # Test a symmetric relationship (Company <-> Company)
    partners_of_c1 = populated_db.get_relationship_entities(company_label, "id", "c1", "PARTNERS_WITH", company_label, "id")
    assert len(partners_of_c1) == 1
    assert partners_of_c1[0]["name"] == "BetaCorp"

    partners_of_c2 = populated_db.get_relationship_entities(company_label, "id", "c2", "PARTNERS_WITH", company_label, "id")
    assert len(partners_of_c2) == 1
    assert partners_of_c2[0]["name"] == "AlphaInc"

def test_get_relationship_properties(populated_db):
    """
    Test getting properties of a specific relationship with test labels.
    """
    person_label = get_test_label("Person")
    company_label = get_test_label("Company")

    props_list = populated_db.get_relationship_properties(person_label, "id", "p1", "WORKS_FOR", company_label, "id", "c1")
    assert len(props_list) == 1
    assert props_list[0]["role"] == "Engineer"
    
    # Test for non-existent edge
    no_props = populated_db.get_relationship_properties(person_label, "id", "p1", "WORKS_FOR", company_label, "id", "c2")
    assert no_props == []

def test_get_entity_properties(populated_db):
    """
    Test getting properties of a single entity with a test label.
    """
    person_label = get_test_label("Person")

    props_list = populated_db.get_entity_properties(person_label, "id", "p1")
    assert len(props_list) == 1
    assert props_list[0]["name"] == "Alice"
    
    no_props = populated_db.get_entity_properties(person_label, "id", "p3")
    assert no_props == []
