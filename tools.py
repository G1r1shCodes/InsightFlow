from crewai.tools import tool
from crewai_tools import SerperDevTool
import os

# Option 1: Built-in SerperDev tool (recommended - 2500 free searches)
# Sign up at https://serper.dev/ and set SERPER_API_KEY in .env
serper_api_key = os.getenv("SERPER_API_KEY")

if serper_api_key:
    search_tool = SerperDevTool()
else:
    # Fallback: a dummy tool that uses LLM's own knowledge
    @tool("web_search")
    def search_tool(query: str) -> str:
        """Search the web for information about companies, markets, and business news."""
        return (
            f"[Web search unavailable - no SERPER_API_KEY configured] "
            f"Please use your own knowledge to answer the query: {query}"
        )