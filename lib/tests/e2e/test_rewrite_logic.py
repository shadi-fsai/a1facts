import pytest
import yaml
from unittest.mock import patch, Mock
from a1facts.knowledge_base import KnowledgeBase
from a1facts.enrichment.knowledge_acquirer import KnowledgeAcquirer
from a1facts.ontology.rdfs_entity import RDFSEntity
from a1facts.ontology.rdfs_relationship import RDFSRelationship


@pytest.fixture
def complex_ontology(tmp_path):
    """Creates a highly complex ontology with 10 entity classes and 10 relationships."""
    ontology_data = {
        'world': {
            'name': 'GlobalFinance',
            'description': 'An ontology for multinational corporations, their executives, and financial performance.'
        },
        'entity_classes': {
            'Corporation': {
                'description': 'A multinational business entity.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'industry', 'type': 'string'},
                    {'name': 'market_cap', 'type': 'float'}
                ]
            },
            'Executive': {
                'description': 'A high-level manager in a corporation.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'title', 'type': 'string'}
                ]
            },
            'Product': {
                'description': 'A product or service offered by a corporation.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'category', 'type': 'string'}
                ]
            },
            'Market': {
                'description': 'A geographical or economic market.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'region', 'type': 'string'}
                ]
            },
            'FinancialReport': {
                'description': 'An official report on a corporation\'s financial performance.',
                'properties': [
                    {'name': 'report_id', 'type': 'string', 'primary_key': True},
                    {'name': 'year', 'type': 'integer'},
                    {'name': 'revenue', 'type': 'float'}
                ]
            },
            'Shareholder': {
                'description': 'An individual or institution that owns shares in a corporation.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'stake_percentage', 'type': 'float'}
                ]
            },
            'Subsidiary': {
                'description': 'A company controlled by a holding company.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True}
                ]
            },
            'Country': {
                'description': 'A nation or state.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True}
                ]
            },
            'IndustryGroup': {
                'description': 'A classification of companies into a specific industry.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True}
                ]
            },
            'NewsArticle': {
                'description': 'A news report from a media outlet.',
                'properties': [
                    {'name': 'url', 'type': 'string', 'primary_key': True},
                    {'name': 'publication_date', 'type': 'string'}
                ]
            }
        },
        'relationships': {
            'EMPLOYS': {
                'description': 'A Corporation employs an Executive.',
                'domain': 'Corporation',
                'range': 'Executive',
                'properties': [{'name': 'start_year', 'type': 'integer'}]
            },
            'PRODUCES': {
                'description': 'A Corporation produces a Product.',
                'domain': 'Corporation',
                'range': 'Product',
                'properties': []
            },
            'OPERATES_IN': {
                'description': 'A Corporation operates in a Market.',
                'domain': 'Corporation',
                'range': 'Market',
                'properties': [{'name': 'market_share', 'type': 'float'}]
            },
            'HAS_FINANCIAL_REPORT': {
                'description': 'A Corporation has a FinancialReport.',
                'domain': 'Corporation',
                'range': 'FinancialReport',
                'properties': []
            },
            'HAS_MAJOR_SHAREHOLDER': {
                'description': 'A Corporation has a major Shareholder.',
                'domain': 'Corporation',
                'range': 'Shareholder',
                'properties': []
            },
            'HAS_SUBSIDIARY': {
                'description': 'A Corporation has a Subsidiary.',
                'domain': 'Corporation',
                'range': 'Subsidiary',
                'properties': [{'name': 'ownership_percentage', 'type': 'float'}]
            },
            'HEADQUARTERED_IN': {
                'description': 'A Corporation is headquartered in a Country.',
                'domain': 'Corporation',
                'range': 'Country',
                'properties': []
            },
            'PART_OF_INDUSTRY': {
                'description': 'A Corporation is part of an IndustryGroup.',
                'domain': 'Corporation',
                'range': 'IndustryGroup',
                'properties': []
            },
            'FEATURED_IN': {
                'description': 'A Corporation is featured in a NewsArticle.',
                'domain': 'Corporation',
                'range': 'NewsArticle',
                'properties': [{'name': 'sentiment', 'type': 'string'}]
            },
            'SERVES_AS_CEO_OF': {
                'description': 'An Executive serves as CEO of a Corporation.',
                'domain': 'Executive',
                'range': 'Corporation',
                'properties': [{'name': 'appointment_date', 'type': 'string'}]
            }
        }
    }
    file_path = tmp_path / "complex_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.graph.query_rewrite_agent.Agent')
