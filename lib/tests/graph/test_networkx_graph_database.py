import pytest
import os
import pickle
import networkx as nx
from a1facts.graph.networkx_graph_database import NetworkxGraphDatabase

@pytest.fixture
def db_path(tmp_path):
    """Create a temporary path for the graph database file."""
    return tmp_path / "test_graph.pickle"

@pytest.fixture
def db(db_path):
    """Create a NetworkxGraphDatabase instance with a temporary file path."""
    database = NetworkxGraphDatabase(graph_file=str(db_path))
    yield database
    database.close()

def test_initialization_new(db, db_path):
    """Test initialization with a non-existent file."""
    assert os.path.exists(db_path) == False
    assert db.graph.number_of_nodes() == 0
    assert db.graph.number_of_edges() == 0

def test_initialization_from_existing_file(db_path):
    """Test initialization from an existing graph file."""
    # Create a dummy graph file
    graph = nx.DiGraph()
    node_id = ("Person", "node1")
    graph.add_node(node_id, label="Person", name="Alice")
    with open(db_path, "wb") as f:
        pickle.dump(graph, f)
    
    db = NetworkxGraphDatabase(graph_file=str(db_path))
    assert db.graph.number_of_nodes() == 1
    assert node_id in db.graph

def test_add_or_update_entity_add_new(db):
    """Test adding a new entity."""
    properties = {"id": "company1", "name": "TestCorp", "value": 100}
    db.add_or_update_entity("Company", "id", properties)
    
    node_id = ("Company", "company1")
    assert db.graph.has_node(node_id)
    node_data = db.graph.nodes[node_id]
    assert node_data["label"] == "Company"
    assert node_data["name"] == "TestCorp"

def test_add_or_update_entity_update_existing(db):
    """Test updating properties of an existing entity without changing the label."""
    properties1 = {"id": "p1", "name": "Person 1", "age": 30}
    db.add_or_update_entity("Person", "id", properties1)
    
    properties2 = {"id": "p1", "name": "Person One", "age": 31}
    db.add_or_update_entity("Person", "id", properties2)
    
    node_id = ("Person", "p1")
    node_data = db.graph.nodes[node_id]
    assert node_data["name"] == "Person One"
    assert node_data["age"] == 31
    assert db.graph.number_of_nodes() == 1

def test_add_or_update_entity_update_with_label_change(db):
    """
    Tests that calling add_or_update_entity with a new label for an
    existing primary key creates a new, distinct node, as the label is
    part of the unique identifier.
    """
    properties = {"id": "e1", "name": "Entity 1"}
    db.add_or_update_entity("TypeA", "id", properties)
    
    node_id_A = ("TypeA", "e1")
    assert db.graph.has_node(node_id_A)
    
    updated_properties = {"id": "e1", "name": "Entity One"}
    db.add_or_update_entity("TypeB", "id", updated_properties)
    
    node_id_B = ("TypeB", "e1")
    assert db.graph.has_node(node_id_B)
    
    # Verify that the original node still exists and a new one was created
    assert db.graph.number_of_nodes() == 2
    assert db.graph.nodes[node_id_A]['name'] == "Entity 1"
    assert db.graph.nodes[node_id_B]['name'] == "Entity One"

def test_add_or_update_entity_missing_pk(db):
    """Test adding an entity with a missing primary key field."""
    initial_node_count = db.graph.number_of_nodes()
    properties = {"name": "TestCorp"}
    db.add_or_update_entity("Company", "id", properties)
    assert db.graph.number_of_nodes() == initial_node_count

