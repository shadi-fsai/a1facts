import pytest
from unittest.mock import Mock, patch, mock_open

from a1facts.ontology.ontology_rewrite_agent import OntologyRewriteAgent

@patch('a1facts.ontology.ontology_rewrite_agent.Agent')
def test_ontology_rewrite_agent(MockAgent):
    """
    Tests that the OntologyRewriteAgent correctly constructs a prompt
    and calls the internal agent.
    """
    # 1. Setup
    mock_agent_instance = Mock()
    mock_agent_instance.run.return_value = Mock(content="Rewritten Text")
    MockAgent.return_value = mock_agent_instance
    
    ontology_yaml_content = """
    world:
      name: Test World
    """
    ontology_file_path = "dummy_ontology.yaml"
    
    # 2. Mocks
    # Mock the file system to avoid actual file I/O
    m_open = mock_open(read_data=ontology_yaml_content)
    with patch('builtins.open', m_open):
        # 3. Execution
        rewrite_agent = OntologyRewriteAgent(ontology_yaml=ontology_file_path, mytools=[])
        result = rewrite_agent.rewrite_query("Original Text")

    # 4. Assertions
    # Verify the Agent was initialized correctly
    MockAgent.assert_called_once()
    
    # Verify open was called with the correct ontology file
    m_open.assert_called_once_with(ontology_file_path, 'r')
    
    # Verify the agent's run method was called
    mock_agent_instance.run.assert_called_once()
    
    # Verify the prompt construction
    # We check the argument that agent.run was called with
    prompt_arg = mock_agent_instance.run.call_args[0][0]
    assert "Here is the ontology:" in prompt_arg
    assert "Test World" in prompt_arg # Check that ontology content is in the prompt
    assert "Here is the text to rewrite: Original Text" in prompt_arg
    
    # Verify the result is returned correctly
    assert result == "Rewritten Text"
