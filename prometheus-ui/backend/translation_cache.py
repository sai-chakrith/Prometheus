"""
Translation cache to avoid repeated LLM calls for transliteration
Saves ~15-25 seconds per query!
"""
import json
import os
from typing import Dict, Optional

CACHE_FILE = "translation_cache.json"

class TranslationCache:
    def __init__(self):
        self.cache: Dict[str, Dict[str, str]] = {}
        self.load()
    
    def load(self):
        """Load cache from disk"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"✅ Loaded {sum(len(v) for v in self.cache.values())} cached translations")
            except Exception as e:
                print(f"⚠️ Could not load cache: {e}")
                self.cache = {}
    
    def save(self):
        """Save cache to disk"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.warning(f"Could not save cache file: {e}")
        except TypeError as e:
            logger.error(f"Cache contains non-serializable data: {e}")
    
    def get(self, text: str, lang: str) -> Optional[str]:
        """Get cached translation"""
        if lang in self.cache:
            return self.cache[lang].get(text)
        return None
    
    def set(self, text: str, lang: str, translation: str):
        """Cache translation"""
        if lang not in self.cache:
            self.cache[lang] = {}
        self.cache[lang][text] = translation
        
        # Auto-save every 10 translations
        if len(self.cache[lang]) % 10 == 0:
            self.save()
    
    def preload_common_terms(self):
        """Preload common sector/city names"""
        common_terms = {
            'hi': {
                'Fintech': 'फिनटेक',
                'Edtech': 'एडटेक',
                'Healthtech': 'हेल्थटेक',
                'Foodtech': 'फूडटेक',
                'SaaS': 'सास',
                'E-commerce': 'ई-कॉमर्स',
                'Gaming': 'गेमिंग',
                'Agritech': 'एग्रीटेक',
                'Mobility': 'मोबिलिटी',
                'Deeptech': 'डीपटेक',
                'Delhi': 'दिल्ली',
                'Mumbai': 'मुंबई',
                'Bangalore': 'बैंगलोर',
                'Pune': 'पुणे',
                'Hyderabad': 'हैदराबाद',
                'Chennai': 'चेन्नई',
                'Kolkata': 'कोलकाता',
                'Gurgaon': 'गुड़गांव',
                'Ahmedabad': 'अहमदाबाद',
                'Surat': 'सुरत'
            },
            'te': {
                'Fintech': 'ఫిన్టెక్',
                'Edtech': 'ఎడ్టెక్',
                'Healthtech': 'హెల్త్‌టెక్',
                'Foodtech': 'ఫుడ్‌టెక్',
                'SaaS': 'సాస్',
                'E-commerce': 'ఈ-కామర్స్',
                'Gaming': 'గేమింగ్',
                'Agritech': 'అగ్రిటెక్',
                'Delhi': 'ఢిల్లీ',
                'Mumbai': 'ముంబై',
                'Bangalore': 'బెంగళూరు',
                'Pune': 'పుణే',
                'Hyderabad': 'హైదరాబాద్'
            },
            'ta': {
                'Fintech': 'நிதித்தொழில்நுட்பம்',
                'Edtech': 'கல்வித்தொழில்நுட்பம்',
                'Delhi': 'தில்லி',
                'Mumbai': 'மும்பை',
                'Bangalore': 'பெங்களூர்'
            }
            # Add more languages...
        }
        
        for lang, terms in common_terms.items():
            if lang not in self.cache:
                self.cache[lang] = {}
            self.cache[lang].update(terms)
        
        self.save()
        print(f"✅ Preloaded {sum(len(v) for v in common_terms.values())} common translations")

# Global cache instance
translation_cache = TranslationCache()
