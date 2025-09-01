from agno.agent import Agent
from datetime import datetime
from textwrap import dedent
from agno.tools.exa import ExaTools
from agno.models.openai import OpenAIChat
from agno.models.groq import Groq
from dotenv import load_dotenv
from agno.tools import tool

#from agno.models.google import Gemini

load_dotenv()

my_model = OpenAIChat(id="gpt-4.1")
my_query_model = OpenAIChat(id="gpt-4.1")
my_fast_model = Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct")#Gemini(id="gemini-2.5-flash")#OpenAIChat(id="gpt-4.1-mini")
