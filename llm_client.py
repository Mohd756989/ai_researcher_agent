"""
Shared LLM client used by all agents.
"""
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL

llm = ChatGroq(
    model=LLM_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY,
)

class Solution:
    def get_info():
        return "hello world"