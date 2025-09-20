import pytest
import yaml
from unittest.mock import Mock, patch

from a1facts.knowledge_base import KnowledgeBase

def create_mock_ontology_file(tmp_path, name, description):
    """Helper function to create a temporary ontology YAML file."""
    ontology_data = {
        'world': {
            'name': name,
            'description': description
        },
        'entity_classes': {},
        'relationships': {}
    }
    file_path = tmp_path / f"{name}_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.knowledge_graph.QueryAgent')
@patch('a1facts.graph.knowledge_graph.UpdateAgent')
def test_acquirer_prompt_rewriting_with_different_ontologies(MockUpdateAgent, MockQueryAgent, MockAcquirerAgent, tmp_path):
    """
    Integration test to verify that the KnowledgeAcquirer's instructions
    are dynamically rewritten based on the provided ontology.
    """
    # 1. Create two different mock ontologies
    ontology_file_A = create_mock_ontology_file(tmp_path, "FinancialWorld", "Data about companies and markets.")
    ontology_file_B = create_mock_ontology_file(tmp_path, "SportsWorld", "Data about athletes and teams.")
    
    # Mock the knowledge sources config file
    sources_config_file = tmp_path / "sources.yaml"
    sources_config_file.write_text("{'knowledge_sources': {}}")

    # 2. Initialize KnowledgeBase with the first ontology
    # The KnowledgeAcquirer is initialized within the KnowledgeBase
    with patch('pickle.dump'), patch('builtins.open', side_effect=open):
        kb_A = KnowledgeBase(name="TestKB_A", ontology_config_file=ontology_file_A, knowledge_sources_config_file=str(sources_config_file))

    # 3. Capture the instructions passed to the acquirer's agent
    # The agent is initialized once, so we can inspect the call_args
    assert MockAcquirerAgent.call_count == 1
    instructions_A = MockAcquirerAgent.call_args.kwargs['instructions']
    
    # Verify content from the first ontology
    assert "FinancialWorld" in instructions_A
    assert "SportsWorld" not in instructions_A

    # 4. Reset the mock and initialize with the second ontology
    MockAcquirerAgent.reset_mock()
    with patch('pickle.dump'), patch('builtins.open', side_effect=open):
        kb_B = KnowledgeBase(name="TestKB_B", ontology_config_file=ontology_file_B, knowledge_sources_config_file=str(sources_config_file))

    # 5. Capture and verify the new instructions
    assert MockAcquirerAgent.call_count == 1
    instructions_B = MockAcquirerAgent.call_args.kwargs['instructions']
    
    assert "SportsWorld" in instructions_B
    assert "FinancialWorld" not in instructions_B
    
    # 6. Final check: ensure the two sets of instructions are different
    assert instructions_A != instructions_B
