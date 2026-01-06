"""
Query Expansion using LLM to generate better search queries
Improves retrieval by expanding user query with synonyms and related terms
"""
import ollama
from typing import List
import logging

logger = logging.getLogger(__name__)

def expand_query(query: str, lang: str = "en") -> List[str]:
    """
    Expand query with synonyms and related terms using LLM
    
    Args:
        query: Original user query
        lang: Language code
    
    Returns:
        List of expanded queries (original + variations)
    """
    
    # Skip expansion for very short queries
    if len(query.split()) < 3:
        return [query]
    
    prompt = f"""Generate 2 alternative phrasings of this startup funding query. Keep them short and focused.

Original: {query}

Alternative 1:
Alternative 2:"""
    
    try:
        response = ollama.generate(
            model='llama3.1:8b',
            prompt=prompt,
            options={
                'temperature': 0.3,
                'num_predict': 100
            }
        )
        
        # Parse alternatives
        text = response['response'].strip()
        alternatives = []
        
        for line in text.split('\n'):
            line = line.strip()
            # Remove numbering and labels
            if line and not line.startswith('#'):
                cleaned = line.replace('Alternative 1:', '').replace('Alternative 2:', '').strip()
                if cleaned and len(cleaned) > 5:
                    alternatives.append(cleaned)
        
        # Return original + alternatives
        expanded = [query] + alternatives[:2]
        logger.info(f"Expanded query: {query} -> {len(expanded)} variants")
        return expanded
        
    except Exception as e:
        logger.error(f"Query expansion failed: {e}")
        return [query]

# Usage:
# queries = expand_query("2024 EdTech funding", "en")
# # Returns: ["2024 EdTech funding", "EdTech investments in 2024", "Education technology funding 2024"]
# 
# # Then search with all queries and combine results
# all_results = []
# for q in queries:
#     results = collection.query(query_texts=[q], n_results=50)
#     all_results.extend(results)
# # Deduplicate and rerank
