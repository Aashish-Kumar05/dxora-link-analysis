import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_invalid_url_scheme():
    response = client.post("/link-analysis", json={"url": "ftp://example.com"})
    assert response.status_code == 400
    assert "Invalid URL scheme" in response.json()["detail"]


def test_ssrf_prevention_localhost():
    response = client.post("/link-analysis", json={"url": "http://localhost:8000"})
    assert response.status_code == 400
    assert "SSRF" in response.json()["detail"]


def test_ssrf_prevention_private_ip():
    response = client.post("/link-analysis", json={"url": "http://127.0.0.1:4000"})
    assert response.status_code == 400
    assert "SSRF" in response.json()["detail"]


def test_ssrf_prevention_metadata():
    response = client.post("/link-analysis", json={"url": "http://169.254.169.254/latest/meta-data"})
    assert response.status_code == 400
    assert "SSRF" in response.json()["detail"]


def test_link_analysis_success():
    # Test with real public site (example.com)
    response = client.post("/link-analysis", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()

    # Base structure
    assert data["success"] is True
    assert data["website"] == "https://example.com"
    assert "brand" in data
    assert "analysis" in data

    analysis = data["analysis"]

    # Section 1: Competitor Analysis
    assert "competitor_analysis" in analysis
    comp = analysis["competitor_analysis"]
    assert "brand_overview" in comp
    assert len(comp["competitors"]) >= 3
    for c in comp["competitors"]:
        assert "name" in c
        assert "main_service" in c
        assert "key_strength" in c
        assert "weakness_or_gap" in c

    # Section 2: Top 5 Target Search Queries
    assert "target_search_queries" in analysis
    queries = analysis["target_search_queries"]
    assert len(queries) == 5
    for q in queries:
        assert "query" in q
        assert "platforms" in q
        assert "intent" in q
        assert "business_relevance" in q
        assert "target_audience" in q

    # Section 3: SEO Improvements
    assert "seo_improvements" in analysis
    seo = analysis["seo_improvements"]
    assert "primary_keyword" in seo
    assert "recommended_title" in seo
    assert "meta_description" in seo
    assert len(seo["supporting_content"]) > 0

    # Section 4: Top 5 Services
    assert "top_services" in analysis
    services = analysis["top_services"]
    assert len(services) == 5
    for s in services:
        assert "service_name" in s
        assert "description" in s
        assert "target_industry" in s
        assert "target_customer" in s
        assert "main_benefit" in s
        assert "source" in s

    # Section 5: Target Audience Identification
    assert "target_audience" in analysis
    aud = analysis["target_audience"]
    assert "primary_audience" in aud
    assert "secondary_audience" in aud
    assert "industries" in aud
    assert "customer_needs" in aud
    assert "audience_segments" in aud
    assert len(aud["audience_segments"]) >= 3
