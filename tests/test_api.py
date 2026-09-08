"""
API Tests
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_destinations():
    """Test destinations endpoint"""
    response = client.get("/api/destinations")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_categories():
    """Test categories endpoint"""
    response = client.get("/api/destinations/categories/all")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data


def test_get_municipalities():
    """Test municipalities endpoint"""
    response = client.get("/api/destinations/municipalities/all")
    assert response.status_code == 200
    data = response.json()
    assert "municipalities" in data


def test_dashboard_summary():
    """Test dashboard summary"""
    response = client.get("/api/analytics/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_destinations" in data
    assert "total_reviews" in data


def test_sentiment_summary():
    """Test sentiment summary"""
    response = client.get("/api/mining/sentiment-summary")
    assert response.status_code == 200
    data = response.json()
    assert "positive" in data
    assert "neutral" in data
    assert "negative" in data


def test_clustering_status():
    """Test clustering status"""
    response = client.get("/api/mining/clustering/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data