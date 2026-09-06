"""Optional web search for evidence-based debate arguments."""

from __future__ import annotations

import os

import requests
from crewai.tools import BaseTool
from ddgs import DDGS
from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    query: str = Field(..., description="A focused claim or topic to verify on the web.")


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for current evidence relevant to the debate. "
        "Use it only for factual claims that may be outdated or need sources."
    )
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPER_API_KEY")
        if api_key:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": 4},
                timeout=10,
            )
            response.raise_for_status()
            results = response.json().get("organic", [])
            provider = "Serper"
            normalized = [(item.get("title", ""), item.get("link", ""), item.get("snippet", "")) for item in results]
        else:
            results = DDGS(timeout=10).text(query, max_results=4)
            provider = "DDGS"
            normalized = [(item.get("title", ""), item.get("href", ""), item.get("body", "")) for item in results]

        usable = [(title, url, snippet) for title, url, snippet in normalized if url]
        if not usable:
            return "No usable search results found."
        return "\n\n".join(f"[{provider}] {title}\n{snippet}\nURL: {url}" for title, url, snippet in usable)
