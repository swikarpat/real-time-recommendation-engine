import requests
import pytest
from api.app.main import app
from fastapi.testclient import TestClient

# Use TestClient to simulate requests to your FastAPI application
client = TestClient(app)


def test_recommend_endpoint():
    """Test the /recommend endpoint."""
    user_id = 123
    response = client.post("/recommend", json={"user_id": user_id})

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    # Add more assertions to validate the response structure and content

    # Example: Check if the recommendations list is not empty
    assert len(data["recommendations"]) > 0

    # Example: Check the format of each recommendation
    for rec in data["recommendations"]:
        assert "product_id" in rec
        assert isinstance(rec["product_id"], int)
        assert "score" in rec
        assert isinstance(rec["score"], float)


# Add more tests for different scenarios, error handling, edge cases, etc.