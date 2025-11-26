from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    query: str
    domains: Optional[List[str]] = None


class LawUpdateRequest(BaseModel):
    date: str
    domains: Optional[List[str]] = None


class Website(BaseModel):
    id: str
    category: str
    name: str
    authority: str
    description: str
    url: str
