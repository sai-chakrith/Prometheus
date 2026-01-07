"""
Integration tests for RAG service
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import database as db


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user():
    """Create test user"""
    db.create_user("testuser", "test@example.com", "password123")
    yield "testuser"
    # Cleanup
    # Note: Add cleanup logic here


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_signup_success(self, client):
        """Test successful user signup"""
        response = client.post("/signup", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
    
    def test_signup_duplicate_username(self, client, test_user):
        """Test signup with duplicate username"""
        response = client.post("/signup", json={
            "username": test_user,
            "email": "different@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post("/login", json={
            "username": test_user,
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post("/login", json={
            "username": test_user,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post("/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == 401


class TestRAGEndpoint:
    """Test RAG query endpoint"""
    
    def test_rag_query_without_auth(self, client):
        """Test RAG query without authentication"""
        response = client.post("/rag", json={
            "query": "What are top fintech startups?"
        })
        # Should either work without auth or return 401
        assert response.status_code in [200, 401]
    
    def test_rag_query_with_auth(self, client, test_user):
        """Test RAG query with authentication"""
        # Login first
        login_response = client.post("/login", json={
            "username": test_user,
            "password": "password123"
        })
        session_id = login_response.json()["session_id"]
        
        # Make RAG query
        response = client.post(
            "/rag",
            json={"query": "What are top fintech startups?"},
            headers={"X-Session-Id": session_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_rag_query_invalid_input(self, client):
        """Test RAG query with invalid input"""
        response = client.post("/rag", json={
            "query": "hi"  # Too short
        })
        assert response.status_code == 422  # Validation error
    
    def test_rag_query_empty(self, client):
        """Test RAG query with empty query"""
        response = client.post("/rag", json={
            "query": ""
        })
        assert response.status_code == 422


class TestChatHistoryEndpoints:
    """Test chat history endpoints"""
    
    def test_get_history_without_auth(self, client):
        """Test getting history without auth"""
        response = client.get("/history")
        assert response.status_code == 401
    
    def test_save_chat(self, client, test_user):
        """Test saving chat to history"""
        # Login
        login_response = client.post("/login", json={
            "username": test_user,
            "password": "password123"
        })
        session_id = login_response.json()["session_id"]
        
        # Save chat
        response = client.post(
            "/save-chat",
            json={
                "query": "Test query",
                "response": "Test response",
                "session_id": session_id
            },
            headers={"X-Session-Id": session_id}
        )
        assert response.status_code == 200


class TestFeedbackEndpoint:
    """Test feedback endpoints"""
    
    def test_submit_feedback(self, client):
        """Test submitting feedback"""
        response = client.post("/feedback", json={
            "query": "Test query",
            "response": "Test response",
            "rating": 5,
            "comment": "Great response!"
        })
        assert response.status_code == 200
    
    def test_submit_feedback_invalid_rating(self, client):
        """Test feedback with invalid rating"""
        response = client.post("/feedback", json={
            "query": "Test query",
            "response": "Test response",
            "rating": 6  # Invalid, must be 1-5
        })
        assert response.status_code == 422
