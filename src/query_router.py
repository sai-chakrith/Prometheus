# -*- coding: utf-8 -*-
"""
Query Router Module - Main intelligence layer for query processing
"""

import re
from typing import Dict, Any, Tuple, Optional
from langdetect import detect, LangDetectException
import pandas as pd

# Import local modules
from src.data_loader import load_and_clean_data
from src.rag import load_vector_index, retrieve, get_embedding_model
from src.analytics import get_funding_stats, print_stats_summary


# Global state (loaded once)
_df = None
_index = None
_chunks = None


def initialize():
    """
    Initialize the query router by loading data and vector index.
    Call this once at startup.
    """
    global _df, _index, _chunks
    
    if _df is None:
        print("Initializing query router...")
        print("\n1. Loading and cleaning data...")
        _df = load_and_clean_data()
        
        print("\n2. Loading vector index...")
        _index, _chunks = load_vector_index()
        
        print("\nQuery router initialized successfully!")
    
    return _df, _index, _chunks


def detect_language(text: str) -> str:
    """
    Detect the language of input text.
    
    Parameters:
    -----------
    text : str
        Input text
        
    Returns:
    --------
    str
        Language code ('en', 'hi', etc.) or 'en' as default
    """
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return 'en'  # Default to English


def detect_intent(query: str) -> str:
    """
    Detect user intent: 'analytics' or 'rag'.
    
    Analytics keywords (English/Hindi):
    - how many, total, sum, कितना, कुल, average, औसत
    - trend, growth, वृद्धि, रुझान
    - statistics, stats, आँकड़े
    - top, टॉप, सबसे
    
    RAG keywords:
    - who, what, which, कौन, क्या, किसने
    - find, search, खोज, ढूंढ
    - show me, tell me, बताओ, दिखाओ
    
    Parameters:
    -----------
    query : str
        User query
        
    Returns:
    --------
    str
        'analytics' or 'rag'
    """
    query_lower = query.lower()
    
    # Analytics patterns
    analytics_patterns = [
        # English
        r'\bhow many\b', r'\btotal\b', r'\bsum\b', r'\baverage\b', r'\bavg\b',
        r'\btrend\b', r'\bgrowth\b', r'\bstatistics\b', r'\bstats\b',
        r'\bcount\b', r'\bnumber of\b', r'\bdistribution\b',
        # Hindi (in Devanagari)
        r'कितना', r'कितने', r'कुल', r'औसत', r'वृद्धि', r'रुझान', 
        r'आँकड़े', r'संख्या', r'गणना'
    ]
    
    for pattern in analytics_patterns:
        if re.search(pattern, query_lower):
            return 'analytics'
    
    # Default to RAG for specific information retrieval
    return 'rag'


