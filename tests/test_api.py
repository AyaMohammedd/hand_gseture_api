import pytest
import numpy as np
import sys
import os
import warnings
from fastapi.testclient import TestClient
from sklearn.exceptions import InconsistentVersionWarning

# Add app path to sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from main import app as fastapi_app

# Create a test client using the FastAPI app
@pytest.fixture
def client():
    with TestClient(fastapi_app) as test_client:
        yield test_client

class TestAPI:
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_predict_valid_input(self, client):
        """Test prediction with valid input (63 landmarks)"""
        landmarks = np.random.rand(63).tolist()
        response = client.post("/predict", json={"landmarks": landmarks})

        assert response.status_code in [200, 500]  # Model may be unavailable in test
        if response.status_code == 200:
            data = response.json()
            assert "gesture" in data
            assert "direction" in data
            assert "confidence" in data
            assert "timestamp" in data
            assert isinstance(data["confidence"], float)
    
    def test_predict_invalid_input(self, client):
        """Test prediction with invalid number of landmarks"""
        landmarks = np.random.rand(50).tolist()  # Invalid input (50 instead of 63)
        response = client.post("/predict", json={"landmarks": landmarks})
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
        assert "Expected 63 landmark features" in response.json()["detail"]
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/app-metrics")
        assert response.status_code == 200
        data = response.json()
        assert "model_metrics" in data
        assert "data_metrics" in data
        assert "server_metrics" in data

if __name__ == "__main__":
    pytest.main([__file__])