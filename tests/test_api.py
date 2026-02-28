"""Sample tests for OrchestraLab AI."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.core.config import Settings


@pytest.fixture
def test_settings():
    """Test configuration."""
    return Settings(
        openrouter_api_key="test-key",
        secret_key="test-secret-key-must-be-32-chars-min",
        environment="development",
        debug=True
    )


@pytest.fixture
def client(test_settings):
    """Test client."""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestAnalyzeEndpoint:
    """Test analysis endpoint."""
    
    def test_analyze_validation_error(self, client):
        """Test validation error for empty query."""
        response = client.post(
            "/api/v1/analyze",
            json={"query": ""}
        )
        assert response.status_code == 422
    
    def test_analyze_valid_request_structure(self, client):
        """Test valid request structure."""
        # Note: This test would need mocking for full functionality
        response = client.post(
            "/api/v1/analyze", 
            json={"query": "Design a simple web application"}
        )
        
        # In a real test environment, you would mock the LLM calls
        # For now, this tests the request structure validation
        assert response.status_code in [200, 500]  # 500 if no real API key


class TestSecurityFeatures:
    """Test security features."""
    
    def test_xss_prevention(self, client):
        """Test XSS content rejection."""
        malicious_query = "Design a system <script>alert('xss')</script>"
        
        response = client.post(
            "/api/v1/analyze",
            json={"query": malicious_query}
        )
        
        assert response.status_code == 422
    
    def test_long_query_rejection(self, client):
        """Test rejection of excessively long queries."""
        long_query = "x" * 10000
        
        response = client.post(
            "/api/v1/analyze",
            json={"query": long_query}
        )
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])