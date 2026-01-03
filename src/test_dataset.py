# -*- coding: utf-8 -*-
"""
Test Dataset for RAGAS Evaluation
Contains sample questions, ground truth answers, and metadata
"""

# Sample test questions for the Indian Startup Funding RAG system
TEST_QUESTIONS = [
    # English queries
    "Which fintech startups received funding in Karnataka in 2022?",
    "What was the total funding amount for edtech companies?",
    "List the top 5 investors in the Indian startup ecosystem",
    "How much funding did Bangalore-based startups receive in 2021?",
    "Which sector received the most funding in Maharashtra?",
    
    # Hindi queries
    "कर्नाटक में फिनटेक स्टार्टअप्स को कितनी फंडिंग मिली?",
    "बेंगलुरु में सबसे ज्यादा फंडिंग किस सेक्टर को मिली?",
    "2022 में कितनी स्टार्टअप्स को फंडिंग मिली?",
    
    # Mixed queries
    "Show me all Series A funding rounds in fintech",
    "What is the average funding amount for AI startups?",
    "Tell me about recent funding in healthcare sector",
    "Which cities have the most startup funding?",
]


# Ground truth answers (optional - for answer_correctness metric)
# These should be factually correct answers based on your data
GROUND_TRUTH_ANSWERS = {
    "Which fintech startups received funding in Karnataka in 2022?": 
        "Based on the funding data, several fintech startups in Karnataka received funding in 2022, including major players in the digital payments and lending space.",
    
    "What was the total funding amount for edtech companies?":
        "The edtech sector received significant funding across multiple rounds and companies.",
    
    "कर्नाटक में फिनटेक स्टार्टअप्स को कितनी फंडिंग मिली?":
        "कर्नाटक में फिनटेक स्टार्टअप्स को 2022 में महत्वपूर्ण फंडिंग प्राप्त हुई।",
}


# Expected contexts for each question (for manual validation)
EXPECTED_CONTEXT_KEYWORDS = {
    "Which fintech startups received funding in Karnataka in 2022?": 
        ["fintech", "karnataka", "2022", "funding"],
    
    "What was the total funding amount for edtech companies?":
        ["edtech", "education", "funding", "amount"],
    
    "कर्नाटक में फिनटेक स्टार्टअप्स को कितनी फंडिंग मिली?":
        ["fintech", "karnataka", "funding"],
}


# Test cases with full metadata
TEST_CASES = [
    {
        "id": 1,
        "question": "Which fintech startups received funding in Karnataka in 2022?",
        "language": "en",
        "intent": "rag",
        "filters": {
            "sector": "fintech",
            "state": "karnataka",
            "year": 2022
        },
        "ground_truth": "Based on the funding data, several fintech startups in Karnataka received funding in 2022.",
    },
    {
        "id": 2,
        "question": "What was the total funding amount for edtech companies?",
        "language": "en",
        "intent": "analytics",
        "filters": {
            "sector": "edtech"
        },
        "ground_truth": None,  # Analytics queries may not have ground truth
    },
    {
        "id": 3,
        "question": "कर्नाटक में फिनटेक स्टार्टअप्स को कितनी फंडिंग मिली?",
        "language": "hi",
        "intent": "analytics",
        "filters": {
            "sector": "fintech",
            "state": "karnataka"
        },
        "ground_truth": None,
    },
    {
        "id": 4,
        "question": "Show me all Series A funding rounds in fintech",
        "language": "en",
        "intent": "rag",
        "filters": {
            "sector": "fintech",
            "round": "Series A"
        },
        "ground_truth": "Multiple fintech startups raised Series A rounds with various investors.",
    },
    {
        "id": 5,
        "question": "Which sector received the most funding in Maharashtra?",
        "language": "en",
        "intent": "analytics",
        "filters": {
            "state": "maharashtra"
        },
        "ground_truth": None,
    },
]


# Minimal test set for quick evaluation
QUICK_TEST_QUESTIONS = [
    "Which fintech startups received funding in Karnataka?",
    "What was the total funding for edtech companies?",
    "कर्नाटक में फंडिंग की स्थिति क्या है?",
]


def get_test_questions(
    language: str = "all",
    intent: str = "all",
    limit: int = None
):
    """
    Get filtered test questions.
    
    Parameters:
    -----------
    language : str
        Filter by language: 'en', 'hi', or 'all'
    intent : str
        Filter by intent: 'rag', 'analytics', or 'all'
    limit : int, optional
        Maximum number of questions to return
        
    Returns:
    --------
    List[dict]
        Filtered test cases
    """
    filtered = TEST_CASES.copy()
    
    # Filter by language
    if language != "all":
        filtered = [tc for tc in filtered if tc["language"] == language]
    
    # Filter by intent
    if intent != "all":
        filtered = [tc for tc in filtered if tc["intent"] == intent]
    
    # Apply limit
    if limit:
        filtered = filtered[:limit]
    
    return filtered


def get_questions_with_ground_truth():
    """
    Get only test cases that have ground truth answers.
    Useful for metrics that require ground truth (answer_correctness, etc.)
    
    Returns:
    --------
    List[dict]
        Test cases with ground truth
    """
    return [tc for tc in TEST_CASES if tc["ground_truth"] is not None]


if __name__ == "__main__":
    print("Test Dataset for RAGAS Evaluation")
    print(f"\nTotal test cases: {len(TEST_CASES)}")
    print(f"English questions: {len(get_test_questions(language='en'))}")
    print(f"Hindi questions: {len(get_test_questions(language='hi'))}")
    print(f"RAG queries: {len(get_test_questions(intent='rag'))}")
    print(f"Analytics queries: {len(get_test_questions(intent='analytics'))}")
    print(f"With ground truth: {len(get_questions_with_ground_truth())}")
