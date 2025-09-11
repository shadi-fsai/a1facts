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
    assert db.nodes_by_label == {}

def test_initialization_from_existing_file(db_path):
    """Test initialization from an existing graph file."""
    # Create a dummy graph file
    graph = nx.DiGraph()
    graph.add_node("node1", label="Person", name="Alice")
    with open(db_path, "wb") as f:
        pickle.dump(graph, f)
    
    db = NetworkxGraphDatabase(graph_file=str(db_path))
    assert db.graph.number_of_nodes() == 1
    assert "node1" in db.graph
    assert db.nodes_by_label == {"Person": {"node1"}}

def test_add_or_update_entity_add_new(db):
    """Test adding a new entity."""
    properties = {"id": "company1", "name": "TestCorp", "value": 100}
    db.add_or_update_entity("Company", "id", properties)
    
    assert db.graph.has_node("company1")
    node_data = db.graph.nodes["company1"]
    assert node_data["label"] == "Company"
    assert node_data["name"] == "TestCorp"
    assert "company1" in db.nodes_by_label["Company"]

def test_add_or_update_entity_update_existing(db):
    """Test updating properties of an existing entity without changing the label."""
    properties1 = {"id": "p1", "name": "Person 1", "age": 30}
    db.add_or_update_entity("Person", "id", properties1)
    
    properties2 = {"id": "p1", "name": "Person One", "age": 31}
    db.add_or_update_entity("Person", "id", properties2)
    
    node_data = db.graph.nodes["p1"]
    assert node_data["name"] == "Person One"
    assert node_data["age"] == 31
    assert "p1" in db.nodes_by_label["Person"]
    assert len(db.nodes_by_label["Person"]) == 1

def test_add_or_update_entity_update_with_label_change(db):
    """Test updating an entity and changing its label."""
    properties = {"id": "e1", "name": "Entity 1"}
    db.add_or_update_entity("TypeA", "id", properties)
    
    assert "e1" in db.nodes_by_label["TypeA"]
    
    updated_properties = {"id": "e1", "name": "Entity One"}
    db.add_or_update_entity("TypeB", "id", updated_properties)
    
    assert "TypeA" not in db.nodes_by_label or "e1" not in db.nodes_by_label["TypeA"]
    assert "e1" in db.nodes_by_label["TypeB"]
    assert db.graph.nodes["e1"]["label"] == "TypeB"
    assert db.graph.nodes["e1"]["name"] == "Entity One"

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
    assert populated_db.graph.has_edge("p1", "c1")
    edge_data = populated_db.graph.get_edge_data("p1", "c1")
    assert edge_data["type"] == "WORKS_FOR"
    assert edge_data["role"] == "Engineer"
    
    assert populated_db.graph.has_edge("c1", "c2")
    assert populated_db.graph.has_edge("c2", "c1")

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
    # Test a directional relationship (Person -> Company)
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
    # Save the populated graph
    populated_db.save()
    assert os.path.exists(db_path)
    
    # Close the database
    populated_db.close()
    assert populated_db.graph.number_of_nodes() == 0
    assert populated_db.nodes_by_label == {}
    
    # Re-initialize from the saved file to check persistence
    reloaded_db = NetworkxGraphDatabase(graph_file=str(db_path))
    assert reloaded_db.graph.number_of_nodes() == 4
    assert reloaded_db.graph.number_of_edges() == 4
    
    persons = reloaded_db.get_all_entities_by_label("Person")
    assert len(persons) == 2