def extract_filters(query: str) -> Dict[str, Any]:
    """
    Extract filters from query (sector, state, year, etc.).
    
    Parameters:
    -----------
    query : str
        User query
        
    Returns:
    --------
    dict
        Dictionary with filter parameters
    """
    filters = {}
    query_lower = query.lower()
    
    # Extract year (2015-2025)
    year_match = re.search(r'\b(20[0-2][0-9])\b', query)
    if year_match:
        filters['year'] = int(year_match.group(1))
    
    # Sector detection (English + Hindi)
    sector_keywords = {
        'fintech': ['fintech', 'फिनटेक', 'फिनटैक', 'फाइनटेक', 'financial technology', 'वित्तीय प्रौद्योगिकी', 'वित्तीय'],
        'healthtech': ['healthtech', 'health', 'healthcare', 'हेल्थटेक', 'हेल्थ', 'स्वास्थ्य', 'हेल्थकेयर'],
        'edtech': ['edtech', 'education', 'एडटेक', 'एजुकेशन', 'शिक्षा', 'शैक्षिक'],
        'e-commerce': ['ecommerce', 'e-commerce', 'ई-कॉमर्स', 'ईकॉमर्स', 'online shopping', 'ऑनलाइन शॉपिंग'],
        'logistics': ['logistics', 'delivery', 'लॉजिस्टिक्स', 'लॉजिस्टिक', 'डिलीवरी', 'वितरण'],
        'saas': ['saas', 'software', 'सॉफ्टवेयर', 'सास'],
        'food': ['food', 'foodtech', 'फूड', 'फूडटेक', 'खाना', 'restaurant', 'रेस्टोरेंट'],
        'travel': ['travel', 'tourism', 'यात्रा', 'ट्रैवल', 'टूरिज्म', 'पर्यटन'],
        'agritech': ['agritech', 'agriculture', 'farming', 'कृषि', 'एग्रीटेक', 'खेती']
    }
    
    for sector, keywords in sector_keywords.items():
        for keyword in keywords:
            if keyword in query_lower:
                filters['sector'] = sector
                break
        if 'sector' in filters:
            break
    
    # State/City detection (English + Hindi)
    # Use word boundaries to avoid false matches like 'startups' matching 'up'
    state_keywords = {
        'karnataka': ['karnataka', 'कर्नाटक', 'करनाटक', 'bangalore', 'bengaluru', 'बेंगलुरु', 'बेंगलूर', 'बैंगलोर'],
        'maharashtra': ['maharashtra', 'महाराष्ट्र', 'महाराष्‍ट्र', 'mumbai', 'मुंबई', 'मुम्बई', 'pune', 'पुणे'],
        'delhi': ['delhi', 'दिल्ली', 'दिल्‍ली', 'ncr', 'gurgaon', 'gurugram', 'गुड़गांव', 'गुरुग्राम', 'noida', 'नोएडा'],
        'tamil nadu': ['tamil nadu', 'तमिलनाडु', 'तमिल नाडु', 'chennai', 'चेन्नई', 'चेन्नै'],
        'telangana': ['telangana', 'तेलंगाना', 'तेलङ्गाना', 'hyderabad', 'हैदराबाद', 'हैदरबाद'],
        'west bengal': ['west bengal', 'पश्चिम बंगाल', 'kolkata', 'कोलकाता'],
        'gujarat': ['gujarat', 'गुजरात', 'ahmedabad', 'अहमदाबाद', 'अहमदाबाद']
    }
    
    for state, keywords in state_keywords.items():
        for keyword in keywords:
            # Use word boundary matching to avoid false matches
            # e.g., 'up' in 'startups' should not match
            if len(keyword) <= 3:
                # For short keywords, require word boundaries
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    filters['state'] = state
                    break
            else:
                # For longer keywords, simple substring match is fine
                if keyword in query_lower:
                    filters['state'] = state
                    break
        if 'state' in filters:
            break
    
    # Round type detection
    round_keywords = {
        'seed': ['seed', 'सीड'],
        'series a': ['series a', 'सीरीज़ ए'],
        'series b': ['series b', 'सीरीज़ बी'],
        'series c': ['series c', 'सीरीज़ सी'],
        'pre-seed': ['pre-seed', 'pre seed', 'प्री-सीड']
    }
    
    for round_type, keywords in round_keywords.items():
        for keyword in keywords:
            if keyword in query_lower:
                filters['round_type'] = round_type
                break
        if 'round_type' in filters:
            break
    
    return filters


