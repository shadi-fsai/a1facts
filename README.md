# A1C Knowledge Graph

A1C is a Python-based system for building and interacting with a knowledge graph. It uses a defined ontology to structure data, ingests information from various sources, and allows for natural language queries to retrieve insights. The project is designed to be flexible, using a Neo4j backend to manage the graph data.

## Features

-   **Ontology-Driven**: Define your knowledge domain using simple YAML configuration files. The system dynamically builds tools and structures based on your ontology.
-   **Data Ingestion**: Ingest unstructured text and automatically map it to the defined ontology, creating structured entities and relationships in the graph.
-   **Natural Language Queries**: Ask questions in plain English to query the knowledge graph.
-   **Neo4j Backend**: Leverages the power of the Neo4j graph database for storing and querying complex relationships.

## Project Structure

```
.
├── src/
│   ├── enrichment/   # Handles acquiring and processing new knowledge
│   ├── graph/        # Manages the knowledge graph, including query and update agents
│   ├── ontology/     # Defines and manages the data ontology
│   └── utils/        # Utility scripts and configurations
├── test/             # Test scripts and sample data/ontology files
├── .env              # Neo4j connection credentials (to be created)
└── pyproject.toml    # Project dependencies and metadata
```

## Getting Started

Follow these steps to get the A1C Knowledge Graph running on your local machine.

### Prerequisites

-   Python 3.13+
-   [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver.
-   A running Neo4j Database instance.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd a1c
    ```

2.  **Create a virtual environment and install dependencies using `uv`:**
    ```bash
    # Create the virtual environment
    uv venv
    
    # Activate the virtual environment
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate

    # Install dependencies
    uv pip install -e .
    ```

### Configuration

The application requires credentials to connect to your Neo4j database.

1.  Create a file named `.env` in the root of the project directory.

2.  Add your Neo4j URI and password to the `.env` file:
    ```
    NEO4J_URI="bolt://localhost:7687"
    NEO4J_AUTH="your_neo4j_password"
    ```

## Usage

The `test/infoagent.py` script provides an example of how to use the system. It initializes the ontology and the knowledge graph, ingests data from local files, and runs queries.

To run the agent:
```bash
python test/infoagent.py
```

You can modify this script to change the input data, run different queries, or test other functionalities of the knowledge graph.
