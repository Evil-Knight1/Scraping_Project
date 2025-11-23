from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CrawlRequest(BaseModel):
    url: str
    crawlerOptions: Optional[Dict[str, Any]] = None
    pageOptions: Optional[Dict[str, Any]] = None
    force_refresh: bool = False


class ExtractRequest(BaseModel):
    """Link for docs:
    https://docs.firecrawl.dev/api-reference/endpoint/extract
    """

    urls: List[str]
    prompt: str = (
        "Extract relevant legal information from these pages: laws, regulations, article numbers, effective dates, penalties, definitions, and any PDF-linked legal documents. Also, if there are downloadable PDF files, extract their text content."
    )
    schema: Dict[str, Any]
    enable_web_search: bool = (
        False  # When true, the extraction will use web search to find additional data
    )
    show_sources: bool = True


class SearchRequest(BaseModel):
    query: str
    searchOptions: Optional[Dict[str, Any]] = None
    pageOptions: Optional[Dict[str, Any]] = None
    force_refresh: bool = False


class Website(BaseModel):
    id: str
    category: str
    name: str
    authority: str
    description: str
    baseUrl: str
