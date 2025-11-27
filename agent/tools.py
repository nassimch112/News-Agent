import os
from typing import Any, Callable, List

from firecrawl import FirecrawlApp
from firecrawl.v2.types import Document, SearchData

class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    def run(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description
        }

class SearchTool(Tool):
    def __init__(self):
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            print("DEBUG: FIRECRAWL_API_KEY is missing!")
        else:
            print(f"DEBUG: FIRECRAWL_API_KEY found: {api_key[:4]}...")

        self.app = FirecrawlApp(api_key=api_key)
        super().__init__(
            name="search",
            description="Useful for searching the internet. Returns search results with content snippets.",
            func=self.search
        )

    def _collect_items(self, results: SearchData) -> List[Any]:
        """Normalize Firecrawl search results into a list of entries."""
        items: List[Any] = []
        if getattr(results, "web", None):
            items.extend(results.web)
        if getattr(results, "news", None):
            items.extend(results.news)
        if getattr(results, "images", None):
            items.extend(results.images)
        return items

    def search(self, query: str) -> str:
        try:
            results = self.app.search(query, limit=5)
            print(f"DEBUG: Firecrawl Raw Results: {results}")

            # Firecrawl returns a SearchData object; fall back to legacy structures if needed
            if isinstance(results, SearchData):
                items = self._collect_items(results)
            elif isinstance(results, list):
                items = results
            elif isinstance(results, dict) and 'data' in results:
                items = results['data']
            else:
                try:
                    items = list(results)
                except TypeError:
                    return f"No results found or unknown format: {type(results)}"

            if not items:
                return "No results found."

            output = []
            for item in items[:3]:  # Limit to top 3
                if isinstance(item, dict):
                    title = item.get('title', 'No Title')
                    url = item.get('url', 'No URL')
                    content = item.get('description') or item.get('markdown') or ''
                else:
                    title = getattr(item, 'title', 'No Title')
                    url = getattr(item, 'url', 'No URL')
                    content = getattr(item, 'description', '') or getattr(item, 'markdown', '')

                snippet = (content or '').strip()
                if len(snippet) > 400:
                    snippet = snippet[:400] + "..."
                output.append(f"Title: {title}\nURL: {url}\nContent: {snippet}\n---")

            return "\n".join(output)
        except Exception as e:
            print(f"DEBUG: Firecrawl Error: {e}")
            return f"Error searching with Firecrawl: {e}"

class ScrapeTool(Tool):
    def __init__(self):
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            print("DEBUG: FIRECRAWL_API_KEY is missing!")
        self.app = FirecrawlApp(api_key=api_key)
        super().__init__(
            name="scrape",
            description="Useful for scraping the full content of a specific webpage. Input should be a URL.",
            func=self.scrape
        )

    def scrape(self, url: str) -> str:
        try:
            document: Document = self.app.scrape(
                url,
                formats=['markdown'],
                only_main_content=True,
            )

            markdown = getattr(document, 'markdown', None)
            if not markdown and isinstance(document, dict):
                markdown = document.get('markdown')

            if markdown:
                markdown = markdown.strip()
                return markdown[:5000] + "..." if len(markdown) > 5000 else markdown

            return "Error: No markdown content returned by Firecrawl."
        except Exception as e:
            print(f"DEBUG: Firecrawl scrape error: {e}")
            return f"Error scraping with Firecrawl: {e}"
