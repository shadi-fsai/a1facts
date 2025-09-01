class KnowledgeSource:
    def __init__(self, name: str, reliability: str, credibility: str, api_url: str, api_doc_url: str, api_key: str):
        self.name = name
        self.reliability = reliability
        self.credibility = credibility
        self.api_url = api_url
        self.api_doc_url = api_doc_url
        self.api_key = api_key

    def query_tool(self):
        def query_handler(query_text):
            print(f"Querying {self.name} with query: {query_text}")
            return "No answer found"
        return query_handler

    def __str__(self) -> str:
        return self.name