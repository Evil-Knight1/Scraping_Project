from models import LawUpdateRequest
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
import json
import os
from models import (
    SearchRequest,
    Website,
)
from services import GoogleGeminiService
from database import init_db

app = FastAPI(title="Saudi Legal Scraper API")


# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Dependency for service
def get_google_gemini_service():
    return GoogleGeminiService()


# Load websites
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


# @app.get("/law_updates"):
#     def get_law_updates():
#         return get_websites()


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
        print(target_domains)
        print(request.query)
        search_prompt = service.search(
            query=request.query,
            domains=target_domains,
        )
        print(f"search_prompt: {search_prompt}")
        search_result = service.generate_content(
            query=search_prompt,
        )
        splited_results = search_result.split("sources")
        print(f"ANSWER: {splited_results}")
        return {"response": splited_results[0], "sources": splited_results[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/law_updates")
def get_law_updates(
    request: LawUpdateRequest,
    service: GoogleGeminiService = Depends(get_google_gemini_service),
):
    try:
        # If domains are not provided in request, load default list from JSON
        target_domains = request.domains
        if not target_domains:
            all_sites = get_websites()
            target_domains = [site.url for site in all_sites]
        print(target_domains)
        print(request.date)
        law_updates_prompt = service.get_updated_laws(
            date=request.date,
            domains=target_domains,
        )
        print(f"law_updates_prompt: {law_updates_prompt}")
        law_updates_result = service.generate_content(
            query=law_updates_prompt,
        )
        return law_updates_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
