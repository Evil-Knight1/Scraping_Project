from typing import Optional, List, Dict
from firecrawl import Firecrawl
from dotenv import load_dotenv
import os
import re

load_dotenv()


class FireCrawlService:
    def __init__(self):
        self.api_key = os.environ.get("FIRE_CRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRE_CRAWL_API_KEY environment variable not set")

        self.client: Firecrawl = Firecrawl(api_key=self.api_key)

    def scrape_website(self, url: str) -> List[Dict]:
        """
        Scrape website with structured extraction.
        Returns organized structured legal updates.
        """
        response = self.client.scrape(
            url,
            formats=[
                {
                    "type": "json",
                    "prompt": (
                        "Extract all legal updates, regulations, circulars, "
                        "constitutional amendments, and any law modifications "
                        "from the website content. Only include official updates."
                    ),
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "date": {"type": "string"},
                                "summary": {"type": "string"},
                            },
                            "required": ["title", "url", "date"],
                        },
                    },
                }
            ],
            only_main_content=True,
        )

        json_content = response.dict().get("json", "")
        print(response.dict())
        return json_content

    def batch_scrape(self, urls: Optional[List[str]] = None):
        """
        Start a Firecrawl batch scrape job.
        """
        if not urls:
            return "No URLs provided."
        self.domain_context(urls)
        response = self.client.start_batch_scrape(
            urls,
            formats=[
                {
                    "type": "json",
                    "prompt": (
                        "Extract all legal updates, regulations, circulars, "
                        "constitutional amendments, and any law modifications "
                        "from the website content. Only include official updates."
                    ),
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "date": {"type": "string"},
                                "summary": {"type": "string"},
                            },
                            "required": ["title", "url", "date"],
                        },
                    },
                }
            ],
            only_main_content=True,
        )
        return response

    def get_scrap_id(self, job_id: str):
        """
        Get the status and results of a Firecrawl batch scrape job.
        """
        response = self.client.get_batch_scrape_status(job_id)
        return response

    def domain_context(self, domains: List[str]):
        domain_list = ", ".join(domains)
        return domain_list
