from a1facts.utils.modelconfig import my_fast_language_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from colored import cprint
import yaml

class OntologyRewriteAgent:
    def __init__(self, ontology_yaml: str, mytools: list):
        self.ontology_yaml = ontology_yaml        
        self.agent = Agent(
            name="Ontology rewrite agent",
            role="Rewrite the query to use ontology",
            model=my_fast_language_model,
            tools=mytools,
            instructions=dedent("""
                Rewrite the query to use ontology.
                """),
                markdown=True,
                debug_mode=False,
            )
    
    def rewrite_query(self, text: str):
        #print(ontology)
        #cprint(query, 'yellow')
        with open(self.ontology_yaml, 'r') as file:
            ontology = yaml.load(file, Loader=yaml.FullLoader)
        prompt = dedent(f"""
            Rewrite the given text to be suitable for the ontology.
            Here is the ontology: {ontology}
            Here is the text to rewrite: {text}
            Only return the rewritten text, no other text.
            """
        )

        result = self.agent.run(prompt)
        #cprint(result.content, 'green')
        return result.content