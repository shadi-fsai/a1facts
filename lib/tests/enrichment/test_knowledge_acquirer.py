import pytest
import yaml
from unittest.mock import Mock, patch
import os
import pickle
import hashlib

from a1facts.enrichment.knowledge_acquirer import KnowledgeAcquirer
from a1facts.utils.logger import logger

@pytest.fixture
def mock_ontology():
    """Fixture for a mocked KnowledgeOntology."""
    ontology = Mock()
    ontology.rewrite_agent.rewrite_query.return_value = "Rewritten instructions"
    # Add a mock hash for caching tests
    ontology_str = "ontology_details_for_hashing"
    type(ontology).name = "TestOntology"
    type(ontology).description = "A mock ontology for testing."
    type(ontology).__str__ = Mock(return_value=ontology_str)
    return ontology

@pytest.fixture
def mock_graph():
    """Fixture for a mocked KnowledgeGraph."""
    return Mock()

# ==============================================================================
# 1. Tests for Configuration and Initialization
# ==============================================================================

def test_initialization_with_valid_config(tmp_path, mock_ontology, mock_graph):
    """
    Tests that KnowledgeAcquirer initializes correctly with a valid config file.
    """
    config_data = {
        'knowledge_sources': {
            'source1': {
                'type': 'function',
                'name': 'Test Function Source',
                'description': 'A test source.',
                'module_path': 'path/to/module',
                'functions': ['func1']
            }
        }
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    with patch('a1facts.enrichment.knowledge_acquirer.FunctionKnowledgeSource') as MockFuncSource, \
         patch('a1facts.enrichment.knowledge_acquirer.ExaTools') as MockExa, \
         patch('a1facts.enrichment.knowledge_acquirer.Agent') as MockAgent:

        mock_source_instance = Mock()
        mock_source_instance.query_tool.return_value = "function_tool"
        MockFuncSource.return_value = mock_source_instance

        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, str(config_file))

        assert len(acquirer.knowledge_sources) == 1
        MockFuncSource.assert_called_once_with(config_data['knowledge_sources']['source1'])
        MockExa.assert_called_once()
        MockAgent.assert_called_once()
        
        agent_args, agent_kwargs = MockAgent.call_args
        assert len(agent_kwargs['tools']) == 3
        assert "function_tool" in agent_kwargs['tools']

def test_initialization_with_empty_sources(tmp_path, mock_ontology, mock_graph):
    """
    Tests initialization with a config file that has an empty 'knowledge_sources' section.
    """
    config_data = {'knowledge_sources': {}}
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    with patch('a1facts.enrichment.knowledge_acquirer.Agent'):
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, str(config_file))
        assert len(acquirer.knowledge_sources) == 0

