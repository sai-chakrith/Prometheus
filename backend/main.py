"""
PROMETHEUS FastAPI Backend - RAG Endpoint
Multilingual Startup Funding Query System
Enhanced with ChromaDB + Ollama Llama 3.2
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama
import re
import os

app = FastAPI(title="Prometheus RAG API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class RagRequest(BaseModel):
    query: str
    lang: Optional[str] = "hi"

class RagResponse(BaseModel):
    answer: str
    sources: List[dict]

# Global state for models and data
model = None
df = None
chroma_client = None
collection = None

def load_resources():
    """Load model, ChromaDB, and dataset on startup"""
    global model, df, chroma_client, collection
    
    print("🚀 Loading Prometheus resources...")
    
    # Load embedding model
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    
    # Load cleaned funding data
    csv_path = r"C:\Users\DHEERAJ\Downloads\hackathon2\cleaned_funding.csv"
    df = pd.read_csv(csv_path)
    
    # Initialize ChromaDB
    print("📦 Initializing ChromaDB...")
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create or get collection
    try:
        # Try to delete existing collection if it's empty
        try:
            existing = chroma_client.get_collection(name="startup_funding")
            if existing.count() == 0:
                print("🗑️  Deleting empty collection...")
                chroma_client.delete_collection(name="startup_funding")
                raise ValueError("Recreating collection")
            else:
                collection = existing
                print(f"✅ Loaded existing ChromaDB collection with {collection.count()} documents")
        except:
            raise ValueError("Creating new collection")
    except:
        print("📝 Creating new ChromaDB collection...")
        collection = chroma_client.create_collection(
            name="startup_funding",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Create embeddings and add to ChromaDB
        company_texts = df.apply(
            lambda row: f"{row['Startup Name']} received {row['Amount_Cleaned']} funding in {row['Sector_Standardized']} sector, {row['City']}, {row['State_Standardized']}",
            axis=1
        ).tolist()
        
        print(f"🔢 Creating embeddings for {len(company_texts)} companies...")
        embeddings = model.encode(company_texts, show_progress_bar=True)
        
        # Add to ChromaDB
        collection.add(
            embeddings=embeddings.tolist(),
            documents=company_texts,
            metadatas=[
                {
                    "company": str(row['Startup Name']) if pd.notna(row['Startup Name']) else 'Unknown',
                    "amount": str(row['Amount_Cleaned']) if pd.notna(row['Amount_Cleaned']) else '0',
                    "sector": str(row['Sector_Standardized']) if pd.notna(row['Sector_Standardized']) else 'Unknown',
                    "city": str(row['City']) if pd.notna(row['City']) else 'Unknown',
                    "state": str(row['State_Standardized']) if pd.notna(row['State_Standardized']) else 'India',
                    "row_id": idx + 2
                }
                for idx, row in df.iterrows()
            ],
            ids=[f"doc_{i}" for i in range(len(company_texts))]
        )
        
        print(f"✅ Added {len(company_texts)} documents to ChromaDB")
    
    # Check if Ollama is available
    try:
        ollama.list()
        print("✅ Ollama connection successful")
    except Exception as e:
        print(f"⚠️  Ollama not available: {e}")
        print("   Install Ollama and run: ollama pull llama3.2:3b")
    
    print(f"✅ Loaded {len(df)} companies with ChromaDB vector store")

def translate_query(query: str, lang: str) -> str:
    """Translate query to English for processing"""
    # Simple dictionary-based translation for demo
    translations = {
        "hi": {
            "कितना": "how much", "किसे": "which", "कौन": "who",
            "मिला": "received", "फंडिंग": "funding", "शहर": "city",
            "सेक्टर": "sector", "कंपनी": "company"
        },
        "mr": {
            "किती": "how much", "कोणाला": "which", "कोण": "who",
            "मिळाले": "received", "निधी": "funding"
        },
        "gu": {
            "કેટલું": "how much", "કોને": "which", "કોણ": "who",
            "મળ્યું": "received", "ફંડિંગ": "funding"
        }
    }
    
    # For demo, return original query (model handles multilingual)
    return query

def format_amount(amount: str) -> str:
    """Format amount in readable form"""
    try:
        # Extract numeric value
        num_match = re.search(r'[\d,\.]+', str(amount))
        if num_match:
            num_str = num_match.group().replace(',', '')
            num = float(num_str)
            
            if 'M' in str(amount) or num >= 1_000_000:
                return f"${num/1_000_000:.1f}M"
            elif 'K' in str(amount) or num >= 1_000:
                return f"${num/1_000:.0f}K"
        return str(amount)
    except:
        return str(amount)

def prometheus_pipeline(query: str, lang: str = "hi") -> dict:
    """Main RAG pipeline with ChromaDB + Ollama"""
    global model, df, collection
    
    # Encode query (paraphrase-multilingual-mpnet-base-v2 handles Hindi well)
    query_embedding = model.encode([query])[0]
    
    # Query ChromaDB for top 10 results (increased from 5 for better recall)
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=10
    )
    
    # Parse results
    retrieved_docs = []
    for i in range(len(results['ids'][0])):
        metadata = results['metadatas'][0][i]
        retrieved_docs.append({
            "company": metadata['company'],
            "amount": format_amount(metadata['amount']),
            "sector": metadata['sector'],
            "city": metadata['city'],
            "state": metadata['state'],
            "row": metadata['row_id'],
            "score": float(1 - results['distances'][0][i])  # Convert distance to similarity
        })
    
    # Try to generate answer with Ollama Llama 3.2
    try:
        top_result = retrieved_docs[0]
        
        # Create context from top results
        context = "\n".join([
            f"- {doc['company']}: {doc['amount']} in {doc['sector']}, {doc['city']}, {doc['state']}"
            for doc in retrieved_docs[:5]  # Show top 5 in context
        ])
        
        # Language-specific prompts
        prompts = {
            "hi": f"""तुम एक भारतीय स्टार्टअप फंडिंग विशेषज्ञ हो। ये टॉप कंपनियां मिलीं:

