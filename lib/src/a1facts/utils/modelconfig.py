from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

load_dotenv()

my_high_precision_model = OpenAIChat(id="gpt-4.1")
my_query_model = OpenAIChat(id="gpt-4.1")
my_fast_tool_calling_model = OpenAIChat(id="gpt-4.1-mini") #OpenAIChat(id="gpt-4.1")
my_fast_language_model = OpenAIChat(id="gpt-4.1-mini")
my_thinking_model = OpenAIChat(id="o3")