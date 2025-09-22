import pytest
from unittest.mock import MagicMock, patch, Mock
from a1facts.graph.update_agent import UpdateAgent, RDFSResult
from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.graph.graph_database import BaseGraphDatabase

@pytest.fixture
def mock_ontology():
    """Fixture for a mocked KnowledgeOntology."""
    return MagicMock(spec=KnowledgeOntology)

@pytest.fixture
def mock_graph_db():
    """Fixture for a mocked GraphDatabase."""
    return MagicMock(spec=BaseGraphDatabase)

@patch('a1facts.graph.update_agent.Agent')
def test_update_agent_init(MockAgent, mock_ontology, mock_graph_db):
    """Test the initialization of UpdateAgent."""
    update_agent = UpdateAgent(ontology=mock_ontology, graph_database=mock_graph_db)
    assert update_agent.ontology == mock_ontology
    assert update_agent.graph_database == mock_graph_db
    assert MockAgent.call_count == 1 # Only rdfs_agent should be initialized
    
    # Check rdfs_agent initialization
    rdfs_agent_args, rdfs_agent_kwargs = MockAgent.call_args_list[0]
    assert rdfs_agent_kwargs['name'] == "RDFS Agent"
    assert rdfs_agent_kwargs['output_schema'] == RDFSResult

@patch('a1facts.graph.update_agent.Agent')
def test_update_agent_update(MockAgent, mock_ontology, mock_graph_db):
    """Test the update method of UpdateAgent."""
    # Arrange
    mock_rdfs_agent_instance = MagicMock()
    MockAgent.return_value = mock_rdfs_agent_instance
    
    update_agent = UpdateAgent(ontology=mock_ontology, graph_database=mock_graph_db)
    
    knowledge_to_update = "Some new knowledge"
    rdfs_content = "<...>"
    rdfs_result = RDFSResult(rdfs=rdfs_content, other_information="...", ontology_elements_used=[])
    
    mock_rdfs_agent_instance.run.return_value = Mock(content=rdfs_result)
    
    # Mock the parsing result from the ontology
    mock_entities = [MagicMock(), MagicMock()]
    mock_relationships = [MagicMock(), MagicMock()]
    mock_ontology.parse_rdfs_with_validation.return_value = (mock_entities, mock_relationships)

    # Act
    update_agent.update(knowledge_to_update)

    # Assert
    mock_rdfs_agent_instance.run.assert_called_once_with("Translate the following knowledge into a structured format based on the ontology\n\n " + knowledge_to_update)
    mock_ontology.parse_rdfs_with_validation.assert_called_once_with(rdfs_content)
    
    # Verify that the graph database methods were called for each parsed entity and relationship
    for entity in mock_entities:
        mock_graph_db.add_or_update_entity.assert_any_call(entity)
    assert mock_graph_db.add_or_update_entity.call_count == len(mock_entities)
    
    for rel in mock_relationships:
        mock_graph_db.add_relationship.assert_any_call(rel)
    assert mock_graph_db.add_relationship.call_count == len(mock_relationships)
