"""
Web search tool backed by Tavily.

The original notebook had a bug: it called `results.search(...)` on the
dict returned by `client.search(...)`, which doesn't exist. Fixed here to
just read the `results` key from the response dict.
"""
from tavily import TavilyClient
from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Run a web search and return a list of result dicts with
    'title', 'url', and 'content' keys."""
    response = client.search(
        query=query,
        search_depth="basic",
        max_results=max_results,
    )
    return response.get("results", [])
