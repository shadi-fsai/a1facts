from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

load_dotenv()

my_model = OpenAIChat(id="gpt-4.1")
my_query_model = OpenAIChat(id="gpt-4.1")
