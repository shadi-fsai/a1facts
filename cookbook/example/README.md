This example demonstrates how to use `a1facts` to build a simple financial analyst agent. This agent can answer questions about companies by using a knowledge graph and external data sources.

### How it Works

The agent is built using the following components:

-   **`infoagent.py`**: The main script that creates and runs the agent. It initializes the `a1facts` tool, which acts as the bridge between the agent and the knowledge graph.
-   **`company.yaml`**: This file defines the schema of our knowledge graph. It specifies the types of entities (e.g., `Company`, `Product_Service`, `Market`) and the relationships between them (e.g., `competes_with`, `operates_in`).
-   **`sources.yaml`**: This file configures the external data sources. In this case, it's set up to use the Financial Modeling Prep (FMP) API.
-   **`fmp_functions.py`**: This file contains the Python functions that interact with the FMP API to fetch data.

When you run `infoagent.py`, it initializes an agent with the `a1facts` tool. The agent is then asked a question: `"what do you know about how UnitedHealth competes with CVS?"`. The `a1facts` tool uses the information from the `company.yaml` and `sources.yaml` to understand the query, fetch relevant data from the FMP API using the functions in `fmp_functions.py`, and then provides an answer.

### Running the Example

1.  **Set up your environment:**

    Create a `.env` file in the root of this project and add your Financial Modeling Prep API key:

    ```
    FMP_KEY=your_fmp_api_key
    ```

2.  **Run the agent:**

    Navigate to the `example` directory and run the following command:

    ```bash
    python infoagent.py
    ```

This will run the agent and print the answer to the query in the console.
