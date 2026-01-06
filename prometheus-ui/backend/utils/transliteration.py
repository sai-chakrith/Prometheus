"""
Transliteration utilities for Indian languages
"""
import ollama
import logging

logger = logging.getLogger(__name__)

def transliterate_company_name(company_name: str, lang: str) -> str:
    """Use LLM to transliterate company name to native script"""
    if not company_name or company_name in ['Unknown', 'Not disclosed', 'अज्ञात', 'माहिती नाही', 'తెలియదు', 'சொல்லப்படவில்லை', 'ತಿಳಿದಿಲ್ಲ', 'জানা নেই', 'અજ્ઞાત']:
        return company_name
    
    try:
        # Language-specific prompts for transliteration with explicit script requirement
        prompts = {
            "hi": f"Write ONLY '{company_name}' in Devanagari Hindi Unicode (स्विगी for Swiggy). No explanation:",
            "te": f"Write ONLY '{company_name}' in Telugu Unicode script. No explanation:",
            "ta": f"Write ONLY '{company_name}' in Tamil Unicode script. No explanation:",
            "kn": f"Write ONLY '{company_name}' in Kannada Unicode script. No explanation:",
            "bn": f"Write ONLY '{company_name}' in Bengali Unicode script. No explanation:",
            "mr": f"Write ONLY '{company_name}' in Devanagari Marathi Unicode. No explanation:",
            "gu": f"Write ONLY '{company_name}' in Gujarati Unicode script. No explanation:"
        }
        
        if lang not in prompts:
            return company_name
        
        response = ollama.generate(
            model='llama3.1:8b',
            prompt=prompts[lang],
            options={
                'temperature': 0.0,  # Zero temp for consistency
                'num_predict': 30,   # Short output
                'top_p': 0.8
            }
        )
        
        transliterated = response['response'].strip()
        # Clean up the response
        transliterated = transliterated.replace('"', '').replace("'", '').strip()
        transliterated = transliterated.split('\n')[0].strip()  # Take only first line
        
        # Validate it's not mostly English/Latin characters
        latin_count = sum(1 for c in transliterated if ord(c) < 128)
        if latin_count > len(transliterated) * 0.5:  # More than 50% Latin
            return company_name  # Fallback to original
        
        return transliterated if transliterated else company_name
    except Exception as e:
        logger.error(f"Transliteration error: {e}")
        return company_name

def reverse_transliterate_company_name(name: str) -> str:
    """Convert Indic script company names to English equivalents"""
    # Common company name mappings from Indic scripts to English
    company_mappings = {
        # Hindi/Devanagari
        'स्विगी': 'Swiggy', 'स्विग्गी': 'Swiggy',
        'फ्लिपकार्ट': 'Flipkart', 'फ्लिप्कार्ट': 'Flipkart',
        'पेटीएम': 'Paytm', 'पेटिएम': 'Paytm',
        'ओला': 'Ola',
        'ज़ोमैटो': 'Zomato', 'जोमैटो': 'Zomato',
        'उबर': 'Uber',
        'ग्रोफर्स': 'Grofers',
        
        # Telugu
        'స్విగ్గీ': 'Swiggy', 'స్విగ్గి': 'Swiggy',
        'ఫ్లిప్‌కార్ట్': 'Flipkart', 'ఫ్లిప్కార్ట్': 'Flipkart',
        'పేటీఎం': 'Paytm',
        'ఓలా': 'Ola',
        'జోమాటో': 'Zomato',
        
        # Tamil
        'ஸ்விகி': 'Swiggy', 'ஸ்விக்கி': 'Swiggy',
        'ஃபிளிப்கார்ட்': 'Flipkart',
        'பேடிஎம்': 'Paytm',
        'ஓலா': 'Ola',
        'ஜொமேட்டோ': 'Zomato',
        
        # Kannada
        'ಸ್ವಿಗ್ಗಿ': 'Swiggy', 'ಸ್ವಿಗ್ಗೀ': 'Swiggy',
        'ಫ್ಲಿಪ್ಕಾರ್ಟ್': 'Flipkart',
        'ಪೇಟಿಎಂ': 'Paytm',
        'ಓಲಾ': 'Ola',
        'ಜೋಮ್ಯಾಟೋ': 'Zomato',
        
        # Marathi
        'स्विगी': 'Swiggy',
        'फ्लिपकार्ट': 'Flipkart',
        'पेटीएम': 'Paytm',
        'ओला': 'Ola',
        'झोमॅटो': 'Zomato',
        
        # Gujarati
        'સ્વિગી': 'Swiggy',
        'ફ્લિપકાર્ટ': 'Flipkart',
        'પેટીએમ': 'Paytm',
        'ઓલા': 'Ola',
        'ઝોમેટો': 'Zomato',
        
        # Bengali
        'সুইগি': 'Swiggy', 'স্উইগি': 'Swiggy',
        'ফ্লিপকার্ট': 'Flipkart',
        'পেটিএম': 'Paytm',
        'ওলা': 'Ola',
        'জোমাটো': 'Zomato'
    }
    
    # Check if the name is in our mapping
    for indic_name, english_name in company_mappings.items():
        if indic_name in name:
            return english_name
    
    return name
