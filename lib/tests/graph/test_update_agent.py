import pytest
from unittest.mock import MagicMock, patch
from a1facts.graph.update_agent import UpdateAgent, RDFSResult
from a1facts.ontology.knowledge_ontology import KnowledgeOntology

@pytest.fixture
def mock_ontology():
    """Fixture for a mocked KnowledgeOntology."""
    return MagicMock(spec=KnowledgeOntology)

@pytest.fixture
def mock_tools():
    """Fixture for a mocked list of tools."""
    return [MagicMock(), MagicMock()]

@patch('a1facts.graph.update_agent.Agent')
def test_update_agent_init(MockAgent, mock_ontology, mock_tools):
    """Test the initialization of UpdateAgent."""
    update_agent = UpdateAgent(ontology=mock_ontology, mytools=mock_tools)
    assert update_agent.ontology == mock_ontology
    assert MockAgent.call_count == 2
    
    # Check rdfs_agent initialization
    rdfs_agent_args, rdfs_agent_kwargs = MockAgent.call_args_list[0]
    assert rdfs_agent_kwargs['name'] == "RDFS Agent"
    assert rdfs_agent_kwargs['output_schema'] == RDFSResult

    # Check update_agent initialization
    update_agent_args, update_agent_kwargs = MockAgent.call_args_list[1]
    assert update_agent_kwargs['name'] == "Knowledge Graph Update Agent"
    assert update_agent_kwargs['input_schema'] == RDFSResult


@patch('a1facts.graph.update_agent.Agent')
def test_update_agent_update(MockAgent, mock_ontology, mock_tools):
    """Test the update method of UpdateAgent."""
    # Arrange
    mock_rdfs_agent_instance = MagicMock()
    mock_update_agent_instance = MagicMock()

    # Have the Agent constructor return our mock instances in order
    MockAgent.side_effect = [mock_rdfs_agent_instance, mock_update_agent_instance]

    update_agent = UpdateAgent(ontology=mock_ontology, mytools=mock_tools)
    
    knowledge_to_update = "Some new knowledge"
    rdfs_result = RDFSResult(rdfs="<...>", other_information="...")
    
    mock_rdfs_agent_instance.run.return_value = rdfs_result
    mock_update_agent_instance.run.return_value = "Update successful"

    # Act
    result = update_agent.update(knowledge_to_update)

    # Assert
    mock_rdfs_agent_instance.run.assert_called_once_with("Translate the following knowledge into a structured format based on the ontology\n\n " + knowledge_to_update)
    mock_update_agent_instance.run.assert_called_once_with(rdfs_result.rdfs)
    assert result == "Update successful"
