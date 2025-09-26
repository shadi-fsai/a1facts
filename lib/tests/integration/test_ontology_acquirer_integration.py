import pytest
import yaml
from unittest.mock import Mock, patch

from a1facts.knowledge_base import KnowledgeBase
from a1facts.enrichment.knowledge_acquirer import KnowledgeAcquirer

def create_mock_ontology_file(tmp_path, name, description, main_entities):
    """Helper function to create a temporary ontology YAML file."""
    ontology_data = {
        'world': {
            'name': name,
            'description': description,
            'main_entities': main_entities
        },
        'entity_classes': {},
        'relationships': {}
    }
    for entity in main_entities:
        ontology_data['entity_classes'][entity] = {
            'description': f'A {entity} entity.',
            'properties': [{'name': 'name', 'type': 'string', 'primary_key': True}]
        }
    file_path = tmp_path / f"{name}_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

def test_acquirer_prompt_rewriting_with_different_ontologies(tmp_path):
    """
    Integration test to verify that the KnowledgeAcquirer's instructions
    are dynamically rewritten based on the provided ontology.
    """
    # 1. Create two different mock ontologies
    ontology_file_A = create_mock_ontology_file(tmp_path, "FinancialWorld", "Data about companies and markets.", ["Company"])
    ontology_file_B = create_mock_ontology_file(tmp_path, "SportsWorld", "Data about athletes and teams.", ["Athlete"])
    
    # Mock the knowledge sources config file
    sources_config_file = tmp_path / "sources.yaml"
    sources_config_file.write_text("{'knowledge_sources': {}}")

    # 2. Initialize KnowledgeBase with the first ontology and verify instructions
    with patch.object(KnowledgeAcquirer, 'get_acquisition_instructions') as mock_get_instructions_A:
        mock_get_instructions_A.return_value = "Instructions for FinancialWorld"
        kb_A = KnowledgeBase(name="TestKB_A", ontology_config_file=ontology_file_A, knowledge_sources_config_file=str(sources_config_file))
        
        mock_get_instructions_A.assert_called_once()
        assert kb_A.knowledge_acquirer.agent.instructions == "Instructions for FinancialWorld"

    # 3. Initialize KnowledgeBase with the second ontology and verify instructions
    with patch.object(KnowledgeAcquirer, 'get_acquisition_instructions') as mock_get_instructions_B:
        mock_get_instructions_B.return_value = "Instructions for SportsWorld"
        kb_B = KnowledgeBase(name="TestKB_B", ontology_config_file=ontology_file_B, knowledge_sources_config_file=str(sources_config_file))

        mock_get_instructions_B.assert_called_once()
        assert kb_B.knowledge_acquirer.agent.instructions == "Instructions for SportsWorld"
