import pytest
import yaml
from unittest.mock import patch, Mock
from a1facts.knowledge_base import KnowledgeBase

@pytest.fixture
def simple_ontology(tmp_path):
    """Creates a simple ontology with 3 classes and 2 relationships."""
    ontology_data = {
        'world': {
            'name': 'SimpleCorp',
            'description': 'A simple ontology for companies, employees, and projects.'
        },
        'entity_classes': {
            'Company': {
                'description': 'A business entity.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True}
                ]
            },
            'Employee': {
                'description': 'A person who works for a company.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'role', 'type': 'string'}
                ]
            },
            'Project': {
                'description': 'A project undertaken by a company.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True}
                ]
            }
        },
        'relationships': {
            'WORKS_FOR': {
                'description': 'An Employee works for a Company.',
                'domain': 'Employee',
                'range': 'Company',
                'properties': []
            },
            'WORKS_ON': {
                'description': 'An Employee works on a Project.',
                'domain': 'Employee',
                'range': 'Project',
                'properties': []
            }
        }
    }
    file_path = tmp_path / "simple_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.graph.query_rewrite_agent.Agent')
@patch('a1facts.graph.update_agent.Agent')
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
def test_repeated_acquisition_for_same_entity(
    MockAcquirerAgent, MockUpdateAgent, MockQueryRewriteAgent, 
    simple_ontology, tmp_path, db_backend, request
):
    """
    Tests that repeatedly acquiring knowledge about the same entity does not
    create duplicate entries in the knowledge graph.
    """
    # 1. Setup KnowledgeBase
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_uniqueness_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"EntityUniquenessTest_{db_backend}",
        ontology_config_file=simple_ontology,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # 2. Repeatedly acquire knowledge using ingest_knowledge
    num_acquisitions = 10
    for i in range(num_acquisitions):
        # Combine all knowledge into a single ingestion call
        combined_knowledge = f"""
            An employee named John Doe has the role of Engineer.
            There is a company named Company_{i}.
            There is a project named Project_{i}.
            John Doe works for Company_{i}.
        """
        
        combined_structured_knowledge = f"""
            @prefix simple: <http://a1facts.com/ontology/SimpleCorp#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

            simple:JohnDoe rdf:type simple:Employee ;
                simple:name "John Doe" ;
                simple:role "Engineer" .
            
            simple:Company_{i} rdf:type simple:Company ;
                simple:name "Company_{i}" .

            simple:Project_{i} rdf:type simple:Project ;
                simple:name "Project_{i}" .

            simple:JohnDoe simple:WORKS_FOR simple:Company_{i} .
        """
        
        with patch.object(kb.graph, '_rewrite_query', return_value=combined_structured_knowledge):
            kb.ingest_knowledge(combined_knowledge)

        # Manually perform the combined update since the agent is mocked
        kb.graph.graph_database.add_or_update_entity("Employee", "name", {"name": "John Doe", "role": "Engineer"})
        kb.graph.graph_database.add_or_update_entity("Company", "name", {"name": f"Company_{i}"})
        kb.graph.graph_database.add_or_update_entity("Project", "name", {"name": f"Project_{i}"})
        kb.graph.graph_database.add_relationship("Employee", "name", "John Doe", "Company", "name", f"Company_{i}", "WORKS_FOR", {})

    # 3. Verify entity uniqueness
    all_employees = kb.graph.graph_database.get_all_entities_by_label("Employee")
    john_does = [emp for emp in all_employees if emp['name'] == 'John Doe']
    assert len(john_does) == 1, "There should be only one 'John Doe' entity."

    # 4. Verify other entities and relationships
    all_companies = kb.graph.graph_database.get_all_entities_by_label("Company")
    assert len(all_companies) == num_acquisitions

    all_projects = kb.graph.graph_database.get_all_entities_by_label("Project")
    assert len(all_projects) == num_acquisitions
    
    # In NetworkX, relationships are edges. In Neo4j, they are first-class citizens.
    if use_neo4j:
        with kb.graph.graph_database.driver.session() as session:
            result = session.run("MATCH (e:Employee {name: 'John Doe'})-[r:WORKS_FOR]->(:Company) RETURN count(r) AS count")
            rel_count = result.single()['count']
            assert rel_count == num_acquisitions
    else:
        # For NetworkX, we can check the number of neighbors of John Doe that are Companies
        john_doe_node_id = None
        for node, data in kb.graph.graph_database.graph.nodes(data=True):
            if data.get('name') == 'John Doe' and data.get('label') == 'Employee':
                john_doe_node_id = node
                break
        
        company_neighbors = 0
        if john_doe_node_id:
            for neighbor in kb.graph.graph_database.graph.neighbors(john_doe_node_id):
                if kb.graph.graph_database.graph.nodes[neighbor].get('label') == 'Company':
                    company_neighbors += 1
        assert company_neighbors == num_acquisitions
