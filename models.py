from pydantic import BaseModel
from typing import Optional, List


class Website(BaseModel):
    id: str
    category: str
    name: str
    authority: str
    description: str
    url: str
    paths: List[str]


class SearchRequest(BaseModel):
    query: str
    domains: Optional[List[str]] = None
    mode: Optional[bool] = False
