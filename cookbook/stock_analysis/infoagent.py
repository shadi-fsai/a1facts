import sys
import os
import time


from colored import cprint
from a1facts.knowledge_base import KnowledgeBase
from agno.agent import Agent
from textwrap import dedent
from a1facts.utils.modelconfig import my_model


def main():
    a1facts = KnowledgeBase("finance_info_agent", "company.yaml", "sources.yaml")
    exit()
    agent = Agent(
        name="finance_info_agent",
        role="get financial information about the company",
        model=my_model,
        tools=a1facts.get_tools(),
        instructions=dedent("""get financial information about the company, always start with query tool, if you don't get a satisfactory answer use the acquire tool to get new knowledge.
        never use your internal knowledge to answer the question, only use the tools to get information from the knowledge graph and the knowledge sources. - never make up information"""),
        markdown=True,
        debug_mode=False,
    )
    query = "what do you know about how UnitedHealth competes with CVS?"
    result = agent.run(query)
    print(result.content)
    
if __name__ == "__main__":
    main()