"""
Cross-Encoder Reranker for improved retrieval accuracy
Reranks ChromaDB results to get most relevant documents
"""
from sentence_transformers import CrossEncoder
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder for reranking
        
        Good models:
        - cross-encoder/ms-marco-MiniLM-L-6-v2 (fast, good)
        - cross-encoder/ms-marco-MiniLM-L-12-v2 (slower, better)
        """
        print(f"Loading reranker model: {model_name}")
        self.model = CrossEncoder(model_name)
        print("✅ Reranker loaded")
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict], 
        top_k: int = 15
    ) -> List[Dict]:
        """
        Rerank documents based on query relevance
        
        Args:
            query: User query
            documents: List of retrieved documents with 'text' field
            top_k: Number of top documents to return
        
        Returns:
            Reranked list of top_k documents
        """
        if not documents:
            return []
        
        # Create query-document pairs
        pairs = []
        for doc in documents:
            # Combine all text fields for better matching
            text = f"{doc.get('company', '')} {doc.get('sector', '')} {doc.get('amount', '')} {doc.get('city', '')}"
            pairs.append([query, text])
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Sort by score descending
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k
        reranked = [doc for doc, score in scored_docs[:top_k]]
        
        logger.info(f"Reranked {len(documents)} docs -> top {top_k}")
        logger.info(f"Score range: {scores.max():.3f} to {scores.min():.3f}")
        
        return reranked

# Usage in main.py:
# reranker = Reranker()
# retrieved_docs = reranker.rerank(query, retrieved_docs, top_k=15)
