"""
Translation Service - Enhanced multilingual support
"""
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating text between languages"""
    
    def __init__(self):
        self.translator = None
        self.enabled = False
        self._initialize()
    
    def _initialize(self):
        """Initialize translation service"""
        try:
            from googletrans import Translator
            self.translator = Translator()
            self.enabled = True
            logger.info("Google Translate service initialized")
        except ImportError:
            logger.warning("googletrans not installed. Install: pip install googletrans==4.0.0-rc1")
            self.enabled = False
        except Exception as e:
            logger.warning(f"Translation service initialization failed: {e}")
            self.enabled = False
    
    @lru_cache(maxsize=1000)
    def translate_text(self, text: str, target_lang: str, source_lang: str = "auto") -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'en', 'hi', 'te')
            source_lang: Source language code (auto-detect if 'auto')
        
        Returns:
            Translated text
        """
        if not self.enabled:
            return text
        
        if not text or target_lang == source_lang:
            return text
        
        try:
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            logger.debug(f"Translated '{text[:30]}...' from {source_lang} to {target_lang}")
            return result.text
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def translate_query_to_english(self, query: str, source_lang: str = "auto") -> str:
        """
        Translate query to English for better RAG processing
        
        Args:
            query: Query text in any language
            source_lang: Source language (auto-detect if 'auto')
        
        Returns:
            English translation of query
        """
        return self.translate_text(query, target_lang="en", source_lang=source_lang)
    
    def translate_response(self, text: str, target_lang: str) -> str:
        """
        Translate English response back to user's language
        
        Args:
            text: Response text in English
            target_lang: User's preferred language
        
        Returns:
            Translated response
        """
        if target_lang == "en":
            return text
        
        return self.translate_text(text, target_lang=target_lang, source_lang="en")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Input text
        
        Returns:
            Language code (e.g., 'en', 'hi', 'te')
        """
        if not self.enabled:
            return "en"
        
        try:
            result = self.translator.detect(text)
            logger.debug(f"Detected language: {result.lang} (confidence: {result.confidence})")
            return result.lang
        
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"
    
    def get_supported_languages(self) -> dict:
        """
        Get supported languages
        
        Returns:
            Dict of language codes and names
        """
        return {
            "en": "English",
            "hi": "Hindi",
            "te": "Telugu",
            "ta": "Tamil",
            "kn": "Kannada",
            "mr": "Marathi",
            "gu": "Gujarati",
            "bn": "Bengali",
            "ml": "Malayalam",
            "pa": "Punjabi"
        }


# Fallback translation using dictionary (for common phrases)
TRANSLATIONS = {
    "hi": {
        "Total": "कुल",
        "companies": "कंपनियां",
        "funding": "फंडिंग",
        "crores": "करोड़",
        "Company": "कंपनी",
        "Amount": "राशि",
        "Sector": "सेक्टर",
        "Location": "स्थान",
        "Investors": "निवेशक",
        "Date": "तारीख",
        "No results found": "कोई परिणाम नहीं मिला"
    },
    "te": {
        "Total": "మొత్తం",
        "companies": "కంపెనీలు",
        "funding": "ఫండింగ్",
        "crores": "కోట్లు",
        "Company": "కంపెనీ",
        "Amount": "మొత్తం",
        "Sector": "రంగం",
        "Location": "ప్రదేశం",
        "Investors": "పెట్టుబడిదారులు",
        "Date": "తేదీ",
        "No results found": "ఫలితాలు కనుగొనబడలేదు"
    },
    "ta": {
        "Total": "மொத்தம்",
        "companies": "நிறுவனங்கள்",
        "funding": "நிதி",
        "crores": "கோடி",
        "Company": "நிறுவனம்",
        "Amount": "தொகை",
        "Sector": "துறை",
        "Location": "இடம்",
        "Investors": "முதலீட்டாளர்கள்",
        "Date": "தேதி",
        "No results found": "முடிவுகள் எதுவும் கிடைக்கவில்லை"
    }
}


def get_fallback_translation(text: str, target_lang: str) -> str:
    """Get fallback translation from dictionary"""
    if target_lang in TRANSLATIONS and text in TRANSLATIONS[target_lang]:
        return TRANSLATIONS[target_lang][text]
    return text


# Global translation service instance
translation_service = TranslationService()
