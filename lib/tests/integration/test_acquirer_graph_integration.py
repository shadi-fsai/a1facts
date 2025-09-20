import pytest
from unittest.mock import Mock, patch
import yaml

from a1facts.knowledge_base import KnowledgeBase

@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.knowledge_graph.QueryAgent')
@patch('a1facts.graph.knowledge_graph.UpdateAgent')
def test_acquire_and_ingest_flow(MockUpdateAgent, MockQueryAgent, MockAcquirerAgent, tmp_path):
    """
    Integration test to verify that acquired knowledge is correctly passed to the
    knowledge graph for ingestion.
    """
    # 1. Setup a mock ontology and config files
    ontology_data = {
        'world': {'name': 'TestWorld', 'description': '...'},
        'entity_classes': {}, 'relationships': {}
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

    # 3. Mock the return value of the acquirer's agent
    # This simulates the LLM returning new knowledge to be added to the graph.
    mock_acquirer_agent_instance = MockAcquirerAgent.return_value
    acquired_knowledge = "This is a new piece of knowledge."
    mock_acquirer_agent_instance.run.return_value = Mock(content=acquired_knowledge)
    
    # We also need to mock the graph's internal update agent to intercept the final call
    mock_update_agent_instance = MockUpdateAgent.return_value

    # 4. Run the acquisition process
    query = "Find new knowledge."
    result = kb.acquire_knowledge_for_query(query)

    # 5. Assertions
    # a) Verify the acquirer's agent was called with the query
    mock_acquirer_agent_instance.run.assert_called_once_with(query)
    assert result == acquired_knowledge

    # b) Verify the knowledge graph's update_knowledge method was called,
    #    which in turn calls the update_agent. We can check the final call.
    # We will also mock the rewrite_agent to simplify the test
    with patch.object(kb.graph, '_rewrite_query') as mock_rewrite:
        mock_rewrite.return_value = acquired_knowledge
        kb.ingest_knowledge(acquired_knowledge)
        mock_update_agent_instance.update.assert_called_with(acquired_knowledge)
        
    # c) Verify the graph database's save method was called after ingestion
    with patch.object(kb.graph.graph_database, 'save') as mock_save:
        kb.ingest_knowledge(acquired_knowledge)
        mock_save.assert_called_once()
