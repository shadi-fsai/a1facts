import sys
import os
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__),  '..', '..', 'src'))


from colored import cprint
from a1facts import KnowledgeBase
from agno.agent import Agent
from textwrap import dedent
from utils.modelconfig import my_model

def main():
    a1facts = KnowledgeBase("tests\\e2e\\a1facts", "tests\\e2e\\company.yaml", "tests\\e2e\\sources.yaml")
    
    agent = Agent(
        name="finance_info_agent",
        role="get financial information about the company",
        model=my_model,
        tools=a1facts.get_tools(),
        instructions=dedent("""get financial information about the company"""),
        show_tool_calls=True,
        markdown=True,
        debug_mode=False,
    )
    query = "what do you know about about Winnibago and how they make money?"
    result = agent.run(query)
    print(result.content)
    
if __name__ == "__main__":
    main()