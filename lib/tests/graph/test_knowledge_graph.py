import pytest
from unittest.mock import Mock, patch

from a1facts.graph.knowledge_graph import KnowledgeGraph

@pytest.fixture
def mock_ontology():
    """Fixture for a mocked KnowledgeOntology."""
    ontology = Mock()
    # Mock tool generation methods
    ontology.get_tools_get_entity_and_relationship.return_value = ["get_tool_1"]
    ontology.get_tools_add_or_update_entity_and_relationship.return_value = ["update_tool_1"]
    return ontology

@patch('a1facts.graph.knowledge_graph.NetworkxGraphDatabase')
@patch('a1facts.graph.knowledge_graph.Neo4jGraphDatabase')
@patch('a1facts.graph.knowledge_graph.QueryAgent')
@patch('a1facts.graph.knowledge_graph.UpdateAgent')
@patch('a1facts.graph.knowledge_graph.QueryRewriteAgent')
def test_initialization(MockRewrite, MockUpdate, MockQuery, MockNeo4j, MockNetworkx, mock_ontology):
    """
    Tests that KnowledgeGraph initializes correctly, selecting the right DB
    and setting up agents with tools.
    """
    # Test with use_neo4j = False
    kg_networkx = KnowledgeGraph(ontology=mock_ontology, use_neo4j=False)
    MockNetworkx.assert_called_once()
    MockNeo4j.assert_not_called()
    MockQuery.assert_called_with(mock_ontology, ["get_tool_1"])
    MockUpdate.assert_called_with(mock_ontology, ["update_tool_1"])
    MockRewrite.assert_called_with(mock_ontology, [])
    assert kg_networkx.graph_database == MockNetworkx.return_value

    # Reset mocks and test with use_neo4j = True
    MockNetworkx.reset_mock()
    MockNeo4j.reset_mock()
    kg_neo4j = KnowledgeGraph(ontology=mock_ontology, use_neo4j=True)
    MockNeo4j.assert_called_once()
    MockNetworkx.assert_not_called()
    assert kg_neo4j.graph_database == MockNeo4j.return_value

@patch('a1facts.graph.knowledge_graph.QueryAgent')
@patch('a1facts.graph.knowledge_graph.UpdateAgent')
@patch('a1facts.graph.knowledge_graph.QueryRewriteAgent')
def test_query_method(MockRewrite, MockUpdate, MockQuery, mock_ontology):
    """
    Tests the query method's orchestration of rewriting and querying.
    """
    kg = KnowledgeGraph(ontology=mock_ontology)
    
    # Mock internal agent instances
    kg.rewrite_agent = MockRewrite.return_value
    kg.query_agent = MockQuery.return_value
    
    # Set return values for chained calls
    kg.rewrite_agent.rewrite_query.return_value = "Rewritten Query"
    kg.query_agent.query.return_value = "Query Result"
    
    # Mock the internal helper that depends on the DB
    with patch.object(kg, '_get_class_entity_pairs') as mock_get_pairs:
        result = kg.query("Original Query")

        mock_get_pairs.assert_called_once()
        kg.rewrite_agent.rewrite_query.assert_called_once()
        kg.query_agent.query.assert_called_once_with("Rewritten Query")
        assert result == "Query Result"

@patch('a1facts.graph.knowledge_graph.QueryAgent')
@patch('a1facts.graph.knowledge_graph.UpdateAgent')
@patch('a1facts.graph.knowledge_graph.QueryRewriteAgent')
def test_update_knowledge_method(MockRewrite, MockUpdate, MockQuery, mock_ontology):
    """
    Tests the update_knowledge method's orchestration of rewriting and updating.
    """
    kg = KnowledgeGraph(ontology=mock_ontology)
    
    # Mock internal agent and DB instances
    kg.rewrite_agent = MockRewrite.return_value
    kg.update_agent = MockUpdate.return_value
    kg.graph_database = Mock() # A mock for the graph_database instance
    
    # Set return values
    kg.rewrite_agent.rewrite_query.return_value = "Rewritten Knowledge"
    update_result = Mock()
    update_result.content = "Update Result"
    kg.update_agent.update.return_value = update_result
    
    with patch.object(kg, '_get_class_entity_pairs') as mock_get_pairs:
        result = kg.update_knowledge("Original Knowledge")

        mock_get_pairs.assert_called_once()
        kg.rewrite_agent.rewrite_query.assert_called_once()
        kg.update_agent.update.assert_called_once_with("Rewritten Knowledge")
        kg.graph_database.save.assert_called_once()
        assert result == "Update Result"
