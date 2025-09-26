import pytest
import yaml
import os
from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.graph.knowledge_graph import KnowledgeGraph

@pytest.fixture
def complex_ontology(tmp_path):
    """Creates a highly complex ontology with multiple entity classes and relationships."""
    ontology_data = {
        'world': {
            'name': 'CorporateWorld',
            'description': 'An ontology for companies, their aliases, and financial data.',
            'main_entities': ['Company']
        },
        'entity_classes': {
            'Company': {
                'description': 'A business entity.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'aliases', 'type': 'string'},
                    {'name': 'industry', 'type': 'string'}
                ]
            },
            'Financial_Metric': {
                'description': 'A financial metric for a company.',
                'properties': [
                    {'name': 'metric_id', 'type': 'string', 'primary_key': True},
                    {'name': 'metric_type', 'type': 'string'},
                    {'name': 'value', 'type': 'float'}
                ]
            }
        },
        'relationships': {
            'HAS_METRIC': {
                'description': 'A Company has a Financial_Metric.',
                'domain': 'Company',
                'range': 'Financial_Metric',
                'properties': [{'name': 'year', 'type': 'integer'}]
            }
        }
    }
    file_path = tmp_path / "complex_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USER = os.environ.get("NEOJ4_USER")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

@pytest.fixture(scope="function", params=["networkx", "neo4j"])
def knowledge_graph(request, tmp_path):
    use_neo4j = request.param == "neo4j"
    if use_neo4j and not (NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD):
        pytest.skip("Neo4j credentials not provided, skipping test.")

    # Setup ontology
    ontology_file = tmp_path / "company_ontology.yaml"
    with open(ontology_file, "w") as f:
        # A simple ontology for testing
        yaml.dump({
            'world': {
                'name': 'Test Company KG',
                'description': 'A simple KG for testing.',
                'main_entities': ['Company', 'Financial_Metric']
            },
            'entity_classes': {
                'Company': {
                    'description': 'A business entity.',
                    'properties': [
                        {'name': 'name', 'type': 'string', 'primary_key': True},
                        {'name': 'industry', 'type': 'string'}
                    ]
                },
                'Financial_Metric': {
                    'description': 'A financial metric for a company.',
                    'properties': [
                        {'name': 'metric_id', 'type': 'string', 'primary_key': True},
                        {'name': 'metric_type', 'type': 'string'},
                        {'name': 'value', 'type': 'float'}
                    ]
                }
            },
            'relationships': {
                'HAS_METRIC': {
                    'description': 'A company has a financial metric.',
                    'domain': 'Company',
                    'range': 'Financial_Metric',
                    'properties': [
                        {'name': 'year', 'type': 'integer'}
                    ]
                }
            }
        }, f)

    ontology = KnowledgeOntology(ontology_file=str(ontology_file))
    graph_file = tmp_path / "test_graph.pickle"
    
    kg = KnowledgeGraph(
        ontology=ontology, 
        use_neo4j=use_neo4j, 
        graph_file=str(graph_file),
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD
    )
    
    yield kg  # Provide the kg instance to the test

    # Teardown: close the graph connection after the test
    kg.close()


def test_alias_querying(knowledge_graph):
    """
    Tests that querying with an alias correctly retrieves the canonical entity's data.
    """
    # Ingest initial knowledge with aliases
    ingested = knowledge_graph.update_knowledge("Intel Corporation participates in the semiconductor industry.")
    print(ingested)
    
    # Query using an alias
    result = knowledge_graph.query("What industry does Intel participate in?")
    print(result)
    assert "semiconductor" in result.lower()

def test_alias_in_updates(knowledge_graph):
    """
    Tests that updating an entity via an alias correctly merges the information.
    """
    # Initial entity
    knowledge_graph.update_knowledge("Intel Corporation is a company in the semiconductor industry.")
    
    # Update using an alias
    knowledge_graph.update_knowledge("Intel has a new financial metric: revenue of 50 billion in 2025.")

    # Query for the updated information on the canonical name
    result = knowledge_graph.query("What is the revenue of Intel Inc.?")
    
    assert "50,000,000,000" in result

def test_alias_relationship_integrity(knowledge_graph):
    """
    Tests that relationships are preserved when entities are updated through aliases.
    """
    # Establish a relationship
    print(knowledge_graph.update_knowledge("Intel Corporation has a financial metric 'Q1 Revenue' with a value of 20.0."))
    # Update the company using an alias
    print(knowledge_graph.update_knowledge("Intel Inc. is in the 'chips' industry."))

    # Verify that the relationship still holds and the new property is added
    result = knowledge_graph.query("What is the value of the 'Q1 Revenue' metric for Intel Corporation?")
    print(result)
    
    assert "20" in result
    
    # Also verify the new property
    result_industry = knowledge_graph.query("What industry is Intel in?")
    print(result_industry)
    assert "chips" in result_industry.lower()
