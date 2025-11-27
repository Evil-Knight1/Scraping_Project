from models import LawUpdateRequest
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
import json
import os
from models import (
    SearchRequest,
    Website,
    LawUpdateRequest
)
from services import GoogleGeminiService
from database import init_db

app = FastAPI(title="Saudi Legal Scraper API")



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
        # elif len(target_domains) > 20:
        #     partial_sites = target_domains[:19]
        #     target_domains = partial_sites

        law_updates_prompt = service.get_updated_laws(
            date=request.date,
            domains=target_domains,
        )
        law_updates_result = service.generate_content(
            query=law_updates_prompt,
        )
        try:
            start_index = law_updates_result.find("{")
            end_index = law_updates_result.rfind("}")

            if start_index == -1 or end_index == -1 or start_index > end_index:
                # If we can't find the start/end of JSON, raise error with the full text
                raise json.JSONDecodeError(
                    "JSON start/end markers not found in response.",
                    law_updates_result,
                    0,
                )
            json_string = law_updates_result[start_index : end_index + 1]
            # The prompt instructs the model to return a specific JSON object
            law_updates_json = json.loads(json_string)
            # Ensure the required keys exist before returning
            return law_updates_json

        except json.JSONDecodeError as json_e:
            # Handle cases where the model returns non-JSON or malformed JSON
            print(
                f"JSON Decode Error in /law_updates: {json_e}. Raw text: {law_updates_result}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse model law updates result as JSON. Raw response: {law_updates_result}",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
