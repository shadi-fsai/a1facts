from a1c import a1c
from agno.agent import Agent
from datetime import datetime
from textwrap import dedent
from agno.tools.exa import ExaTools
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from company_ontology import onto
from colored import cprint
from agno.tools import tool

load_dotenv()

my_cheap_model = OpenAIChat(id="gpt-4.1")

web_search_agent = Agent(
    name="Web Search Agent",
    role="Search the web for information",
    model=my_cheap_model,
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

finance_info_agent = Agent(
    name="Finance Info Agent",
    role="Get financial data and information",
    model=my_cheap_model,
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

def get_ontology_description():
    try:
        with open('company_ontology.py', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Error: company_ontology.py file not found"
    except Exception as e:
        return f"Error reading company_ontology.py: {str(e)}"

def get_knowledge_instantiation_example():
    try:
        with open('test.py', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Error: test.py file not found"
    except Exception as e:
        return f"Error reading test.py: {str(e)}"

@tool(show_result=False, stop_after_tool_call=False)
def add_to_knowledge_base(knowledge):
    """
    Add knowledge to the knowledge base.
    knowledge is a string of text.
    """
    # Save knowledge to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"knowledge_base_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Knowledge Entry - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n")
        f.write(knowledge)
        f.write("\n" + "="*80 + "\n\n")
    
    print(f"Knowledge saved to {filename}")
    print(knowledge)
    #onto.add_to_knowledge_base(knowledge)

onto_analysis = Agent(
    name="Ontology translation Agent",
    role="Translate knowledge into a structured format based on an existing ontology",
    model=my_cheap_model,
    tools=[
        ExaTools(num_results=1, summary=True),
 #       add_to_knowledge_base,
    ],
    instructions=dedent(f""" 
    The user is providing you unstrucutred knowledge. Translate the knowledge into a structured format based on the ontology.
    Ontology:[{get_ontology_description()}]
    Write the results of the instances in OWL format.
    Today is {datetime.now().strftime("%Y-%m-%d")}
"""),
    show_tool_calls=True,
    markdown=True,

)
query = "Who is the CEO of united health?"
print("*"*150)

#websearchresponse = web_search_agent.run(query)
#cprint(websearchresponse.content, 'green')
#print("*"*150)
financeresponse = finance_info_agent.run(query)
cprint(financeresponse.content, 'blue')
print("*"*150)
ontoresponse = onto_analysis.run(financeresponse.content)
cprint(ontoresponse.content, 'red')