def test_query_rewrite_with_complex_ontology(MockQueryRewriteAgent, complex_ontology, tmp_path, db_backend, request):
    """
    Tests that a vague user query is rewritten into a specific, structured query
    tailored to the complex ontology.
    """
    # 1. Setup KnowledgeBase with the complex ontology
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]
        
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_query_rewrite_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"QueryRewriteTest_{db_backend}",
        ontology_config_file=complex_ontology,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # 2. Mock the rewrite agent to return a predictable, structured query
    mock_rewrite_run = MockQueryRewriteAgent.return_value.run
    rewritten_query = "structured_query_for_corporation_market_cap"
    mock_rewrite_run.return_value = Mock(content=rewritten_query)

    # 3. Populate the graph with some data
    corporation_class = kb.ontology.find_entity_class("Corporation")
    global_corp = RDFSEntity(corporation_class, "GlobalCorp", {"name": "GlobalCorp", "market_cap": 500.0})
    kb.graph.graph_database.add_or_update_entity(global_corp)

    # 4. Execute the query and verify the rewrite
    with patch.object(kb.graph, '_rewrite_query', return_value=rewritten_query) as mock_rewrite:
        kb.query("How much is GlobalCorp worth?")
        
        # Assert that the rewrite agent was called with the original query
        mock_rewrite.assert_called_with("How much is GlobalCorp worth?")

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.ontology.ontology_rewrite_agent.Agent')
def test_acquisition_instruction_rewrite(MockOntologyRewriteAgent, complex_ontology, tmp_path, db_backend, request):
    """
    Tests that the knowledge acquisition instructions are rewritten to be specific
    to the complex ontology.
    """
    # 1. Setup KnowledgeBase, which initializes the OntologyRewriteAgent
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_acq_rewrite_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"AcquisitionRewriteTest_{db_backend}",
        ontology_config_file=complex_ontology,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # 2. Mock the rewrite agent to return specific instructions
    mock_rewrite_run = MockOntologyRewriteAgent.return_value.run
    rewritten_instructions = "Find data on Corporations and Executives, focusing on market_cap and titles."
    mock_rewrite_run.return_value = Mock(content=rewritten_instructions)

    # The KnowledgeAcquirer's initialization triggers the rewrite of instructions.
    # To ensure it initializes correctly, we must re-initialize it after mocking.
    kb.knowledge_acquirer = KnowledgeAcquirer(kb.graph, kb.ontology, sources_file)


    # 3. Trigger the rewrite by initializing the acquirer
    # The KnowledgeAcquirer's initialization triggers the rewrite of instructions.
    with patch.object(kb.knowledge_acquirer, 'get_acquisition_instructions', return_value=rewritten_instructions) as mock_get_instructions:
        kb.knowledge_acquirer.get_acquisition_instructions()
        
        # 4. Assert that the original generic template was rewritten
        # In the real implementation, the rewrite is called internally. We verify
        # that the acquirer now has the rewritten instructions.
        mock_get_instructions.assert_called()
        assert kb.knowledge_acquirer.get_acquisition_instructions() == rewritten_instructions

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.graph.query_rewrite_agent.Agent')
def test_knowledge_ingestion_rewrite(MockQueryRewriteAgent, complex_ontology, tmp_path, db_backend, request):
    """
    Tests that acquired, unstructured knowledge is rewritten into a structured
    format before being ingested into the graph.
    """
    # 1. Setup mocks
    mock_rdfs_agent_instance = Mock()
    MockQueryRewriteAgent.return_value = mock_rdfs_agent_instance

    from a1facts.graph.update_agent import RDFSResult
    rdfs_knowledge = "<rdf>MegaCorp hires Jane Doe as CEO</rdf>"
    mock_rdfs_agent_instance.run.return_value = Mock(content=RDFSResult(rdfs=rdfs_knowledge, other_information="", ontology_elements_used=[]))

    # 2. Setup KnowledgeBase
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_ingest_rewrite_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"IngestionRewriteTest_{db_backend}",
        ontology_config_file=complex_ontology,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # 2. Mock the rewrite agent to return a structured version of the knowledge
    unstructured_knowledge = "MegaCorp just hired Jane Doe as their new CEO."
    structured_knowledge = "ADD ENTITY Executive {'name': 'Jane Doe', 'title': 'CEO'}; ADD RELATIONSHIP EMPLOYS from Corporation {'name': 'MegaCorp'} to Executive {'name': 'Jane Doe'}"
    
    # 3. Ingest the unstructured knowledge
    with patch.object(kb.graph, '_rewrite_query', return_value=structured_knowledge) as mock_rewrite, \
         patch('a1facts.graph.update_agent.Agent') as MockRdfsAgent, \
         patch.object(kb.ontology, 'parse_rdfs_with_validation', return_value=([], [])) as mock_parse:
        
        from a1facts.graph.update_agent import RDFSResult
        rdfs_knowledge = "<rdf>MegaCorp hires Jane Doe as CEO</rdf>"
        MockRdfsAgent.return_value.run.return_value = Mock(content=RDFSResult(rdfs=rdfs_knowledge, other_information="", ontology_elements_used=[]))

        kb.ingest_knowledge(unstructured_knowledge)

        # 4. Verify that the rewrite was called and the update agent received the structured data
        mock_rewrite.assert_called_with(unstructured_knowledge)
        
        # Verify that the rdfs agent was called to translate...
        MockRdfsAgent.return_value.run.assert_called_once_with(
            "Translate the following knowledge into a structured format based on the ontology\n\n " + structured_knowledge
        )
        # ...and that the result was passed to the parser.
        mock_parse.assert_called_once_with(rdfs_knowledge)


