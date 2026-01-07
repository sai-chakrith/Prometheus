"""
Unit tests for Prometheus validators
"""
import pytest
from pydantic import ValidationError
from validators import (
    RagRequestValidated,
    SignupRequestValidated,
    SaveChatRequestValidated,
    LoginRequest,
    FeedbackRequest
)


class TestRagRequestValidator:
    """Test RAG request validation"""
    
    def test_valid_query(self):
        """Test valid query passes validation"""
        data = {"query": "What are top fintech startups?"}
        request = RagRequestValidated(**data)
        assert request.query == "What are top fintech startups?"
    
    def test_query_too_short(self):
        """Test query length validation"""
        with pytest.raises(ValidationError) as exc_info:
            RagRequestValidated(query="hi")
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_query_too_long(self):
        """Test maximum query length"""
        long_query = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            RagRequestValidated(query=long_query)
        assert "exceed 1000 characters" in str(exc_info.value)
    
    def test_empty_query(self):
        """Test empty query rejection"""
        with pytest.raises(ValidationError):
            RagRequestValidated(query="")
    
    def test_whitespace_only_query(self):
        """Test whitespace-only query rejection"""
        with pytest.raises(ValidationError):
            RagRequestValidated(query="   ")
    
    def test_query_with_special_characters(self):
        """Test query with special characters"""
        query = "What's the funding for AI/ML startups in 2024?"
        request = RagRequestValidated(query=query)
        assert request.query == query
    
    def test_optional_language(self):
        """Test language parameter"""
        request = RagRequestValidated(query="Test query", language="hi")
        assert request.language == "hi"


class TestSignupRequestValidator:
    """Test signup request validation"""
    
    def test_valid_signup(self):
        """Test valid signup data"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        request = SignupRequestValidated(**data)
        assert request.username == "testuser"
        assert request.email == "test@example.com"
    
    def test_invalid_email(self):
        """Test email validation"""
        with pytest.raises(ValidationError):
            SignupRequestValidated(
                username="testuser",
                email="invalid-email",
                password="SecurePass123!"
            )
    
    def test_username_too_short(self):
        """Test username length validation"""
        with pytest.raises(ValidationError):
            SignupRequestValidated(
                username="ab",
                email="test@example.com",
                password="SecurePass123!"
            )
    
    def test_password_too_short(self):
        """Test password length validation"""
        with pytest.raises(ValidationError):
            SignupRequestValidated(
                username="testuser",
                email="test@example.com",
                password="short"
            )
    
    def test_username_with_invalid_chars(self):
        """Test username character validation"""
        with pytest.raises(ValidationError):
            SignupRequestValidated(
                username="test user!",
                email="test@example.com",
                password="SecurePass123!"
            )


class TestSaveChatRequestValidator:
    """Test chat save request validation"""
    
    def test_valid_chat(self):
        """Test valid chat data"""
        data = {
            "query": "What are top startups?",
            "response": "Here are the top startups..."
        }
        request = SaveChatRequestValidated(**data)
        assert request.query == data["query"]
        assert request.response == data["response"]
    
    def test_optional_session_id(self):
        """Test optional session_id"""
        request = SaveChatRequestValidated(
            query="Test",
            response="Response",
            session_id="session-123"
        )
        assert request.session_id == "session-123"
    
    def test_empty_response(self):
        """Test empty response rejection"""
        with pytest.raises(ValidationError):
            SaveChatRequestValidated(
                query="Test query",
                response=""
            )


class TestLoginRequest:
    """Test login request validation"""
    
    def test_valid_login(self):
        """Test valid login credentials"""
        request = LoginRequest(
            username="testuser",
            password="password123"
        )
        assert request.username == "testuser"
    
    def test_empty_username(self):
        """Test empty username rejection"""
        with pytest.raises(ValidationError):
            LoginRequest(username="", password="password123")
    
    def test_empty_password(self):
        """Test empty password rejection"""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser", password="")


class TestFeedbackRequest:
    """Test feedback request validation"""
    
    def test_valid_feedback(self):
        """Test valid feedback"""
        request = FeedbackRequest(
            query="Test query",
            response="Test response",
            rating=5,
            comment="Great!"
        )
        assert request.rating == 5
    
    def test_rating_bounds(self):
        """Test rating must be 1-5"""
        with pytest.raises(ValidationError):
            FeedbackRequest(
                query="Test",
                response="Response",
                rating=6
            )
        
        with pytest.raises(ValidationError):
            FeedbackRequest(
                query="Test",
                response="Response",
                rating=0
            )
    
    def test_optional_comment(self):
        """Test comment is optional"""
        request = FeedbackRequest(
            query="Test",
            response="Response",
            rating=4
        )
        assert request.comment is None
