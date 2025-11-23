from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CrawlRequest(BaseModel):
    url: str
    crawlerOptions: Optional[Dict[str, Any]] = None
    pageOptions: Optional[Dict[str, Any]] = None
    force_refresh: bool = False

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
