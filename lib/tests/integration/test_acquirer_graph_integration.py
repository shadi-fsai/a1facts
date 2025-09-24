import pytest
from unittest.mock import Mock, patch
import yaml

from a1facts.knowledge_base import KnowledgeBase

def test_acquire_and_ingest_flow(tmp_path):
    """
    Integration test to verify that acquired knowledge is correctly passed to the
    knowledge graph for ingestion.
    """
    # 1. Setup a mock ontology and config files
    ontology_data = {
        'world': {'name': 'TestWorld', 'description': '...', 'main_entities': ['TestEntity']},
        'entity_classes': {
            'TestEntity': {
                'description': 'A test entity.',
                'properties': [{'name': 'name', 'type': 'string', 'primary_key': True}]
            }
        },
        'relationships': {}
    }
    ontology_file = tmp_path / "ontology.yaml"
    with open(ontology_file, 'w') as f:
        yaml.dump(ontology_data, f)

    sources_config_file = tmp_path / "sources.yaml"
    sources_config_file.write_text("{'knowledge_sources': {}}")

    # 2. Initialize the KnowledgeBase
    kb = KnowledgeBase(
        name="TestKB",
        ontology_config_file=str(ontology_file),
        knowledge_sources_config_file=str(sources_config_file)
    )

    # 3. Mock the run method of the acquirer's agent instance
    acquired_knowledge = "This is a new piece of knowledge."
    with patch.object(kb.knowledge_acquirer.agent, 'run', return_value=Mock(content=acquired_knowledge)) as mock_acquirer_run:
        # 4. Run the acquisition process
        query = "Find new knowledge."
        result = kb.acquire_knowledge_for_query(query)

        # 5. Assertions
        # a) Verify the acquirer's agent was called with the query
        mock_acquirer_run.assert_called_once_with(query)
        assert result == acquired_knowledge

        # b) Verify that the update agent and save method were called after ingestion
        mock_rdfs_output = Mock()
        mock_rdfs_output.content.rdfs = ":TestEntity_1 a :TestEntity ; :name \"TestName\" ."
        with patch.object(kb.graph.update_agent.rdfs_agent, 'run', return_value=mock_rdfs_output) as mock_update_run, \
             patch.object(kb.graph.graph_database, 'save') as mock_save:
            kb.ingest_knowledge(acquired_knowledge)

            # Assert that the update agent and save methods were called
            mock_update_run.assert_called_once()
            mock_save.assert_called_once()
