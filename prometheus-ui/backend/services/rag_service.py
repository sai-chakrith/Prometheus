"""
RAG Service - Handles all RAG pipeline operations
"""
import logging
from typing import Dict, List, Optional
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import re

from utils import parse_amount_to_numeric, format_amount, transliterate_company_name, reverse_transliterate_company_name
from config import Config

logger = logging.getLogger(__name__)

class RAGService:
    """Service for RAG operations"""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.df: Optional[pd.DataFrame] = None
        self.chroma_client = None
        self.collection = None
        self.company_info_cache: Dict[str, str] = {}
    
    def initialize(self, dataset_path: str):
        """Initialize RAG components"""
        logger.info("Initializing RAG service...")
        
        # Load embedding model
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        logger.info("Embedding model loaded")
        
        # Load dataset
        self.df = pd.read_csv(dataset_path)
        logger.info(f"Loaded {len(self.df)} records from dataset")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=Config.CHROMA_PATH)
        
        try:
            self.collection = self.chroma_client.get_collection(name="startup_funding")
            logger.info(f"Loaded existing ChromaDB collection with {self.collection.count()} documents")
        except:
            logger.info("Creating new ChromaDB collection...")
            self._create_chromadb_collection()
        
        logger.info("RAG service initialized successfully")
    
    def _create_chromadb_collection(self):
        """Create and populate ChromaDB collection"""
        self.collection = self.chroma_client.create_collection(
            name="startup_funding",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Create embeddings
        company_texts = self.df.apply(
            lambda row: f"{row['Startup Name']} received {row['Amount_Cleaned']} funding in {row['Sector_Standardized']} sector on {row['Date_Parsed']} ({row['Year']}), {row['City']}, {row['State_Standardized']}",
            axis=1
        ).tolist()
        
        logger.info(f"Creating embeddings for {len(company_texts)} companies...")
        embeddings = self.model.encode(company_texts, show_progress_bar=True)
        
        # Add to ChromaDB with clean data
        clean_metadatas, clean_embeddings, clean_documents, clean_ids = [], [], [], []
        
        for i, (idx, row) in enumerate(self.df.iterrows()):
            if (pd.isna(row['Startup Name']) or str(row['Startup Name']).strip().lower() == 'unknown' or
                pd.isna(row['Sector_Standardized']) or str(row['Sector_Standardized']).strip().lower() == 'unknown'):
                continue
            
            metadata = {
                "company": str(row['Startup Name']).strip(),
                "amount": str(row['Amount_Cleaned']) if pd.notna(row['Amount_Cleaned']) else '0',
                "sector": str(row['Sector_Standardized']).strip(),
                "row_id": idx
            }
            
            # Add optional fields
            for field, col in [("city", "City"), ("state", "State_Standardized"), 
                              ("investors", "Investors' Name"), ("date", "Date_Parsed"), ("year", "Year")]:
                value = str(row[col]).strip() if pd.notna(row.get(col)) else ''
                if value and value.lower() not in ['unknown', 'nan', '', 'undisclosed']:
                    metadata[field] = value if field != "year" else str(int(float(value)))
            
            clean_metadatas.append(metadata)
            clean_embeddings.append(embeddings[i].tolist())
            clean_documents.append(company_texts[i])
            clean_ids.append(f"doc_{len(clean_ids)}")
        
        self.collection.add(
            embeddings=clean_embeddings,
            documents=clean_documents,
            metadatas=clean_metadatas,
            ids=clean_ids
        )
        
        logger.info(f"Added {len(clean_metadatas)} documents to ChromaDB")
    
    def query(self, query: str, lang: str = "en", filters: Dict = None) -> Dict:
        """
        Execute RAG query with optional filters
        
        Args:
            query: Search query
            lang: Language code
            filters: Optional filters dict with keys:
                - sector: Filter by sector
                - min_amount: Minimum funding amount
                - max_amount: Maximum funding amount
                - city: Filter by city
                - state: Filter by state
                - year: Filter by year
        """
        logger.info(f"RAG query: '{query[:50]}...' in {lang} with filters: {filters}")
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Build ChromaDB where clause from filters
        where_clause = None
        if filters:
            where_conditions = {}
            
            if filters.get("sector"):
                where_conditions["sector"] = filters["sector"]
            
            if filters.get("city"):
                where_conditions["city"] = filters["city"]
            
            if filters.get("state"):
                where_conditions["state"] = filters["state"]
            
            if filters.get("year"):
                where_conditions["year"] = str(filters["year"])
            
            if where_conditions:
                where_clause = where_conditions
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=100,
            where=where_clause
        )
        
        # Parse and filter results
        SIMILARITY_THRESHOLD = 0.25
        retrieved_docs = []
        
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            similarity_score = float(1 - results['distances'][0][i])
            
            if similarity_score > SIMILARITY_THRESHOLD:
                amount_numeric = parse_amount_to_numeric(metadata['amount'])
                
                # Apply amount filters
                if filters:
                    if filters.get("min_amount") and amount_numeric < filters["min_amount"]:
                        continue
                    if filters.get("max_amount") and amount_numeric > filters["max_amount"]:
                        continue
                
                retrieved_docs.append({
                    "company": metadata['company'],
                    "amount": format_amount(metadata['amount']),
                    "sector": metadata.get('sector', ''),
                    "city": metadata.get('city', ''),
                    "state": metadata.get('state', ''),
                    "investors": metadata.get('investors', ''),
                    "date": metadata.get('date', ''),
                    "year": metadata.get('year', ''),
                    "row": metadata['row_id'],
                    "score": similarity_score
                })
        
        retrieved_docs = sorted(retrieved_docs, key=lambda x: x['score'], reverse=True)
        logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
        
        if not retrieved_docs:
            return self._no_results_response(lang)
        
        # Generate answer
        answer = self._generate_answer(query, lang, retrieved_docs)
        
        return {
            "answer": answer,
            "sources": retrieved_docs[:5]  # Return top 5 sources
        }
    
    def _generate_answer(self, query: str, lang: str, docs: List[Dict]) -> str:
        """Generate answer from retrieved documents"""
        # Calculate totals
        total_funding = sum(parse_amount_to_numeric(doc['amount']) for doc in docs)
        total_companies = len(set(doc['company'] for doc in docs))
        
        if lang != 'en':
            # Use template-based approach for non-English
            return self._generate_template_answer(lang, docs, total_funding, total_companies)
        
        # English response
        answer_parts = []
        answer_parts.append(f"**Total {total_companies} companies, ₹{total_funding/10_000_000:.2f} Cr total funding**\n\n")
        answer_parts.append(f"**Companies:**\n\n")
        
        for i, doc in enumerate(docs[:15], 1):
            answer_parts.append(f"{i}. **{doc['company']}** • {doc['amount']}")
            if doc.get('year'):
                answer_parts.append(f" • {doc['year']}")
            if doc.get('sector') and doc['sector'] != 'Unknown':
                answer_parts.append(f" • {doc['sector']}")
            if doc.get('city') and doc['city'] != 'Unknown':
                answer_parts.append(f" • {doc['city']}")
            answer_parts.append("\n")
        
        return "".join(answer_parts)
    
    def _generate_template_answer(self, lang: str, docs: List[Dict], total_funding: float, total_companies: int) -> str:
        """Generate template-based answer for non-English languages"""
        labels = {
            'hi': {'total': 'कुल', 'companies': 'कंपनियां', 'funding': 'फंडिंग', 'crores': 'करोड़'},
            'te': {'total': 'మొత్తం', 'companies': 'కంపెనీలు', 'funding': 'ఫండింగ్', 'crores': 'కోట్లు'},
            'ta': {'total': 'மொத்தம்', 'companies': 'நிறுவனங்கள்', 'funding': 'நிதி', 'crores': 'கோடி'},
            'kn': {'total': 'ಒಟ್ಟು', 'companies': 'ಕಂಪನಿಗಳು', 'funding': 'ಫಂಡಿಂಗ್', 'crores': 'ಕೋಟಿ'},
            'mr': {'total': 'एकूण', 'companies': 'कंपन्या', 'funding': 'फंडिंग', 'crores': 'कोटी'},
            'gu': {'total': 'કુલ', 'companies': 'કંપનીઓ', 'funding': 'ફંડિંગ', 'crores': 'કરોડ'},
            'bn': {'total': 'মোট', 'companies': 'কোম্পানি', 'funding': 'ফান্ডিং', 'crores': 'কোটি'}
        }
        
        lbl = labels.get(lang, labels['hi'])
        
        answer_parts = []
        answer_parts.append(f"**{lbl['total']} {total_companies} {lbl['companies']}, ₹{total_funding/10_000_000:.2f} {lbl['crores']} {lbl['funding']}**\n\n")
        answer_parts.append(f"**{lbl['companies']}:**\n\n")
        
        for i, doc in enumerate(docs[:15], 1):
            company_name = transliterate_company_name(doc['company'], lang)
            answer_parts.append(f"{i}. **{company_name}** • {doc['amount']}")
            if doc.get('year'):
                answer_parts.append(f" • {doc['year']}")
            if doc.get('sector'):
                answer_parts.append(f" • {doc['sector']}")
            answer_parts.append("\n")
        
        return "".join(answer_parts)
    
    def _no_results_response(self, lang: str) -> Dict:
        """Return no results found response"""
        messages = {
            "hi": "क्षमा करें, इस प्रश्न के लिए कोई जानकारी नहीं मिली। कृपया अलग शब्दों में पूछें।",
            "te": "క్షమించండి, ఈ ప్రశ్నకు సమాచారం దొరకలేదు। దయచేసి వేరే పదాలలో అడగండి।",
            "en": "Sorry, no relevant information found. Please try rephrasing your question."
        }
        return {
            "answer": messages.get(lang, messages["en"]),
            "sources": []
        }
    
    def get_company_info(self, company_name: str, lang: str = "en") -> Optional[Dict]:
        """Get detailed company information"""
        if self.df is None:
            return None
        
        company_data = self.df[self.df['Startup Name'].str.lower() == company_name.lower()]
        
        if company_data.empty:
            return None
        
        funding_rounds = []
        for _, row in company_data.iterrows():
            funding_rounds.append({
                "amount": format_amount(row['Amount_Cleaned']),
                "date": row.get('Date', 'Unknown'),
                "year": str(row.get('Year', 'Unknown')),
                "investors": row.get('Investors', 'Not disclosed'),
                "sector": row.get('Sector', 'Unknown'),
                "city": row.get('City_Standardized', 'Unknown'),
                "state": row.get('State_Standardized', 'Unknown')
            })
        
        total_funding = company_data['Amount_Cleaned'].apply(parse_amount_to_numeric).sum()
        
        return {
            "company": company_name,
            "description": self._get_company_description(company_name, lang),
            "funding_rounds": funding_rounds,
            "total_funding": format_amount(total_funding),
            "total_rounds": len(funding_rounds)
        }
    
    def _get_company_description(self, company_name: str, lang: str) -> str:
        """Get or generate company description"""
        cache_key = f"{company_name.lower()}_{lang}"
        if cache_key in self.company_info_cache:
            return self.company_info_cache[cache_key]
        
        company_data = self.df[self.df['Startup Name'].str.lower() == company_name.lower()]
        
        if not company_data.empty:
            sector = company_data['Sector_Standardized'].mode()[0] if not company_data['Sector_Standardized'].empty else ""
            if sector and sector != 'Unknown':
                descriptions = {
                    "en": f"A {sector} company",
                    "hi": f"{sector} सेक्टर की कंपनी"
                }
                description = descriptions.get(lang, descriptions["en"])
                self.company_info_cache[cache_key] = description
                return description
        
        return f"A startup company" if lang == "en" else "एक स्टार्टअप कंपनी"

# Global RAG service instance
rag_service = RAGService()
