import pytest
import requests
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.llm_classifier import LLMClassifier, LLMClassificationResult
from backend.rag_loader import RegulationRAG

client = TestClient(app)

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """Test successful login"""
        response = client.post("/token", data={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_failure(self):
        """Test failed login"""
        response = client.post("/token", data={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.post("/classify", json={
            "title": "Test Feature",
            "description": "Test description"
        })
        assert response.status_code == 401

class TestClassification:
    """Test classification functionality"""
    
    def test_single_classification_with_auth(self):
        """Test single feature classification with authentication"""
        # First login
        login_response = client.post("/token", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Test classification
        response = client.post("/classify", 
            json={"title": "Age Verification System", "description": "System to verify user age"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "needs_geo_logic" in data
        assert "reasoning" in data
        assert "regulations" in data
        assert "confidence" in data
        assert "risk_level" in data
        assert "specific_requirements" in data
    
    def test_classification_edge_cases(self):
        """Test classification with edge cases"""
        login_response = client.post("/token", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Test with empty strings
        response = client.post("/classify",
            json={"title": "", "description": ""},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Test with very long text
        long_text = "x" * 1000
        response = client.post("/classify",
            json={"title": long_text, "description": long_text},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

class TestRAGSystem:
    """Test RAG system functionality"""
    
    def test_rag_initialization(self):
        """Test RAG system initialization"""
        rag = RegulationRAG()
        assert rag is not None
        assert rag.regulations_dir == "regulations"
    
    def test_regulation_loading(self):
        """Test regulation loading"""
        rag = RegulationRAG()
        regulations = rag.load_regulations()
        assert len(regulations) > 0
        assert all("name" in reg for reg in regulations)
        assert all("content" in reg for reg in regulations)
    
    def test_search_functionality(self):
        """Test RAG search functionality"""
        rag = RegulationRAG()
        rag.build_index()
        results = rag.search("age verification", k=3)
        assert len(results) > 0
        assert all("relevance_score" in result for result in results)

class TestLLMClassifier:
    """Test LLM classifier functionality"""
    
    def test_classifier_initialization(self):
        """Test LLM classifier initialization"""
        classifier = LLMClassifier()
        assert classifier is not None
        assert classifier.model == "gpt-4o-mini"
    
    def test_mock_classification(self):
        """Test mock classification fallback"""
        classifier = LLMClassifier()
        result = classifier._mock_classification(
            "Age Verification System",
            "System to verify user age during registration"
        )
        assert isinstance(result, LLMClassificationResult)
        assert result.needs_geo_logic in [True, False]
        assert 0 <= result.confidence <= 1
        assert result.risk_level in ["low", "medium", "high"]

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_regulations_endpoint(self):
        """Test regulations endpoint"""
        login_response = client.post("/token", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/regulations", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "regulations" in data
        assert "count" in data
        assert data["count"] > 0
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        login_response = client.post("/token", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/stats", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total_classifications" in data
        assert "compliance_required" in data
        assert "no_compliance_needed" in data
        assert "average_confidence" in data
        assert "risk_levels" in data

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting(self):
        """Test rate limiting (this would need more sophisticated testing in production)"""
        # This is a basic test - in production you'd want to test actual rate limiting
        login_response = client.post("/token", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Make multiple requests to test rate limiting
        for i in range(5):
            response = client.post("/classify",
                json={"title": f"Test Feature {i}", "description": "Test description"},
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should succeed for reasonable number of requests
            assert response.status_code in [200, 429]

if __name__ == "__main__":
    pytest.main([__file__])
