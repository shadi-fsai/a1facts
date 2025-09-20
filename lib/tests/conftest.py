import pytest
import os
from neo4j import GraphDatabase

# This file contains shared fixtures for the entire test suite.

# ==============================================================================
# Neo4j Docker Fixtures
# ==============================================================================

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """
    Constructs the absolute path to the docker-compose.yml file, relative
    to the location of the graph tests.
    """
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "graph", "docker-compose.yml")

def is_neo4j_responsive(uri):
    """Check if Neo4j is responsive."""
    try:
        with GraphDatabase.driver(uri, auth=("neo4j", "password")) as driver:
            driver.verify_connectivity()
            return True
    except Exception:
        return False

@pytest.fixture(scope="session")
def neo4j_service(docker_services):
    """
    Manages the lifecycle of the Neo4j Docker container, waits for it to be ready,
    and returns connection details.
    """
    bolt_port = docker_services.port_for("neo4j", 7687)
    http_port = docker_services.port_for("neo4j", 7474)
    uri = f"bolt://localhost:{bolt_port}"

    docker_services.wait_until_responsive(
        timeout=60.0, pause=1.0, check=lambda: is_neo4j_responsive(uri)
    )

    return {
        "uri": uri,
        "http_uri": f"http://localhost:{http_port}",
        "user": "neo4j",
        "password": "password",
    }
