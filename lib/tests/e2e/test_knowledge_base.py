import pytest
from a1facts.knowledge_base import KnowledgeBase
import os
import yaml
from unittest.mock import Mock, patch

# E2E tests will be added here to validate the full KnowledgeBase lifecycle.

def create_e2e_ontology(tmp_path):
    """Creates a simple but realistic ontology file for E2E testing."""
    ontology_data = {
        'world': {
            'name': 'E2E Test World',
            'description': 'A world for testing the full lifecycle.'
        },
        'entity_classes': {
            'Person': {
                'description': 'A human being.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'description': 'The name of the person.', 'primary_key': True},
                    {'name': 'age', 'type': 'integer', 'description': 'The age of the person.'}
                ]
            }
        },
        'relationships': {}
    }
    file_path = tmp_path / "e2e_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

def create_complex_ontology(tmp_path):
    """Creates a more complex ontology with multiple entity and relationship classes."""
    ontology_data = {
        'world': {
            'name': 'CorporateWorld',
            'description': 'An ontology for companies, employees, and their roles.'
        },
        'entity_classes': {
            'Company': {
                'description': 'A business entity.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'industry', 'type': 'string'}
                ]
            },
            'Person': {
                'description': 'A human being.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'age', 'type': 'integer'}
                ]
            },
            'Role': {
                'description': 'A position or function within a company.',
                'properties': [
                    {'name': 'title', 'type': 'string', 'primary_key': True}
                ]
            }
        },
        'relationships': {
            'WORKS_AT': {
                'description': 'A Person works at a Company.',
                'domain': 'Person',
                'range': 'Company',
                'properties': [
                    {'name': 'role_title', 'type': 'string'}
                ]
            },
            'HAS_ROLE': {
                'description': 'A Person has a Role.',
                'domain': 'Person',
                'range': 'Role',
                'properties': []
            }
        }
    }
    file_path = tmp_path / "complex_ontology.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return str(file_path)

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.update_agent.Agent')
@patch('a1facts.graph.query_agent.Agent')
def test_knowledge_base_full_lifecycle(MockQueryAgentInternal, MockUpdateAgentInternal, MockAcquirerAgent, tmp_path, db_backend, request):
    """
    Tests the full end-to-end lifecycle of the KnowledgeBase.
    This test runs for both NetworkX and Neo4j backends.
    """
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    # 1. Setup: Create configs and initialize KnowledgeBase with a unique DB file
    ontology_file = create_e2e_ontology(tmp_path)
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_full_lifecycle_{db_backend}.pickle"

    kb = KnowledgeBase(
        name=f"E2ETest_{db_backend}",
        ontology_config_file=ontology_file,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # Mock the internal agno.Agent instances' .run() method for each agent
    mock_query_run = MockQueryAgentInternal.return_value.run
    mock_update_run = MockUpdateAgentInternal.return_value.run
    mock_acquirer_run = MockAcquirerAgent.return_value.run

    # 2. Query Empty Graph: Simulate the agent finding no information.
    # The QueryAgent's logic will return a fallback string if content is empty.
    mock_query_run.return_value = Mock(content=None) # Simulate empty response from LLM
    result_empty = kb.query("What is the age of Alice?")
    assert "A verifiable answer is not available" in result_empty
    mock_query_run.assert_called_once()

    # 3. Acquire Knowledge: Simulate the acquirer finding new information.
    acquired_knowledge = "The person Alice is 30 years old."
    mock_acquirer_run.return_value = Mock(content=acquired_knowledge)
    
    new_knowledge = kb.acquire_knowledge_for_query("Find info about Alice.")
    assert new_knowledge == acquired_knowledge
    
    # 4. Ingest Knowledge: Simulate the update agent processing the knowledge.
    # The `acquire_knowledge_for_query` method automatically calls `ingest_knowledge`.
    with patch.object(kb.graph, '_rewrite_query', return_value=acquired_knowledge):
        kb.ingest_knowledge(acquired_knowledge)
        
        # Verify that the update agent's internal run method was called with the
        # correct, fully-formed prompt.
        expected_prompt = (
            "Translate the following knowledge into a structured format based on the ontology, "
            "then add every entity and every relationship to the graph using the tools available to you.\n \n "
            f"{acquired_knowledge}"
        )
        mock_update_run.assert_called_with(expected_prompt)

    # 5. Query Populated Graph: Now, simulate the agent finding the data.
    mock_query_run.reset_mock()
    mock_query_run.return_value = Mock(content="The age of Alice is 30.")
    
    result_populated = kb.query("What is the age of Alice?")
    assert "age of Alice is 30" in result_populated
    mock_query_run.assert_called_once()

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.update_agent.Agent')
@patch('a1facts.graph.query_agent.Agent')
def test_knowledge_extension_e2e(MockQueryAgentInternal, MockUpdateAgentInternal, MockAcquirerAgent, tmp_path, db_backend, request):
    """
    Tests a more complex E2E flow for both backends.
    """
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    # 1. Setup with a unique DB file
    ontology_file = create_e2e_ontology(tmp_path)
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_extension_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"E2ETestExtension_{db_backend}",
        ontology_config_file=ontology_file,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    # Mock the internal agents' run methods
    mock_query_run = MockQueryAgentInternal.return_value.run
    mock_update_run = MockUpdateAgentInternal.return_value.run
    mock_acquirer_run = MockAcquirerAgent.return_value.run

    # 2. Ingest Initial Knowledge
    initial_knowledge = "There is a person named Bob."
    # We will directly add this to the graph to simulate a pre-existing state
    kb.graph.graph_database.add_or_update_entity("Person", "name", {"name": "Bob"})

    # 3. Acquire New Knowledge
    new_knowledge = "Bob is 42 years old."
    mock_acquirer_run.return_value = Mock(content=new_knowledge)
    
    acquired_info = kb.acquire_knowledge_for_query("How old is Bob?")
    assert acquired_info == new_knowledge
    
    # 4. Ingest and Extend Knowledge
    # In a real run, this would involve an LLM call to translate knowledge to tool calls.
    # We will simulate the outcome of that LLM call: updating the existing entity.
    # The acquirer's run would trigger an ingest, which calls the update agent.
    # We can simulate this by directly calling the update function on the real graph DB.
    kb.graph.graph_database.add_or_update_entity("Person", "name", {"name": "Bob", "age": 42})

    # 5. Verify the Update
    # We now query the graph for the new information.
    # In a real scenario, this would go through the query agent.
    # We can simulate the agent finding the data in our NetworkX graph.
    all_persons = kb.graph.graph_database.get_all_entities_by_label("Person")
    
    # Assert that the entity was updated, not duplicated
    assert len(all_persons) == 1
    bob_data = all_persons[0]
    assert bob_data.get("name") == "Bob"
    assert bob_data.get("age") == 42
    
    # Finally, simulate the query agent returning this data
    mock_query_run.return_value = Mock(content="Bob is 42 years old.")
    final_result = kb.query("What is Bob's age?")
    assert "42" in final_result

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.update_agent.Agent')
@patch('a1facts.graph.query_agent.Agent')
def test_stress_knowledge_base(MockQueryAgentInternal, MockUpdateAgentInternal, MockAcquirerAgent, tmp_path, db_backend, request):
    """
    Stress tests the system for both backends.
    """
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    # 1. Setup with a unique DB file
    ontology_file = create_e2e_ontology(tmp_path)
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_stress_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"StressTestKB_{db_backend}",
        ontology_config_file=ontology_file,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )
    
    # Mock the internal agents' run methods
    mock_query_run = MockQueryAgentInternal.return_value.run
    mock_acquirer_run = MockAcquirerAgent.return_value.run
    
    # 2. Populate the Graph with a large number of entities
    num_entities = 1000
    for i in range(num_entities):
        kb.graph.graph_database.add_or_update_entity(
            "Person", "name", {"name": f"Person_{i}", "age": 20 + (i % 50)}
        )

    # Verify that all entities were added
    all_persons = kb.graph.graph_database.get_all_entities_by_label("Person")
    assert len(all_persons) == num_entities

    # 3. Query for a specific entity in the populated graph
    target_person_name = "Person_500"
    mock_query_run.return_value = Mock(content=f"The age of {target_person_name} is 20.")
    query_result = kb.query(f"What is the age of {target_person_name}?")
    assert "20" in query_result
    mock_query_run.assert_called_once()

    # 4. Update an existing entity
    # Simulate an update call that would be triggered by an ingest operation
    kb.graph.graph_database.add_or_update_entity(
        "Person", "name", {"name": target_person_name, "age": 21}
    )
    
    # Verify the update by checking the graph directly
    updated_person = kb.graph.graph_database.get_entity_properties("Person", "name", target_person_name)
    assert updated_person['age'] == 21

    # 5. Acquire and Extend new knowledge for a different entity
    acquire_target = "Person_750"
    new_knowledge = f"{acquire_target} now has an occupation of 'Engineer'."
    mock_acquirer_run.return_value = Mock(content=new_knowledge)
    
    acquired_info = kb.acquire_knowledge_for_query(f"What is {acquire_target}'s job?")
    assert acquired_info == new_knowledge
    
    # Simulate the ingestion of this new property
    kb.graph.graph_database.add_or_update_entity(
        "Person", "name", {"name": acquire_target, "occupation": "Engineer"}
    )
    
    # Verify the extension
    extended_person = kb.graph.graph_database.get_entity_properties("Person", "name", acquire_target)
    assert extended_person['occupation'] == 'Engineer'
    # Ensure the original property is still there
    assert 'age' in extended_person

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.update_agent.Agent')
@patch('a1facts.graph.query_agent.Agent')
def test_complex_ontology_relationships(MockQueryAgentInternal, MockUpdateAgentInternal, MockAcquirerAgent, tmp_path, db_backend, request):
    """
    Tests ingestion and querying of entities and relationships with properties
    using a more complex, multi-class ontology.
    """
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    # 1. Setup with complex ontology
    ontology_file = create_complex_ontology(tmp_path)
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_complex_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"ComplexE2E_{db_backend}",
        ontology_config_file=ontology_file,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    mock_query_run = MockQueryAgentInternal.return_value.run

    # 2. Ingest interconnected entities
    kb.graph.graph_database.add_or_update_entity("Person", "name", {"name": "Alice", "age": 30})
    kb.graph.graph_database.add_or_update_entity("Company", "name", {"name": "InnovateCorp", "industry": "Tech"})
    
    # 3. Add a relationship with properties
    kb.graph.graph_database.add_relationship(
        "Person", "name", "Alice",
        "Company", "name", "InnovateCorp",
        "WORKS_AT", {"role_title": "Lead Developer"}
    )
    
    # 4. Verify the relationship and its properties via query
    # Simulate the query agent finding the role title from the relationship
    mock_query_run.return_value = Mock(content="Alice's role at InnovateCorp is Lead Developer.")
    
    query = "What is Alice's role at InnovateCorp?"
    result = kb.query(query)
    
    assert "Lead Developer" in result
    mock_query_run.assert_called_once()

    # 5. Verify by checking the graph directly for more detailed validation
    if use_neo4j:
        with kb.graph.graph_database.driver.session() as session:
            res = session.run("""
                MATCH (p:Person {name: 'Alice'})-[r:WORKS_AT]->(c:Company {name: 'InnovateCorp'})
                RETURN r.role_title AS role
            """).single()
            assert res is not None
            assert res["role"] == "Lead Developer"
    else: # NetworkX
        rel_props = kb.graph.graph_database.get_relationship_properties(
            "Person", "name", "Alice",
            "WORKS_AT",
            "Company", "name", "InnovateCorp"
        )
        assert rel_props is not None
        assert rel_props.get("role_title") == "Lead Developer"