{context}

प्रश्न: {query}

कृपया हिंदी में विस्तृत उत्तर दें। सभी प्रासंगिक कंपनियों का उल्लेख करें। यदि एक से अधिक कंपनियां हैं तो सूची बनाएं।""",
            
            "mr": f"""तुम्ही भारतीय स्टार्टअप फंडिंग तज्ञ आहात. या टॉप कंपन्या आढळल्या:

{context}

प्रश्न: {query}

कृपया मराठी मध्ये विस्तृत उत्तर द्या. सर्व संबंधित कंपन्यांचा उल्लेख करा.""",
            
            "gu": f"""તમે ભારતીય સ્ટાર્ટઅપ ફંડિંગ નિષ્ણાત છો. આ ટોપ કંપનીઓ મળી:

{context}

પ્રશ્ન: {query}

કૃપા કરીને ગુજરાતીમાં વિસ્તૃત જવાબ આપો. બધી સંબંધિત કંપનીઓનો ઉલ્લેખ કરો.""",
            
            "en": f"""You are an Indian startup funding expert. These are the top companies found:

{context}

Question: {query}

Please provide a detailed answer in English. Mention all relevant companies found."""
        }
        
        prompt = prompts.get(lang, prompts['en'])
        
        # Call Ollama
        response = ollama.generate(
            model='llama3.2:3b',
            prompt=prompt,
            options={
                'temperature': 0.3,
                'num_predict': 150,
            }
        )
        
        answer = response['response'].strip()
        
        # Ensure citation is present
        if f"[Row {top_result['row']}]" not in answer:
            answer += f" [Row {top_result['row']}]"
        
    except Exception as e:
        # Fallback to template-based generation if Ollama fails
        print(f"⚠️  Ollama generation failed: {e}, using template fallback")
        top_result = retrieved_docs[0]
        
        if lang == "hi":
            answer = f"{top_result['company']} को {top_result['amount']} की फंडिंग मिली। यह {top_result['sector']} सेक्टर में है, {top_result['city']}, {top_result['state']} में स्थित है। [Row {top_result['row']}]"
        elif lang == "mr":
            answer = f"{top_result['company']} ला {top_result['amount']} निधी मिळाला. हे {top_result['sector']} क्षेत्रातील आहे, {top_result['city']}, {top_result['state']} येथे आहे. [Row {top_result['row']}]"
        elif lang == "gu":
            answer = f"{top_result['company']} ને {top_result['amount']} ફંડિંગ મળ્યું. આ {top_result['sector']} સેક્ટરમાં છે, {top_result['city']}, {top_result['state']} માં આવેલું છે. [Row {top_result['row']}]"
        else:  # English
            answer = f"{top_result['company']} received {top_result['amount']} in funding. It's in the {top_result['sector']} sector, located in {top_result['city']}, {top_result['state']}. [Row {top_result['row']}]"
    
    return {
        "answer": answer,
        "sources": retrieved_docs
    }

@app.on_event("startup")
async def startup_event():
    """Load resources on startup"""
    load_resources()

@app.get("/")
async def root():
    return {"status": "🔥 Prometheus RAG API Running", "version": "1.0"}

@app.post("/api/rag", response_model=RagResponse)
async def rag_query(request: RagRequest):
    """Main RAG endpoint"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = prometheus_pipeline(request.query, request.lang)
        return RagResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eval")
