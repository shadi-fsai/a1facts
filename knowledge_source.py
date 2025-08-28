class knowledge_source:
    def __init__(self, name, reliability, credibility, api_url, api_doc_url, api_key):
        self.name = name
        self.reliability = reliability
        self.credibility = credibility
        self.api_url = api_url
        self.api_doc_url = api_doc_url
        self.api_key = api_key

    def query(self, query):
        return "query"

    def __str__(self):
        return self.name