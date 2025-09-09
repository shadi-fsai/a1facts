import sys
import os
import time

from colored import cprint
from a1facts import KnowledgeBase
from agno.agent import Agent
from textwrap import dedent
from utils.modelconfig import my_model

def main():
    a1facts = KnowledgeBase("tests\\e2e\\a1facts", "tests\\e2e\\company.yaml", "tests\\e2e\\sources.yaml", use_neo4j=False)
    
#    a1facts.ingest_knowledge("Winnibago's revenue in FY 2024 was $100 million based on the SEC filings")
    # Read sources file and ingest the knowledge
#    sources_file_path = "..\\..\\..\\fortusight\\fortusight\\Analysis_Output\\AAPL_analysis_output_\\memory.md"
#    with open(sources_file_path, 'r', encoding='utf-8') as file:
#        sources_content = file.read()
    
#    a1facts.ingest_knowledge(sources_content)

#    a1facts.ingest_knowledge("Winnibago's revenue in FY 2024 was $100 million based on the SEC filings")
#    print(a1facts.query("get_Financial_Metrics_Company_reports(kwargs={'from_Company_name': 'Winnebago'})"))#what was Winnibago's revenue in FY 2024?"))
#    return
    agent = Agent(
        name="finance_info_agent",
        role="get financial information about the company",
        model=my_model,
        tools=a1facts.get_tools(),
        instructions=dedent("""get financial information about the company"""),
        markdown=True,
        debug_mode=False,
    )
    query = "what do you know about about Winnibago and how they make money?"
    result = agent.run(query)
    print(result.content)
    
if __name__ == "__main__":
    main()