@pytest.mark.e2e
@pytest.mark.parametrize("db_backend", ["networkx", "neo4j"])
@patch('a1facts.enrichment.knowledge_acquirer.Agent')
@patch('a1facts.graph.update_agent.Agent')
@patch('a1facts.graph.query_agent.Agent')
def test_stress_complex_ontology(MockQueryAgentInternal, MockUpdateAgentInternal, MockAcquirerAgent, tmp_path, db_backend, request):
    """
    Stress tests the system using the complex ontology with many interconnected
    entities and relationships.
    """
    use_neo4j = (db_backend == "neo4j")
    neo4j_uri, neo4j_user, neo4j_password = None, None, None
    if use_neo4j:
        neo4j_config = request.getfixturevalue('clean_neo4j_db')
        neo4j_uri = neo4j_config["uri"]
        neo4j_user = neo4j_config["user"]
        neo4j_password = neo4j_config["password"]

    # 1. Setup
    ontology_file = create_complex_ontology(tmp_path)
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("{'knowledge_sources': {}}")
    db_file = tmp_path / f"kb_complex_stress_{db_backend}.pickle"
    kb = KnowledgeBase(
        name=f"ComplexStress_{db_backend}",
        ontology_config_file=ontology_file,
        knowledge_sources_config_file=str(sources_file),
        use_neo4j=use_neo4j,
        graph_file=str(db_file),
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )

    mock_query_run = MockQueryAgentInternal.return_value.run

    # 2. Populate the Graph
    num_companies = 50
    persons_per_company = 20
    for i in range(num_companies):
        company_name = f"Company_{i}"
        kb.graph.graph_database.add_or_update_entity(
            "Company", "name", {"name": company_name, "industry": "Tech"}
        )
        for j in range(persons_per_company):
            person_name = f"Person_{i}_{j}"
            kb.graph.graph_database.add_or_update_entity(
                "Person", "name", {"name": person_name, "age": 30 + j}
            )
            kb.graph.graph_database.add_relationship(
                "Person", "name", person_name,
                "Company", "name", company_name,
                "WORKS_AT", {"role_title": "Engineer"}
            )
    
    total_persons = num_companies * persons_per_company
    total_entities = total_persons + num_companies
    # Each relationship creates one edge in NetworkX and Neo4j
    total_relationships = total_persons

    if use_neo4j:
        with kb.graph.graph_database.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            assert node_count == total_entities
            assert rel_count == total_relationships
    else: # NetworkX
        assert kb.graph.graph_database.graph.number_of_nodes() == total_entities
        assert kb.graph.graph_database.graph.number_of_edges() == total_relationships

    # 3. Query for a specific relationship in the populated graph
    target_person = "Person_25_10"
    target_company = "Company_25"
    mock_query_run.return_value = Mock(content=f"{target_person}'s role at {target_company} is Engineer.")
    
    query = f"What is {target_person}'s role at {target_company}?"
    result = kb.query(query)
    assert "Engineer" in result
    mock_query_run.assert_called_once()
