# a1facts: An Agentic AI Knowledge Graph System

a1facts is a powerful Python framework for building and interacting with knowledge graphs. It allows you to define a clear structure (ontology) for your knowledge, intelligently ingest information from various sources, and use natural language to get precise, reliable answers. By grounding your AI agents in a structured knowledge graph, a1facts helps eliminate hallucinations and ensures that your agent's responses are based on verified facts.

This project supports a Neo4j backend to manage and query the graph data, providing a robust and scalable solution for your knowledge management needs.

![Architecture](public/Architecture.png)

## Key Features

-   **Ontology-Driven**: Define your knowledge domain with simple YAML files. a1facts uses this ontology to automatically create the tools and structures needed to interact with your data.
-   **Structured Data Ingestion and cross validation**: Convert unstructured text into structured entities and relationships within your knowledge graph, ensuring data quality and consistency.
-   **Natural Language Queries**: Ask questions in plain English. a1facts translates your queries into precise graph traversals to retrieve the information you need.
-   **Reliable AI Agents**: Build AI agents that can provide accurate and trustworthy answers by grounding them in the factual data of the knowledge graph.
-   **Neo4j Backend**: Supports Neo4j for efficient storage and complex querying of your knowledge base.

## Usage Scenario: Building AI Agents with Precise Answers

In many applications, it's critical for AI agents to provide answers that are not just plausible but also precise and factually correct. Standard large language models (LLMs) can sometimes "hallucinate" or generate incorrect information, which can be a major issue in domains like finance, legal, or scientific research.

a1facts addresses this problem by grounding your AI agent in a knowledge graph. Here's how it works:

1.  **Define Your Domain**: You start by creating an ontology that describes the key concepts and relationships in your specific domain. For example, in finance, you might define entities like `Company`, `Product`, and `Market`, and relationships like `competes_with` or `operates_in`.

    ![Ontology Example](public/Onto_example.png)

2.  **Populate the Graph**: You then ingest data from different sources into the knowledge graph. This could be from internal documents, databases, external APIs, or the web. a1facts ensures that this data is structured according to your ontology, but also that it's factual by triangulating facts from different sources.

    ![Example Knowledge Graph](public/example_KG.png)

3.  **Query with Confidence**: When your AI agent receives a question, it doesn't just rely on its internal training data. Instead, it uses a1facts to query the knowledge graph. This means the agent's answers are based on the structured, verified data.

    ![Query Example](public/Query_example.jpeg)

By using a1facts, you can build an AI agent that is not only intelligent but also trustworthy, providing precise and reliable answers every time.

a1facts is a work in progress, we'd love to hear from you on how you're using it and what you need it to do next.

## Getting Started

Follow these steps to get the a1facts Knowledge Graph running on your local machine.

### Prerequisites

-   Python 3.13+
-   [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer.
-   Optional: A running Neo4j Database instance.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shadi-fsai/a1facts.git
    cd a1facts/lib
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    # Create the virtual environment
    uv venv
    
    # Activate the virtual environment
    # On Windows: .venv\Scripts\activate
    # On macOS/Linux: source .venv/bin/activate
    .venv\Scripts\activate

    # Install dependencies
    uv pip install -e .
    ```

### Configuration

You'll need to provide credentials to connect to your Neo4j database and other services.

1.  Create a `.env` file in the root of the project.
2.  Add your API keys to the file:
    ```
    OPENAI_API_KEY="your_openai_api_key"
    EXA_API_KEY="your_exa_api_key"
    ```
3.  Optionally if you want to use neo4j add the following to the .env file
    NEO4J_URI="bolt://localhost:7687"
    NEO4J_AUTH="your_neo4j_password"
    ```

## Cookbook

The `cookbook/` directory contains practical examples of how to use a1facts.

The `cookbook/example/` directory shows how to build a financial analyst agent that can answer questions about companies. To run this example, navigate to the directory and run:

```bash
cd cookbook/example
uv add a1facts
uv run infoagent.py
```

You can modify this script to experiment with different data, queries, or other functionalities of the knowledge graph - see README.md in cookbook/ for more.

## Privacy Notice

We collect minimal usage statistics (number of times the library is run) to help improve the project. You can opt-out by setting the environment variable `A1FACTS_TELEMETRY_DISABLED=1`.

