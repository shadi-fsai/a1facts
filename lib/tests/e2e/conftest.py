import pytest

# This file is used for pytest configuration.

# Ignore the test_mcp_client.py file during test collection.
# It is not relevant to the a1facts library and has broken dependencies.
collect_ignore = ["test_mcp_client.py"]

from neo4j import GraphDatabase

@pytest.fixture
def clean_neo4j_db(neo4j_service):
    """
    Fixture that provides Neo4j connection details and ensures the database is
    clean before each test that uses it.
    """
    uri = neo4j_service["uri"]
    user = neo4j_service["user"]
    password = neo4j_service["password"]

    # Clean the database before the test runs
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    # Yield the connection details to the test
    yield neo4j_service
