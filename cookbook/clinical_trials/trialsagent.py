import sys
import os
import time

from colored import cprint
from a1facts import KnowledgeBase
from agno.agent import Agent
from textwrap import dedent
from utils.modelconfig import my_model

def main():
    a1facts = KnowledgeBase("clinical_trials_agent", "trials.yaml", "sources.yaml")

    agent = Agent(
        name="clinical_trials_agent",
        role="get clinical trials information",
        model=my_model,
        tools=[],#a1facts.get_tools(),
        instructions=dedent("""get clinical trials information, always start with query tool, if you don't get a satisfactory answer use the acquire tool to get new knowledge.
        never use your internal knowledge to answer the question, only use the tools to get information from the knowledge graph and the knowledge sources. - never make up information"""),
        show_tool_calls=True,
        markdown=True,
        debug_mode=False,
    )
    query = "List all Phase II clinical trials for drugs targeting GLP-1 that have reported primary endpoint data in the last 6 months, excluding those with known cardiovascular adverse events"
    result = agent.run(query)
    print(result.content)
    
if __name__ == "__main__":
    main()