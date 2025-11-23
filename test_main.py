from fastapi.testclient import TestClient
from main import app, get_firecrawl_service
from services import FirecrawlService
from unittest.mock import MagicMock

client = TestClient(app)

# Mock the service
def get_mock_service():
    mock = MagicMock(spec=FirecrawlService)
    mock.crawl.return_value = {"status": "success", "data": [{"url": "http://example.com"}]}
    mock.search.return_value = {"status": "success", "data": [{"url": "http://example.com"}]}
    return mock

app.dependency_overrides[get_firecrawl_service] = get_mock_service

def test_read_websites():
    response = client.get("/websites")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == "R1"

def test_crawl_endpoint():
    response = client.post("/crawl", json={"url": "https://uqn.gov.sa"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_search_endpoint():
    response = client.post("/search", json={"query": "law"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
