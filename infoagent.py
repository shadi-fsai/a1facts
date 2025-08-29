from a1c import a1c
from agno.agent import Agent
from datetime import datetime
from textwrap import dedent
from agno.tools.exa import ExaTools
from agno.models.openai import OpenAIChat
#from agno.models.groq import Groq
from dotenv import load_dotenv
from company_ontology import onto
from colored import cprint
from agno.tools import tool
from graph import Neo4jGraph
#from agno.models.google import Gemini

load_dotenv()

my_model = OpenAIChat(id="gpt-4.1")
#my_query_model = Gemini(id="gemini-2.5-flash")#OpenAIChat(id="gpt-4.1-mini")

graph = Neo4jGraph()

def get_ontology_description():
    try:
        with open('company_ontology.py', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Error: company_ontology.py file not found"
    except Exception as e:
        return f"Error reading company_ontology.py: {str(e)}"

@tool(show_result=False, stop_after_tool_call=False)
def add_entity_to_graph(entity: dict) -> str:
    """
    Add entity to the graph.
    entity is a dictionary of properties.
    Args:
        entity (dict): A dictionary containing entity information with the following structure:
            - label (str): The type/label of the entity (e.g., "Company", "Person", "Stock")
            - primary_key_field (str): The field name that serves as the unique identifier
            - properties (dict): Key-value pairs of entity properties and their values
    
    Returns:
        str: Success message indicating the entity was added to the graph

    Examples:
        # Example 1: Adding a Company entity
        entity_example1 = {
            "label": "Company",
            "primary_key_field": "name",
            "properties": {
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "sector": "Technology",
                "market_cap": 3000000000000,
                "founded": 1976,
                "headquarters": "Cupertino, CA"
            }
        }
        
        # Example 2: Adding a Person entity
        entity_example2 = {
            "label": "Person",
            "primary_key_field": "full_name",
            "properties": {
                "full_name": "Tim Cook",
                "position": "CEO",
                "age": 63,
                "nationality": "American"
            }
        }
        
        # Example 3: Adding a Stock entity
        entity_example3 = {
            "label": "Stock",
            "primary_key_field": "ticker",
            "properties": {
                "ticker": "AAPL",
                "current_price": 185.50,
                "currency": "USD",
                "exchange": "NASDAQ"
            }
        }
    """
    # Save knowledge to file with timestamp
    graph.add_or_update_entity(entity["label"], entity["primary_key_field"], entity["properties"])
    return "Entity added to graph"

@tool(show_result=False, stop_after_tool_call=False)
def add_relationship_to_graph(relationship: dict) -> str:
    """
    Add relationship to the graph.
    
    Args:
        relationship (dict): A dictionary containing relationship properties with the following structure:
            - start_node_label (str): Label of the starting node
            - start_node_pk_val: Primary key value of the starting node
            - end_node_label (str): Label of the ending node
            - end_node_pk_val: Primary key value of the ending node
            - relationship_type (str): Type/name of the relationship
            - properties (dict): Additional properties for the relationship
    
    Returns:
        str: Success message indicating the relationship was added to the graph
    """
    # Save knowledge to file with timestamp    
    graph.add_relationship(relationship["start_node_label"], relationship["start_node_pk_val"], relationship["end_node_label"], relationship["end_node_pk_val"], relationship["relationship_type"], relationship["properties"])
    return "Entity added to graph"
      
@tool(show_result=False, stop_after_tool_call=False)
def get_entity_from_graph(entity_label: str, entity_pk_val: str) -> dict:
    """
    Get entity from the graph.
    Args:
        entity_label (str): The label of the entity to get
        entity_pk_val (str): The primary key value of the entity to get
    Returns:
        dict: A dictionary containing the entity's properties and its relationships

    Examples:
        # Example 1: Getting an Organization entity
        entity_example1 = {
            "entity_label": "Organization",
            "entity_pk_val": "Apple Inc."
        }
        # Example 2: Getting a Person entity  
        entity_example2 = {
            "entity_label": "Person",
            "entity_pk_val": "Tim Cook"
        }
    """
    return graph.get_entity_info(entity_label, entity_pk_val)

@tool(show_result=False, stop_after_tool_call=False)
def get_all_entities_by_label(entity_label: str) -> list:
    """
    Get all entities by label from the graph.
    Args:
        entity_label (str): The label of the entities to get
    Returns:
        list: A list of entity identifiers (primary key values).

    Examples:
        # Example 1: Getting all Organizations
        entity_example1 = {
            "entity_label": "Organization"
        }
        # Example 2: Getting all People
        entity_example2 = {
            "entity_label": "Person"
        }
    """
    return graph.get_all_entities_by_label(entity_label)

web_search_agent = Agent(
    name="Web Search Agent",
    role="Search the web for information",
    model=my_model,
    tools=[
        ExaTools(num_results=20, summary=True),
    ],
    instructions=dedent(f"""
    Search the web for information.
    Today is {datetime.now().strftime("%Y-%m-%d")}
    """),
    show_tool_calls=True,
    markdown=True,
)

knowledge_base_agent = Agent(
    name="Knowledge Base Agent",
    role="Get information from the knowledge base",
    model=my_model,
    tools=[
        get_entity_from_graph,
        get_all_entities_by_label,
    ],
    instructions=dedent(f"""
    Get information from the knowledge base.
    Use the get_entity_from_graph tool to get information from the graph.
    If you can't find the information in the graph, use the get_all_entities_by_label tool to get all entity identifiers by label.
    The ontology on which this knowledge base is based is [{get_ontology_description()}]
    Today is {datetime.now().strftime("%Y-%m-%d")}
    """),
    show_tool_calls=True,
    markdown=True,
)

finance_info_agent = Agent(
    name="Finance Info Agent",
    role="Get financial data and information",
    model=my_model,
    tools=[
        ExaTools(num_results=20, summary=True),
    ],
    instructions=dedent(f""" Use tables to display data. 
    Follow these steps when answering questions:

First, search the knowledge base for fundamental company data, historical performance, and established valuation models.
If the information in the knowledge base is incomplete OR if the user asks for real-time data or recent news, search the web to fill in gaps.
If you find all necessary fundamental data in the knowledge base, use it as the primary source for your analysis.
Always prioritize knowledge base information (for fundamentals and valuation) over web results.
If needed, supplement with web searches for:
Real-time stock prices and market data.
The latest financial news, press releases, and SEC filings.
Broader economic indicators and industry trends.
Analyst ratings and price targets.

When using the web: 
Search for at least 20 results per query, for each source assess their credibility and reliability using the following criteria:[
    A Completely reliable - There is no doubt about the source's authenticity, trustworthiness, or competency. The source has a history of complete reliability.
    B Usually reliable - There are minor doubts about the source's reliability. The source has a history of providing valid information most of the time.
    C Fairly reliable - There are doubts about the source's reliability, but they have provided valid information in the past.
    D Not usually reliable - There are significant doubts about the source's reliability.
    E Unreliable - The source has a history of providing invalid information.
    F Reliability cannot be judged - There is insufficient information to evaluate the source's reliability.]
    Never use sources that are rated D, E or F.

    When you are done synthesizing the information, assess each information based on the following criteria:[
    1. Confirmed - the information is confirmed by multiple different sources.
    2. Probably true - The information is logical and consistent with other information from different sources, but has not been fully corroborated.
    3. Possibly true - The information is reasonably logical, but cannot be judged to be probably true.
    4. Doubtful true - The information is not logical and may be contradicted by other information, but its falsehood cannot be confirmed.
    5. Improbable - The information is illogical and contradicted by other information.
    6. Credibility cannot be judged - There is insufficient information to assess the validity of the information.
    ]
    Only use information that is Confirmed, Probably true or Possibly true.
    Ensure that the information is not outdated relative to the current date.

    When information is confirmed by multiple sources, provide the sources in your reponse.

    Today is {datetime.now().strftime("%Y-%m-%d")}"""),
    show_tool_calls=True,
    markdown=True,
)

onto_analysis = Agent(
    name="Ontology translation Agent",
    role="Translate knowledge into a structured format based on an existing ontology",
    model=my_model,
    tools=[
        ExaTools(num_results=1, summary=True),
        add_entity_to_graph,
        add_relationship_to_graph,
    ],
    instructions=dedent(f""" 
    The user is providing you unstrucutred knowledge. Translate the knowledge into a structured format based on the ontology.
    Ontology:[{get_ontology_description()}]
    Return the results in RDFS format.
    When you are done, add every entity and relationship to the graph using the add_entity_to_graph and add_relationship_to_graph tools 
    Today is {datetime.now().strftime("%Y-%m-%d")}
"""),
    show_tool_calls=True,
    markdown=True,
)
query = "Who is the CEO of united health?"
print("*"*150)

import time
start_time = time.time()
knowledge_base_response = knowledge_base_agent.run(query)
end_time = time.time()
cprint(f"Knowledge base query took {end_time - start_time:.2f} seconds", 'red')
cprint(knowledge_base_response.content, 'yellow')
print("*"*150)

#websearchresponse = web_search_agent.run(query)
#cprint(websearchresponse.content, 'green')
#print("*"*150)
start_time = time.time()
financeresponse = finance_info_agent.run(query)
end_time = time.time()
cprint(f"Finance info query took {end_time - start_time:.2f} seconds", 'red')
#cprint(financeresponse.content, 'blue')
print("*"*150)
start_time = time.time()
ontoresponse = onto_analysis.run(financeresponse.content)
#cprint(ontoresponse.content, 'green')
end_time = time.time()
cprint(f"Ontology & knoweldge graph update {end_time - start_time:.2f} seconds", 'red')
