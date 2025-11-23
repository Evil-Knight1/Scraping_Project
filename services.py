import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from firecrawl import FirecrawlApp
from database import (
    get_cached_crawl,
    save_crawl_result,
    get_cached_search,
    save_search_result,
)

load_dotenv()


class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            # We'll allow it to be None for testing/mocking, but warn
            print("Warning: FIRECRAWL_API_KEY not found in environment variables.")
        self.app: FirecrawlApp = FirecrawlApp(api_key=api_key)

    def search(
        self,
        query: str,
        limit: Optional[int] = 10,
    ) -> Dict[str, Any]:
        results = self.app.search(
            query,
            limit=limit,
        )
        return results

    def extract(self, url: str) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {"description": {"type": "string"}},
            "required": ["description"],
        }

        res = self.app.extract(
            urls=[url],
            prompt="Extract relevant legal information from these pages: laws, regulations, article numbers, effective dates, penalties, definitions, and any PDF-linked legal documents. Also, if there are downloadable PDF files, extract their text content.",
            schema=schema,
        )
        return res
