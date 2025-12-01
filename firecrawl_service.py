import time
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

    def watch_scrape_status(self, job_id: str):
        """Poll Firecrawl manually until the job is completed or failed."""
        print(f"Starting to watch job: {job_id}")

        while True:
            # 1. Get the current status
            # Note: Ensure get_batch_scrape_status is the correct method name for your SDK version.
            # It might be self.client.check_batch_scrape_status(job_id) depending on version.
            response = self.client.get_batch_scrape_status(job_id)

            # 2. Extract status
            # The structure depends on API version, usually response['status']
            status = response.status

            print(f"Current Job Status: {status}")

            # 3. Check if done
            if status == "completed":
                self.notify_user(response)
                return response
            elif status == "scraping ":
                print("Job still in progress...")
            elif status == "failed":
                print("Job failed.")
                self.notify_user(response)
                return response

            # 4. Wait before checking again (Poling)
            time.sleep(2)

    def notify_user(self, result):
        # TODO: integrate your preferred method
        print("Scraping finished!")
        print(result)

        # Example:
        # send_email(...)
        # send_telegram(...)
        # write_to_db(...)
        # websocket_push(...)
