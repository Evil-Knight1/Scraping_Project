from http.client import HTTPException
import json
from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List
import os
from firecrawl_service import FireCrawlService
from google_gemini_service import GoogleGeminiService
from models import SearchRequest, SearchRequest, Website

app = FastAPI()


def get_google_gemini_service():
    return GoogleGeminiService()


def get_fire_crawl_service():
    return FireCrawlService()


def get_websites() -> List[Website]:
    try:
        with open("websites.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Website(**item) for item in data]
    except Exception as e:
        print(f"Error loading websites: {e}")
        return []


@app.post("/websites", response_model=List[Website])
def list_websites(request: List[Website]):
    """List all supported Saudi legal websites."""
    return get_websites()


@app.get("/scrap_all")
def scrap_all(
    service: FireCrawlService = Depends(get_fire_crawl_service),
):
    """
    Scrape all websites listed in websites.json.
    """
    all_sites = get_websites()
    target_domains = [url for site in all_sites for url in site.paths]
    result = service.batch_scrape(target_domains)
    return result


@app.get("/scrap_status/{job_id}")
def scrap_status(
    job_id: str,
    service: FireCrawlService = Depends(get_fire_crawl_service),
):
    """
    Get the status and results of a Firecrawl batch scrape job.
    """
    result = service.get_scrap_id(job_id)
    return result


@app.post("/search")
def search_endpoint(
    request: SearchRequest,
    service: GoogleGeminiService = Depends(get_google_gemini_service),
):
    """
    Search for a query using Gemini Grounding.
    1. Answers the question.
    2. Checks for legal updates.
    """
    try:
        # If domains are not provided in request, load default list from JSON
        target_domains = request.domains
        if not target_domains:
            all_sites = get_websites()
            target_domains = [site.url for site in all_sites]

        search_prompt = service.search(
            query=request.query,
            domains=target_domains,
        )
        search_result = service.generate_content(
            query=search_prompt,
        )
        print(search_result)
        try:
            start_index = search_result.find("{")
            end_index = search_result.rfind("}")

            if start_index == -1 or end_index == -1 or start_index > end_index:
                # If we can't find the start/end of JSON, raise error with the full text
                raise json.JSONDecodeError(
                    "JSON start/end markers not found in response.",
                    search_result,
                    0,
                )
            json_string = search_result[start_index : end_index + 1]

            # The prompt instructs the model to return a specific JSON object
            search_json = json.loads(json_string)

            # Ensure the required keys exist before returning
            return search_json

        except json.JSONDecodeError as json_e:
            # Handle cases where the model returns non-JSON or malformed JSON
            print(f"JSON Decode Error in /search: {json_e}. Raw text: {search_result}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse model search result as JSON. Raw response: {search_result}",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape")
def scrape_website(
    request: str, service: FireCrawlService = Depends(get_fire_crawl_service)
):
    result = service.scrape_website(request)
    return result
    """Scrape a given website URL."""


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