def test_initialization_with_no_sources_key(tmp_path, mock_ontology, mock_graph):
    """
    Tests initialization with a config file missing the 'knowledge_sources' key.
    This is validated by the fix I just added.
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text("{}")

    with patch('a1facts.enrichment.knowledge_acquirer.Agent'):
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, str(config_file))
        assert len(acquirer.knowledge_sources) == 0

def test_initialization_raises_value_error_for_missing_type(tmp_path, mock_ontology, mock_graph):
    """
    Tests that a ValueError is raised if a source in the config is missing the 'type' field.
    """
    config_data = {
        'knowledge_sources': {
            'source1': {
                'name': 'Source without a type'
            }
        }
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Your knowledge source config is missing the 'type' field for source: source1"):
        KnowledgeAcquirer(mock_graph, mock_ontology, str(config_file))

def test_initialization_handles_unknown_source_type(tmp_path, mock_ontology, mock_graph):
    """
    Tests that the system handles an unknown source type gracefully by logging a warning.
    """
    config_data = {
        'knowledge_sources': {
            'source1': {
                'type': 'unknown_type'
            }
        }
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    with patch.object(logger, 'warning') as mock_warning, \
         patch('a1facts.enrichment.knowledge_acquirer.Agent'):
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, str(config_file))
        assert len(acquirer.knowledge_sources) == 0
        mock_warning.assert_called_with("Unknown knowledge source type: unknown_type")

# ==============================================================================
# 2. Tests for Acquisition Instruction Generation
# ==============================================================================

def test_get_acquisition_instructions_calls_rewrite_agent(mock_ontology, mock_graph):
    """
    Tests that get_acquisition_instructions correctly uses the OntologyRewriteAgent
    on a cache miss.
    """
    # We patch load_knowledge_sources to prevent it from trying to open a config file.
    with patch('a1facts.enrichment.knowledge_acquirer.KnowledgeAcquirer.load_knowledge_sources', return_value=[]), \
         patch('a1facts.enrichment.knowledge_acquirer.Agent') as MockAgent, \
         patch('os.path.exists', return_value=False), \
         patch('builtins.open'), \
         patch('pickle.dump'):

        # We don't need a real config file since load_knowledge_sources is patched.
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, "dummy_config.yaml")

        # The acquirer is initialized with instructions.
        # os.path.exists returning False ensures the rewrite agent is called.
        mock_ontology.rewrite_agent.rewrite_query.assert_called_once()
        template = acquirer.get_template()
        # Check that it was called with the template string
        mock_ontology.rewrite_agent.rewrite_query.assert_called_with(template)

        # Check that the instructions from the rewrite agent were used to init the agent
        assert MockAgent.call_args.kwargs['instructions'] == "Rewritten instructions"

# ==============================================================================
# 3. Tests for Instruction Caching Logic
# ==============================================================================

@patch('a1facts.enrichment.knowledge_acquirer.KnowledgeAcquirer.load_knowledge_sources', return_value=[])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('os.path.exists', return_value=False)
@patch('builtins.open')
@patch('pickle.dump')
def test_instruction_caching_creates_cache_on_first_run(mock_pickle_dump, mock_open, mock_path_exists, mock_agent, mock_load_sources, tmp_path, mock_ontology, mock_graph):
    """
    Tests that a cache file is created on the first run (cache miss).
    """
    os.chdir(tmp_path)  # Run in tmp_path to check for the pickle file
    KnowledgeAcquirer(mock_graph, mock_ontology, "dummy_config.yaml")

    # Verify we don't try to load sources (which would hang the test)
    mock_load_sources.assert_called_once()
    # Verify we checked for the cache file, which triggers the cache miss
    mock_path_exists.assert_called_with('acquirer_instructions.pickle')

    # Verify the core logic for a cache miss
    mock_ontology.rewrite_agent.rewrite_query.assert_called_once()
    mock_open.assert_called_once_with('acquirer_instructions.pickle', 'wb')
    mock_pickle_dump.assert_called_once()

    # Check that the hash in the dumped data is correct
    ontology_str = str(mock_ontology)
    expected_hash = hashlib.sha256(ontology_str.encode('utf-8')).hexdigest()
    dump_args, _ = mock_pickle_dump.call_args
    assert dump_args[0]['ontology_hash'] == expected_hash

@patch('a1facts.enrichment.knowledge_acquirer.KnowledgeAcquirer.load_knowledge_sources', return_value=[])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('os.path.exists', return_value=True)
@patch('pickle.load')
@patch('pickle.dump')
def test_instruction_caching_loads_from_cache_on_hit(mock_pickle_dump, mock_pickle_load, mock_exists, mock_agent, mock_load_sources, mock_ontology, mock_graph):
    """
    Tests that instructions are loaded from cache if the ontology hash matches.
    """
    ontology_str = str(mock_ontology)
    current_hash = hashlib.sha256(ontology_str.encode('utf-8')).hexdigest()
    mock_pickle_load.return_value = {
        'ontology_hash': current_hash,
        'instructions': 'Cached instructions'
    }

    with patch('builtins.open'):
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, "dummy_config.yaml")

        # Verify we didn't try to load sources, which would hang
        mock_load_sources.assert_called_once()
        
        # Rewrite agent should NOT be called if cache hits
        mock_ontology.rewrite_agent.rewrite_query.assert_not_called()
        # Pickle dump should not be called
        mock_pickle_dump.assert_not_called()
        
        # Check that the cached instructions were used to initialize the agent
        assert mock_agent.call_args.kwargs['instructions'] == 'Cached instructions'


@patch('a1facts.enrichment.knowledge_acquirer.KnowledgeAcquirer.load_knowledge_sources', return_value=[])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('os.path.exists', return_value=True)
@patch('pickle.load')
@patch('pickle.dump')
def test_instruction_caching_regenerates_on_miss(mock_pickle_dump, mock_pickle_load, mock_exists, mock_agent, mock_load_sources, mock_ontology, mock_graph):
    """
    Tests that instructions are regenerated if the ontology hash does not match.
    """
    mock_pickle_load.return_value = {
        'ontology_hash': 'old_hash',
        'instructions': 'Outdated instructions'
    }

    with patch('builtins.open'):
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, "dummy_config.yaml")

        # Verify we didn't try to load sources, which would hang
        mock_load_sources.assert_called_once()

        # Rewrite agent SHOULD be called
        mock_ontology.rewrite_agent.rewrite_query.assert_called_once()
        # Pickle dump SHOULD be called to update the cache
        mock_pickle_dump.assert_called_once()
        
        # Check that the new instructions were used
        assert mock_agent.call_args.kwargs['instructions'] == 'Rewritten instructions'

# ==============================================================================
# 4. Tests for Knowledge Acquisition (Orchestration)
# ==============================================================================

def test_acquire_method_calls_agent_run(mock_ontology, mock_graph):
    """
    Tests that the acquire method correctly calls the internal agent's run method.
    """
    # Patch load_knowledge_sources to avoid the FileNotFoundError on the dummy config
    with patch('a1facts.enrichment.knowledge_acquirer.KnowledgeAcquirer.load_knowledge_sources', return_value=[]), \
         patch('a1facts.enrichment.knowledge_acquirer.Agent') as MockAgent:
        # Set up a mock agent instance
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = Mock(content="Agent Result")
        MockAgent.return_value = mock_agent_instance
        
        acquirer = KnowledgeAcquirer(mock_graph, mock_ontology, "dummy_config.yaml")
        
        query = "What is the capital of France?"
        result = acquirer.acquire(query)
        
        # Verify agent.run was called with the query
        mock_agent_instance.run.assert_called_once_with(query)
        # Verify the result is the content from the agent's response
        assert result == "Agent Result"