def format_analytics_response(stats: Dict[str, Any], filters: Dict[str, Any], language: str = 'en') -> str:
    """
    Format analytics results in the detected language.
    
    Parameters:
    -----------
    stats : dict
        Statistics from get_funding_stats()
    filters : dict
        Applied filters
    language : str
        Language code ('en' or 'hi')
        
    Returns:
    --------
    str
        Formatted response
    """
    if language == 'hi':
        # Hindi response
        response_lines = ["फंडिंग आंकड़े:"]
        response_lines.append("="*60)
        
        # Filters applied
        if filters:
            filter_parts = []
            if 'sector' in filters:
                filter_parts.append(f"क्षेत्र: {filters['sector']}")
            if 'state' in filters:
                filter_parts.append(f"राज्य: {filters['state']}")
            if 'year' in filters:
                filter_parts.append(f"वर्ष: {filters['year']}")
            if filter_parts:
                response_lines.append(f"फ़िल्टर: {', '.join(filter_parts)}")
                response_lines.append("")
        
        response_lines.append(f"कुल डील्स: {stats['total_deals']:,}")
        response_lines.append(f"कुल फंडिंग: Rs {stats['total_amount_cr']:,.2f} करोड़")
        response_lines.append(f"औसत फंडिंग: Rs {stats['avg_amount_cr']:,.2f} करोड़")
        
        if stats['top_investors']:
            response_lines.append("\nशीर्ष निवेशक:")
            for idx, (investor, count) in enumerate(stats['top_investors'].items(), 1):
                response_lines.append(f"  {idx}. {investor}: {count} डील्स")
        
        if stats['top_startups']:
            response_lines.append("\nशीर्ष स्टार्टअप:")
            for idx, (startup, amount) in enumerate(stats['top_startups'].items(), 1):
                response_lines.append(f"  {idx}. {startup}: Rs {amount:,.2f} करोड़")
        
    else:
        # English response
        response_lines = ["Funding Statistics:"]
        response_lines.append("="*60)
        
        # Filters applied
        if filters:
            filter_parts = []
            if 'sector' in filters:
                filter_parts.append(f"Sector: {filters['sector']}")
            if 'state' in filters:
                filter_parts.append(f"State: {filters['state']}")
            if 'year' in filters:
                filter_parts.append(f"Year: {filters['year']}")
            if filter_parts:
                response_lines.append(f"Filters: {', '.join(filter_parts)}")
                response_lines.append("")
        
        response_lines.append(f"Total Deals: {stats['total_deals']:,}")
        response_lines.append(f"Total Funding: Rs {stats['total_amount_cr']:,.2f} Cr")
        response_lines.append(f"Average Funding: Rs {stats['avg_amount_cr']:,.2f} Cr")
        
        if stats['top_investors']:
            response_lines.append("\nTop Investors:")
            for idx, (investor, count) in enumerate(stats['top_investors'].items(), 1):
                response_lines.append(f"  {idx}. {investor}: {count} deals")
        
        if stats['top_startups']:
            response_lines.append("\nTop Startups by Funding:")
            for idx, (startup, amount) in enumerate(stats['top_startups'].items(), 1):
                response_lines.append(f"  {idx}. {startup}: Rs {amount:,.2f} Cr")
    
    response_lines.append("="*60)
    return "\n".join(response_lines)


def format_rag_response(results: list, query: str, language: str = 'en') -> str:
    """
    Format RAG results with citations.
    
    Parameters:
    -----------
    results : list
        List of (chunk, distance) tuples from retrieve()
    query : str
        Original query
    language : str
        Language code
        
    Returns:
    --------
    str
        Formatted response
    """
    if language == 'hi':
        response_lines = [f"खोज परिणाम: '{query}'"]
        response_lines.append("="*60)
        
        if not results:
            response_lines.append("कोई परिणाम नहीं मिला।")
        else:
            for idx, (chunk, distance) in enumerate(results, 1):
                similarity_score = 1 / (1 + distance)
                response_lines.append(f"\n{idx}. [प्रासंगिकता: {similarity_score:.2%}]")
                response_lines.append(f"   {chunk}")
    else:
        response_lines = [f"Search Results for: '{query}'"]
        response_lines.append("="*60)
        
        if not results:
            response_lines.append("No results found.")
        else:
            for idx, (chunk, distance) in enumerate(results, 1):
                similarity_score = 1 / (1 + distance)
                response_lines.append(f"\n{idx}. [Relevance: {similarity_score:.2%}]")
                response_lines.append(f"   {chunk}")
    
    response_lines.append("\n" + "="*60)
    return "\n".join(response_lines)


def process_query(query: str) -> str:
    """
    Main query processing function.
    Routes to analytics or RAG based on intent.
    
    Parameters:
    -----------
    query : str
        User query in any supported language
        
    Returns:
    --------
    str
        Formatted response
    """
    try:
        # Initialize if needed
        df, index, chunks = initialize()
        
        # Detect language
        language = detect_language(query)
        
        # Detect intent
        intent = detect_intent(query)
        
        # Extract filters
        filters = extract_filters(query)
        
        # Safe console output
        try:
            print(f"\nQuery: {query}")
        except:
            print("\nQuery: [Unicode text]")
        print(f"Detected Language: {language}")
        print(f"Intent: {intent}")
        print(f"Filters: {filters}\n")
        
        if intent == 'analytics':
            # Analytics flow
            stats = get_funding_stats(
                df,
                sector=filters.get('sector'),
                state=filters.get('state'),
                year=filters.get('year'),
                round_type=filters.get('round_type')
            )
            
            # Return response in detected language
            response = format_analytics_response(stats, filters, language)
            
        else:
            # RAG flow
            results = retrieve(index, chunks, query, k=5)
            # Return response in detected language
            response = format_rag_response(results, query, language)
        
        return response
        
    except Exception as e:
        # Return error without Unicode issues
        return f"Error processing query: {str(e)}"


if __name__ == "__main__":
    # This module is designed to be imported
    # No test code - waiting for user's prompt to run on original data
    pass
