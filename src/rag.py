import pandas as pd
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss


# Global model instance (loaded once)
_model = None


def get_embedding_model():
    """
    Get or initialize the sentence transformer model.
    Uses intfloat/multilingual-e5-large for multilingual support.
    
    Returns:
    --------
    SentenceTransformer
        The embedding model
    """
    global _model
    if _model is None:
        print("Loading multilingual-e5-large model...")
        _model = SentenceTransformer('intfloat/multilingual-e5-large')
        print("Model loaded successfully!")
    return _model


def row_to_text_chunk(row: pd.Series) -> str:
    """
    Convert a dataframe row to a text chunk for embedding.
    
    Parameters:
    -----------
    row : pd.Series
        A single row from the funding dataframe
        
    Returns:
    --------
    str
        Formatted text chunk
    """
    parts = []
    
    # Startup/Company name
    for col in ['Startup_Name', 'Company_Name', 'Startup', 'Company']:
        if col in row.index and pd.notna(row[col]):
            parts.append(f"Startup: {row[col]}")
            break
    
    # Sector/Industry
    for col in ['Sector_Standardized', 'Sector', 'Industry', 'Vertical']:
        if col in row.index and pd.notna(row[col]):
            parts.append(f"Sector: {row[col]}")
            break
    
    # Amount
    for col in ['Amount_Cleaned', 'Amount']:
        if col in row.index and pd.notna(row[col]):
            amount_cr = row[col] / 10_000_000  # Convert to Crores
            parts.append(f"Amount: Rs {amount_cr:.2f} Cr")
            break
    
    # State/City/Location
    for col in ['State_Standardized', 'State', 'City', 'Location']:
        if col in row.index and pd.notna(row[col]):
            parts.append(f"Location: {row[col]}")
            break
    
    # Year
    if 'Year' in row.index and pd.notna(row['Year']):
        parts.append(f"Year: {int(row['Year'])}")
    
    # Investor
    for col in ['Investor', 'Investors', 'Investor_Name']:
        if col in row.index and pd.notna(row[col]):
            parts.append(f"Investor: {row[col]}")
            break
    
    # Round/Investment Type
    for col in ['Round', 'Investment_Type', 'Type']:
        if col in row.index and pd.notna(row[col]):
            parts.append(f"Round: {row[col]}")
            break
    
    # Join all parts with separator
    text_chunk = " | ".join(parts)
    
    return text_chunk if text_chunk else "No data available"


