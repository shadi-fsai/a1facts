import importlib
from a1facts.enrichment.function_knowledge_source.query_agent import QueryAgent
from a1facts.enrichment.knowledge_source import KnowledgeSource
from a1facts.utils.logger import logger

class FunctionKnowledgeSource(KnowledgeSource):
    def __init__(self, source_config: dict):
        self.name = source_config['name']
        self.description = source_config['description']
        self.functions_package = source_config['functions_package']
        self.override_reliability = source_config['override_reliability']
        self.override_credibility = source_config['override_credibility']
        self.tools = []
        self.query_agent = None
        logger.system(f"Initializing FunctionKnowledgeSource for {self.name}")
        self._validate_source_config(source_config)


    def _validate_source_config(self, source_config: dict):
        if 'name' not in source_config:
            raise ValueError("Your knowledge source config is missing the 'name' field")
        if 'description' not in source_config:
            raise ValueError("Your knowledge source config is missing the 'description' field")
        if 'functions_package' not in source_config:
            raise ValueError("Your knowledge source config is missing the 'functions_file' field")
        if 'override_reliability' not in source_config:
            raise ValueError("Your knowledge source config is missing the 'override_reliability' field")
        if 'override_credibility' not in source_config:
            raise ValueError("Your knowledge source config is missing the 'override_credibility' field")

    def query_tool(self):
        functions_module = importlib.import_module(f"{self.functions_package}")
        for func_name in dir(functions_module):
            logger.system(f"Checking function {func_name}")
            if func_name.startswith('__') and func_name.endswith('__'):
                continue
            if hasattr(getattr(functions_module, func_name), '__class__') and func_name[0].isupper():
                continue
            if func_name == "load_dotenv":
                continue
            if not func_name.startswith('_'):                
                func = getattr(functions_module, func_name)
                if callable(func):
                    logger.system(f"Adding function {func_name} to tools")
                    self.tools.append(func)
        logger.system(f"Tools for {self.name}: {self.tools}")
        self.query_agent = QueryAgent(self.tools)
        logger.system(f"Query agent for {self.name} initialized")
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

