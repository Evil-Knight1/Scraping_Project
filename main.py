from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
import json
import os
from models import CrawlRequest, SearchRequest, Website, ExtractRequest
from services import FirecrawlService
from database import init_db

app = FastAPI(title="Saudi Legal Scraper API")


# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Dependency for service
def get_firecrawl_service():
    return FirecrawlService()


# Load websites
def get_websites() -> List[Website]:
    try:
        with open("websites.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Website(**item) for item in data]
    except Exception as e:
        print(f"Error loading websites: {e}")
        return []


@app.get("/websites", response_model=List[Website])
def list_websites():
    """List all supported Saudi legal websites."""
    return get_websites()


@app.post("/crawl")
def crawl_endpoint(
    request: CrawlRequest, service: FirecrawlService = Depends(get_firecrawl_service)
):
    """
    Crawl a website.
    Uses Firecrawl API.
    Checks cache first to save quota.
    """
    try:
        result = service.crawl(
            url=request.url,
            crawler_options=request.crawlerOptions,
            page_options=request.pageOptions,
            force_refresh=request.force_refresh,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract")
def extract_endpoint(
    request: ExtractRequest, service: FirecrawlService = Depends(get_firecrawl_service)
):
    """
    Extract data from a website.
    Uses Firecrawl API.
    Checks cache first to save quota.
    """
    try:
        result = service.extract(
            url=request.url,
            prompt=request.prompt,
            schema=request.schema,
            enable_web_search=request.enable_web_search,
            show_sources=request.show_sources,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
def search_endpoint(
    request: SearchRequest, service: FirecrawlService = Depends(get_firecrawl_service)
):
    """
    Search for a query.
    Uses Firecrawl API.
    Checks cache first to save quota.
    """
    try:
        result = service.search(
            query=request.query,
        )
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
