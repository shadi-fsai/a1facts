import importlib
from enrichment.mcp_knowledge_source.query_agent import QueryAgent
from enrichment.knowledge_source import KnowledgeSource

class MCPKnowledgeSource(KnowledgeSource):    
    def __init__(self, source_config: dict):
        self.name = source_config['name']
        self.description = source_config['description']
        self.functions_file = source_config['functions_file']
        self.override_reliability = source_config['override_reliability']
        self.override_credibility = source_config['override_credibility']
        self.tools = []
        self.query_agent = None
        print("found me")
        exit()

    def query_tool(self):
        functions_module = importlib.import_module(f"{self.functions_file[:-3]}")
        for func_name in dir(functions_module):
            if func_name == "load_dotenv":
                continue
            if not func_name.startswith('_'):                
                func = getattr(functions_module, func_name)
                if callable(func):
                    self.tools.append(func)

        self.query_agent = QueryAgent(self.tools)

        def query_handler(query_text):
            return self.query_agent.query(query_text)

        query_handler.__name__ = self.name+"_query"
        query_handler.__doc__ = self.description + \
            "ARGS: query_text: str - The query text to query the knowledge source\n" + \
            "RETURNS: str - The response from the knowledge source\n" + \
            "Override reliability: " + self.override_reliability + "\n" + \
            "Override credibility: " + self.override_credibility
        return query_handler

    def __str__(self) -> str:
        return self.name + " - " + self.description + " - " + self.override_reliability + " - " + self.override_credibility + " - " + self.functions_file

