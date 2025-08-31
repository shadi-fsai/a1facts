from agno.agent import Agent
from datetime import datetime
from textwrap import dedent
from agno.tools.exa import ExaTools
from agno.models.openai import OpenAIChat
#from agno.models.groq import Groq
from dotenv import load_dotenv
from colored import cprint
from agno.tools import tool
from graph import Neo4jGraph
#from agno.models.google import Gemini
import time

load_dotenv()

my_model = OpenAIChat(id="gpt-4.1")
#my_query_model = Gemini(id="gemini-2.5-flash")#OpenAIChat(id="gpt-4.1-mini")

graph = Neo4jGraph()

def get_ontology_description():
    try:
        with open('funding_ontology.py', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Error: funding_ontology.py file not found"
    except Exception as e:
        return f"Error reading funding_ontology.py: {str(e)}"

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
        # Example 1: Adding a VC entity
        entity_example1 = {
            "label": "VC",
            "primary_key_field": "name",
            "properties": {
                "name": "Sequoia Capital",
                "website": "https://www.sequoiacap.com/"
            }
        }
        
        # Example 2: Adding a Portfolio_Company entity
        entity_example2 = {
            "label": "Portfolio_Company",
            "primary_key_field": "name",
            "properties": {
                "name": "Stripe",
                "website": "https://stripe.com/"
            }
        }
        
        # Example 3: Adding an Investment entity
        entity_example3 = {
            "label": "Investment",
            "primary_key_field": "name",
            "properties": {
                "name": "Stripe Series A",
                "investment_amount": 20000000,
                "funding_round": "Series A",
                "investment_date": "2012-02-09"
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

    Examples:
        # Example 1: Adding an invests_in relationship
        relationship_example1 = {
            "start_node_label": "VC",
            "start_node_pk_val": "Sequoia Capital",
            "end_node_label": "Investment",
            "end_node_pk_val": "Stripe Series A",
            "relationship_type": "invests_in",
            "properties": {}
        }
    """
    # Save knowledge to file with timestamp    
    graph.add_relationship(relationship["start_node_label"], relationship["start_node_pk_val"], relationship["end_node_label"], relationship["end_node_pk_val"], relationship["relationship_type"], properties=relationship.get("properties"))
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
        # Example 1: Getting a VC entity
        entity_example1 = {
            "entity_label": "VC",
            "entity_pk_val": "Sequoia Capital"
        }
        # Example 2: Getting a Portfolio_Company entity  
        entity_example2 = {
            "entity_label": "Portfolio_Company",
            "entity_pk_val": "Stripe"
        }
    """
    start_time = time.time()
    entity_info = graph.get_entity_info(entity_label, entity_pk_val)
    end_time = time.time()
    print(f"get_entity_info took {end_time - start_time:.4f} seconds")

    
    if entity_info:
        return entity_info
    else:
        return "No entity found with label '{entity_label}' and primary key value '{entity_pk_val}'"


@tool(show_result=False, stop_after_tool_call=False)
def get_all_entities_by_label(entity_label: str) -> list:
    """
    Get all entities by label from the graph.
    Args:
        entity_label (str): The label of the entities to get
    Returns:
        list: A list of entity identifiers (primary key values).

    Examples:
        # Example 1: Getting all VCs
        entity_example1 = {
            "entity_label": "VC"
        }
        # Example 2: Getting all Portfolio_Companies
        entity_example2 = {
            "entity_label": "Portfolio_Company"
        }
    """

    all_entities = graph.get_all_entities_by_label(entity_label)
    if all_entities:
        return all_entities
    else:
        return "No entities found with label '{entity_label}'" 

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
        ExaTools(num_results=50, summary=True),
    ],
    instructions=dedent(f""" Use tables to display data. 
    Follow these steps when answering questions:

First, search the knowledge base for funding data, historical performance, and established valuation models.
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
queries=[]


# Find all Partners in the graph
partners = graph.get_all_entities_by_label("Partner")
print("Partners found in the graph:")
for partner in partners:
    print(f"- {partner}")

for partner in partners:
    queries.append(f"Find all investments made by {partner} and their target companies? For every target company, find all the other investors at each stage of their funding. List the names of the partners involved in the investments.")

#VC_list = ["Accel", "Benchmark Capital", "Andreessen Horowitz (a16z)", "Sequoia Capital", "Lightspeed Venture Partners", "Greylock Partners", "Battery Ventures", "Bessemer Venture Partners (BVP)", "Founders Fund", "General Catalyst", "Index Ventures", "Kleiner Perkins", "Redpoint Ventures", "First Round Capital"]
#for VC in VC_list:
#    queries.append(f"Find all investments made by {VC} and their target companies? For every target company, find all the other investors at each stage of their funding. List the names of the partners involved in the investments.")

for query in queries:

    print("*"*150)
    #start_time = time.time()
    #knowledge_base_response = knowledge_base_agent.run(query)
    #end_time = time.time()
    #cprint(f"Knowledge base query took {end_time - start_time:.2f} seconds", 'red')
    #cprint(knowledge_base_response.content, 'yellow')
    #print("*"*150)

    #websearchresponse = web_search_agent.run(query)
    #cprint(websearchresponse.content, 'green')
    #print("*"*150)
    start_time = time.time()
    financeresponse = finance_info_agent.run(query)
    end_time = time.time()
    cprint(f"Finance info query took {end_time - start_time:.2f} seconds", 'red')
    cprint(financeresponse.content, 'blue')
    print("*"*150)
    start_time = time.time()
    ontoresponse = onto_analysis.run(financeresponse.content)
    cprint(ontoresponse.content, 'green')
    end_time = time.time()
    cprint(f"Ontology & knoweldge graph update {end_time - start_time:.2f} seconds", 'red')