@pytest.fixture
def populated_db(db):
    """Pre-populate the database with some entities and relationships."""
    db.add_or_update_entity("Person", "id", {"id": "p1", "name": "Alice"})
    db.add_or_update_entity("Person", "id", {"id": "p2", "name": "Bob"})
    db.add_or_update_entity("Company", "id", {"id": "c1", "name": "AlphaInc"})
    db.add_or_update_entity("Company", "id", {"id": "c2", "name": "BetaCorp"})
    
    db.add_relationship("Person", "id", "p1", "Company", "id", "c1", "WORKS_FOR", {"role": "Engineer"})
    db.add_relationship("Person", "id", "p2", "Company", "id", "c1", "WORKS_FOR", {"role": "Manager"})
    db.add_relationship("Company", "id", "c1", "Company", "id", "c2", "PARTNERS_WITH", symmetric=True)
    return db

def test_add_relationship(populated_db):
    """Test adding directional and symmetric relationships."""
    person1_id = ("Person", "p1")
    company1_id = ("Company", "c1")
    company2_id = ("Company", "c2")
    
    assert populated_db.graph.has_edge(person1_id, company1_id)
    edge_data = populated_db.graph.get_edge_data(person1_id, company1_id)
    assert edge_data["type"] == "WORKS_FOR"
    assert edge_data["role"] == "Engineer"
    
    assert populated_db.graph.has_edge(company1_id, company2_id)
    assert populated_db.graph.has_edge(company2_id, company1_id)

def test_get_all_entities_by_label(populated_db):
    """Test retrieving all entities for a given label."""
    persons = populated_db.get_all_entities_by_label("Person")
    companies = populated_db.get_all_entities_by_label("Company")
    non_existent = populated_db.get_all_entities_by_label("Location")
    
    assert len(persons) == 2
    assert len(companies) == 2
    assert len(non_existent) == 0
    
    person_names = {p["name"] for p in persons}
    assert person_names == {"Alice", "Bob"}

def test_get_relationship_entities(populated_db):
    """Test getting entities connected by a specific relationship."""
    company = populated_db.get_relationship_entities("Person", "id", "p1", "WORKS_FOR", "Company", "id")
    assert len(company) == 1
    assert company[0]["name"] == "AlphaInc"

    # Test for non-existent relationship from the other direction
    no_one = populated_db.get_relationship_entities("Company", "id", "c1", "WORKS_FOR", "Person", "id")
    assert len(no_one) == 0

    # Test a symmetric relationship (Company <-> Company)
    partners_of_c1 = populated_db.get_relationship_entities("Company", "id", "c1", "PARTNERS_WITH", "Company", "id")
    assert len(partners_of_c1) == 1
    assert partners_of_c1[0]["name"] == "BetaCorp"

    partners_of_c2 = populated_db.get_relationship_entities("Company", "id", "c2", "PARTNERS_WITH", "Company", "id")
    assert len(partners_of_c2) == 1
    assert partners_of_c2[0]["name"] == "AlphaInc"

def test_get_relationship_properties(populated_db):
    """Test getting properties of a specific relationship."""
    props = populated_db.get_relationship_properties("Person", "id", "p1", "WORKS_FOR", "Company", "id", "c1")
    assert props["role"] == "Engineer"
    
    # Test for non-existent edge
    no_props = populated_db.get_relationship_properties("Person", "id", "p1", "WORKS_FOR", "Company", "id", "c2")
    assert no_props is None

def test_get_entity_properties(populated_db):
    """Test getting properties of a single entity."""
    props = populated_db.get_entity_properties("Person", "id", "p1")
    assert props["name"] == "Alice"
    
    no_props = populated_db.get_entity_properties("Person", "id", "p3")
    assert no_props is None

def test_save_and_close(populated_db, db_path):
    """Test saving the graph to a file and closing the database."""
    populated_db.save()
    assert os.path.exists(db_path)
    
    reloaded_db = NetworkxGraphDatabase(graph_file=str(db_path))
    assert reloaded_db.graph.number_of_nodes() == 4
    # A symmetric relationship in a DiGraph is represented by two distinct edges.
    assert reloaded_db.graph.number_of_edges() == 4
    
    persons = reloaded_db.get_all_entities_by_label("Person")
    assert len(persons) == 2
