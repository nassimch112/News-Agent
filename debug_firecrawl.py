from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv

load_dotenv()

def test_firecrawl():
    app = FirecrawlApp(api_key=os.environ.get("FIRECRAWL_API_KEY"))
    try:
        # Try without params first
        print("Testing search without params...")
        res = app.search("test", limit=5)
        print(f"Result type: {type(res)}")
        print(f"Result content: {res}")

        print("Testing scrape...")
        doc = app.scrape("https://example.com", formats=["markdown"], only_main_content=True)
        markdown = getattr(doc, "markdown", None)
        print(f"Scrape type: {type(doc)}")
        print(f"Markdown length: {len(markdown or '')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_firecrawl()
