"""
Central configuration. Loads API keys from environment variables / .env file.
NEVER hardcode API keys in source files.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not set. Create a .env file (see .env.example) or set it as an environment variable."
    )
if not TAVILY_API_KEY:
    raise EnvironmentError(
        "TAVILY_API_KEY not set. Create a .env file (see .env.example) or set it as an environment variable."
    )
