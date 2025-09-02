import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src')))

from colored import cprint
from a1c import A1C
from agno.agent import Agent
from textwrap import dedent
from utils.modelconfig import my_model

def main():
    a1c = A1C("a1c", "cookbook/example/company.yaml", "cookbook/example/sources.yaml")

    agent = Agent(
        name="finance_info_agent",
        role="get financial information about the company",
        model=my_model,
        tools=[a1c.get_tools()],
        instructions=dedent("""get financial information about the company"""),
        show_tool_calls=True,
        markdown=True,
        debug_mode=False,
    )
    query = "what do you know about how UnitedHealth competes with CVS?"
    result = agent.run(query)
    print(result.content)
    
if __name__ == "__main__":
    main()