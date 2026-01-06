"""
Unit tests for utility functions
"""
import pytest
from utils.amount_utils import parse_amount, format_currency
from utils.transliteration import needs_transliteration, is_indian_language


class TestAmountUtils:
    """Test amount parsing and formatting utilities"""
    
    def test_parse_basic_amount(self):
        """Test basic amount parsing"""
        assert parse_amount("1000000") == 1000000
        assert parse_amount("1,000,000") == 1000000
    
    def test_parse_with_currency_symbols(self):
        """Test parsing with currency symbols"""
        assert parse_amount("$1000") == 1000
        assert parse_amount("₹1000") == 1000
        assert parse_amount("€1000") == 1000
    
    def test_parse_indian_notation(self):
        """Test parsing Indian number notation"""
        assert parse_amount("10,00,000") == 1000000  # 10 lakhs
        assert parse_amount("1,00,00,000") == 10000000  # 1 crore
    
    def test_parse_decimal_amounts(self):
        """Test decimal amounts"""
        assert parse_amount("1000.50") == 1000.50
        assert parse_amount("1,000.50") == 1000.50
    
    def test_parse_invalid_amount(self):
        """Test invalid amount handling"""
        assert parse_amount("invalid") is None
        assert parse_amount("") is None
        assert parse_amount(None) is None
    
    def test_format_currency_usd(self):
        """Test USD formatting"""
        assert format_currency(1000000, "USD") == "$1,000,000"
        assert format_currency(1500.50, "USD") == "$1,500.50"
    
    def test_format_currency_inr(self):
        """Test INR formatting"""
        # Should use Indian notation
        result = format_currency(1000000, "INR")
        assert "₹" in result
        assert "10" in result  # 10 lakhs or similar


class TestTransliteration:
    """Test transliteration utilities"""
    
    def test_needs_transliteration_english(self):
        """Test English text doesn't need transliteration"""
        assert needs_transliteration("Hello World", "en") is False
        assert needs_transliteration("Startup funding", "en") is False
    
    def test_needs_transliteration_hindi(self):
        """Test Hindi text needs transliteration"""
        assert needs_transliteration("नमस्ते", "hi") is True
        assert needs_transliteration("फिनटेक", "hi") is True
    
    def test_needs_transliteration_mixed(self):
        """Test mixed content detection"""
        # Mix of English and Hindi
        mixed = "Hello नमस्ते"
        result = needs_transliteration(mixed, "hi")
        # Should detect Hindi characters
        assert result is True
    
    def test_is_indian_language(self):
        """Test Indian language detection"""
        assert is_indian_language("hi") is True  # Hindi
        assert is_indian_language("te") is True  # Telugu
        assert is_indian_language("ta") is True  # Tamil
        assert is_indian_language("en") is False  # English
        assert is_indian_language("fr") is False  # French
    
    def test_transliteration_threshold(self):
        """Test transliteration threshold logic"""
        # Mostly English with few Hindi words
        text = "The फिनटेक startup in दिल्ली raised funding"
        # Implementation depends on threshold
        # This is a design decision test