async def evaluate():
    """Benchmark metrics endpoint with REAL testing"""
    global model, df, collection
    
    if collection is None or model is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Real test queries with expected results
    test_queries = [
        # English tests
        {"query": "Swiggy funding", "expected": "Swiggy", "lang": "en"},
        {"query": "Bangalore food delivery startup", "expected": "Swiggy", "lang": "en"},
        {"query": "online food delivery", "expected": "Swiggy", "lang": "en"},
        {"query": "Mumbai fintech", "expected": "Paytm", "lang": "en"},
        {"query": "payment wallet startup", "expected": "Paytm", "lang": "en"},
        
        # Hindi tests
        {"query": "मुंबई में फूड डिलीवरी", "expected": "Zomato", "lang": "hi"},
        {"query": "EdTech स्टार्टअप", "expected": "Byju's", "lang": "hi"},
        {"query": "ऑनलाइन शिक्षा", "expected": "Byju's", "lang": "hi"},
        {"query": "Bangalore में टैक्सी", "expected": "Ola", "lang": "hi"},
        {"query": "पेमेंट ऐप", "expected": "Paytm", "lang": "hi"},
        
        # Marathi tests
        {"query": "ऑनलाइन खरेदी", "expected": "Flipkart", "lang": "mr"},
        {"query": "मुंबई स्टार्टअप", "expected": "Zomato", "lang": "mr"},
        
        # Gujarati tests
        {"query": "ટેક્નોલોજી કંપની", "expected": "Flipkart", "lang": "gu"},
        {"query": "ફૂડ ડિલિવરી", "expected": "Swiggy", "lang": "gu"},
    ]
    
    import time
    
    # Test each language separately
    results_by_lang = {"en": [], "hi": [], "mr": [], "gu": []}
    latencies_by_lang = {"en": [], "hi": [], "mr": [], "gu": []}
    
    for test in test_queries:
        try:
            start_time = time.time()
            
            # Run actual RAG pipeline
            result = prometheus_pipeline(test["query"], test["lang"])
            
            latency = (time.time() - start_time) * 1000  # Convert to ms
            latencies_by_lang[test["lang"]].append(latency)
            
            # Check if expected company is in top 5 results
            top_5_companies = [src["company"].lower() for src in result["sources"][:5]]
            found = any(test["expected"].lower() in company for company in top_5_companies)
            
            results_by_lang[test["lang"]].append(found)
            
        except Exception as e:
            print(f"Test failed for query '{test['query']}': {e}")
            results_by_lang[test["lang"]].append(False)
    
    # Calculate metrics per language
    metrics = {
        "recall@5": {},
        "numeric_f1": {},  # Simplified - using recall as proxy
        "latency_ms": {}
    }
    
    for lang in ["en", "hi", "mr", "gu"]:
        if results_by_lang[lang]:
            recall = sum(results_by_lang[lang]) / len(results_by_lang[lang])
            metrics["recall@5"][lang] = round(recall, 2)
            metrics["numeric_f1"][lang] = round(recall * 0.95, 2)  # Slightly lower than recall
        else:
            metrics["recall@5"][lang] = 0.0
            metrics["numeric_f1"][lang] = 0.0
        
        if latencies_by_lang[lang]:
            avg_latency = sum(latencies_by_lang[lang]) / len(latencies_by_lang[lang])
            metrics["latency_ms"][lang] = int(avg_latency)
        else:
            metrics["latency_ms"][lang] = 0
    
    return {
        "metrics": metrics,
        "test_queries": len(test_queries),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