def build_vector_index(df: pd.DataFrame, save_path: str = "data/vector_index.pkl") -> Tuple[faiss.Index, List[str]]:
    """
    Build FAISS vector index from funding dataframe.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned funding dataframe
    save_path : str
        Path to save the vector index and chunks
        
    Returns:
    --------
    tuple
        (faiss_index, text_chunks)
    """
    print("Building vector index...")
    print(f"Processing {len(df)} records...")
    
    # Convert rows to text chunks
    print("\nConverting rows to text chunks...")
    text_chunks = []
    for idx, row in df.iterrows():
        chunk = row_to_text_chunk(row)
        text_chunks.append(chunk)
    
    print(f"Created {len(text_chunks)} text chunks")
    
    # Get embedding model
    model = get_embedding_model()
    
    # Generate embeddings
    print("\nGenerating embeddings (this may take a while)...")
    embeddings = model.encode(
        text_chunks,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # L2 normalization for better similarity
    )
    
    print(f"Generated embeddings with shape: {embeddings.shape}")
    
    # Build FAISS index (IndexFlatL2 for exact search)
    print("\nBuilding FAISS IndexFlatL2...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    print(f"Added {index.ntotal} vectors to index")
    
    # Save index and chunks
    print(f"\nSaving index and chunks to {save_path}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save both index and chunks
    with open(save_path, 'wb') as f:
        pickle.dump({
            'index': faiss.serialize_index(index),
            'chunks': text_chunks,
            'dimension': dimension
        }, f)
    
    print(f"Saved vector index with {len(text_chunks)} chunks")
    
    return index, text_chunks


def load_vector_index(load_path: str = "data/vector_index.pkl") -> Tuple[faiss.Index, List[str]]:
    """
    Load FAISS vector index and text chunks from disk.
    
    Parameters:
    -----------
    load_path : str
        Path to the saved vector index
        
    Returns:
    --------
    tuple
        (faiss_index, text_chunks)
    """
    print(f"Loading vector index from {load_path}...")
    
    if not os.path.exists(load_path):
        raise FileNotFoundError(f"Vector index not found at {load_path}")
    
    with open(load_path, 'rb') as f:
        data = pickle.load(f)
    
    # Deserialize FAISS index
    index = faiss.deserialize_index(data['index'])
    chunks = data['chunks']
    
    print(f"Loaded vector index with {len(chunks)} chunks")
    
    return index, chunks


def retrieve(
    index: faiss.Index,
    chunks: List[str],
    query: str,
    k: int = 5
) -> List[Tuple[str, float]]:
    """
    Retrieve top-k most relevant chunks for a query.
    
    Parameters:
    -----------
    index : faiss.Index
        FAISS index
    chunks : List[str]
        List of text chunks corresponding to index vectors
    query : str
        Query text (can be in any language supported by multilingual-e5-large)
    k : int
        Number of results to return
        
    Returns:
    --------
    List[Tuple[str, float]]
        List of (chunk, distance) tuples, sorted by relevance
    """
    # Get embedding model
    model = get_embedding_model()
    
    # For E5 models, queries should be prefixed with "query: "
    # This is a recommendation from the model documentation
    prefixed_query = f"query: {query}"
    
    # Generate query embedding
    query_embedding = model.encode(
        [prefixed_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    # Search in FAISS index
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    # Prepare results
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx < len(chunks):  # Ensure index is valid
            results.append((chunks[idx], float(distance)))
    
    return results


def retrieve_with_metadata(
    index: faiss.Index,
    chunks: List[str],
    df: pd.DataFrame,
    query: str,
    k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k results with full metadata from original dataframe.
    
    Parameters:
    -----------
    index : faiss.Index
        FAISS index
    chunks : List[str]
        List of text chunks
    df : pd.DataFrame
        Original dataframe with full data
    query : str
        Query text
    k : int
        Number of results to return
        
    Returns:
    --------
    List[Dict[str, Any]]
        List of dictionaries with chunk text, distance, and full row data
    """
    # Get basic retrieval results
    results = retrieve(index, chunks, query, k)
    
    # Enhance with metadata
    enhanced_results = []
    for chunk, distance in results:
        # Find corresponding row index
        try:
            row_idx = chunks.index(chunk)
            if row_idx < len(df):
                row_data = df.iloc[row_idx].to_dict()
                enhanced_results.append({
                    'chunk': chunk,
                    'distance': distance,
                    'similarity_score': 1 / (1 + distance),  # Convert distance to similarity
                    'metadata': row_data
                })
        except (ValueError, IndexError):
            # If row not found, just include the chunk
            enhanced_results.append({
                'chunk': chunk,
                'distance': distance,
                'similarity_score': 1 / (1 + distance),
                'metadata': {}
            })
    
    return enhanced_results


def print_search_results(results: List[Tuple[str, float]], query: str) -> None:
    """
    Pretty print search results.
    
    Parameters:
    -----------
    results : List[Tuple[str, float]]
        Search results from retrieve()
    query : str
        The search query
    """
    print("\n" + "="*80)
    print(f"Search Results for: '{query}'")
    print("="*80)
    
    for idx, (chunk, distance) in enumerate(results, 1):
        similarity_score = 1 / (1 + distance)
        print(f"\n{idx}. [Similarity: {similarity_score:.4f}]")
        print(f"   {chunk}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # This module is designed to be imported and used with actual data
    # No test code - waiting for user's prompt to run on original data
    pass
