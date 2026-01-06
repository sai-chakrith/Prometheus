# Prometheus

AI-powered startup funding intelligence in 8 Indian languages.

## Features

- **8 Languages** - Hindi, Tamil, Telugu, Kannada, Marathi, Gujarati, Bengali, English
- **23K+ Companies** - Indian startup funding data (2010-2025)
- **AI-Powered** - Ollama Llama 3.1 with ChromaDB vector search
- **Voice Input** - Multilingual speech recognition
- **Smart Search** - Semantic search with reranking
- **Chat History** - Persistent conversations with search

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (llama3.1:8b model)

### Backend
```bash
cd prometheus-ui/backend
pip install -r requirements.txt
python main.py
```
Runs on http://localhost:8000

### Frontend
```bash
cd prometheus-ui/frontend
npm install
npm run dev
```
Runs on http://localhost:3000

### Docker
```bash
docker-compose up -d
```

## Tech Stack

**Backend:** FastAPI, Ollama, ChromaDB, SQLite, Whisper  
**Frontend:** React 18, Vite, Framer Motion, TailwindCSS

## API Endpoints

- `POST /api/signup` - Create account
- `POST /api/login` - Login
- `POST /api/rag` - Query AI
- `GET /api/chat-history` - Get history
- `GET /api/insights` - Analytics

## License

MIT