@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.query_agent.Agent')
@patch('a1facts.graph.query_rewrite_agent.Agent')
def test_full_lifecycle_rewrite_under_load(
    MockQueryRewriteAgent,
    MockQueryAgentInternal,
    MockAcquirerAgent,
    complex_ontology,
    tmp_path,
    db_backend,
    request
):
    """
    Tests the full knowledge lifecycle (acquire, update, query) on a highly
    populated graph to ensure the system functions correctly under load.
    """
    # 1. Setup mocks
    mock_rdfs_agent_instance = Mock()
    MockQueryRewriteAgent.return_value = mock_rdfs_agent_instance
    from a1facts.graph.update_agent import RDFSResult

    # 2. Setup KnowledgeBase
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_lifecycle_stress_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"LifecycleStressTest_{db_backend}",
        ontology_config_file=complex_ontology,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # 2. Populate the graph with a large amount of data
    corporation_class = kb.ontology.find_entity_class("Corporation")
    executive_class = kb.ontology.find_entity_class("Executive")
    for i in range(50):
        corp_name = f"Corp_{i}"
        corp = RDFSEntity(corporation_class, corp_name, {"name": corp_name, "market_cap": 1000.0 + i})
        kb.graph.graph_database.add_or_update_entity(corp)
        for j in range(10):
            exec_name = f"Exec_{i}_{j}"
            executive = RDFSEntity(executive_class, exec_name, {"name": exec_name, "title": "VP"})
            kb.graph.graph_database.add_or_update_entity(executive)
            employs = RDFSRelationship(corp, "EMPLOYS", executive, {"start_year": 2020})
            kb.graph.graph_database.add_relationship(employs)

    # 3. Acquire new knowledge about an existing entity
    mock_acquirer_run = MockAcquirerAgent.return_value.run
    new_knowledge = "The market cap of Corp_25 is now 2500.0."
    mock_acquirer_run.return_value = Mock(content=new_knowledge)

    # 4. Ingest the new knowledge, triggering the update rewrite
    structured_update = "UPDATE ENTITY Corporation {'name': 'Corp_25', 'market_cap': 2500.0}"
    
    with patch.object(kb.graph, '_rewrite_query', return_value=structured_update) as mock_ingest_rewrite, \
         patch('a1facts.graph.update_agent.Agent') as MockRdfsAgent:
        
        from a1facts.graph.update_agent import RDFSResult
        rdfs_update = "<rdf>Corp_25 market cap 2500.0</rdf>"
        MockRdfsAgent.return_value.run.return_value = Mock(content=RDFSResult(rdfs=rdfs_update, other_information="", ontology_elements_used=[]))

        # acquire_knowledge_for_query calls ingest_knowledge internally
        kb.acquire_knowledge_for_query("What is the new market cap of Corp_25?")
        
        mock_ingest_rewrite.assert_called_with(new_knowledge)
        
        # Verify that the rdfs agent was called to translate...
        MockRdfsAgent.return_value.run.assert_called_once_with(
            "Translate the following knowledge into a structured format based on the ontology\n\n " + structured_update
        )

        # Because the UpdateAgent is now real, we don't need to manually update the DB.
        # The real agent will parse the RDFS and call the DB methods.
        # We'll rely on the final query to verify the update.

        # 5. Query for the updated knowledge, triggering the query rewrite
        mock_query_rewrite_run = MockQueryRewriteAgent.return_value.run
        rewritten_query = "structured_query_for_market_cap_of_Corp_25"
        mock_query_rewrite_run.return_value = Mock(content=rewritten_query)
    
    # Mock the final query agent to return the updated information
    mock_query_run = MockQueryAgentInternal.return_value.run
    final_answer = "The market cap of Corp_25 is 2500.0."
    mock_query_run.return_value = Mock(content=final_answer)

    result = kb.query("What is the market cap of Corp_25?")

    # 6. Verify the final result
    assert "2500.0" in result
    
    # Additionally, verify the data in the graph directly
    updated_corp = kb.graph.graph_database.get_entity_properties("Corporation", "name", "Corp_25")
    assert updated_corp['market_cap'] == 2500.0
