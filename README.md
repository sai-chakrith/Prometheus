# 🔥 Prometheus - Multilingual RAG System for Indian Startup Funding

<div align="center">

![Prometheus Logo](https://img.shields.io/badge/Prometheus-AI%20Powered-purple?style=for-the-badge&logo=sparkles)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)

**Ask questions about Indian startup funding in 8 languages and get intelligent, context-aware answers.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-endpoints) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### 🗣️ Multilingual Support (8 Languages)
| Language | Native Name | Code |
|----------|-------------|------|
| English | English | `en` |
| Hindi | हिन्दी | `hi` |
| Tamil | தமிழ் | `ta` |
| Telugu | తెలుగు | `te` |
| Kannada | ಕನ್ನಡ | `kn` |
| Marathi | मराठी | `mr` |
| Gujarati | ગુજરાતી | `gu` |
| Bengali | বাংলা | `bn` |

### 🤖 AI-Powered RAG Pipeline
- **ChromaDB** vector store with 23,000+ funding records
- **Sentence Transformers** (paraphrase-multilingual-mpnet-base-v2) for embeddings
- **Ollama LLM** (llama3.1:8b) for intelligent response generation
- Smart query understanding - works like ChatGPT for any funding question

### 🎨 Modern UI/UX
- **Dark/Light Theme** toggle with smooth transitions
- **Voice Input** support via Web Speech API
- **Real-time Chat** interface with typing indicators
- **Responsive Design** for desktop and mobile

### 📊 Analytics Dashboard
- **Investor Details** - Top funded sectors and cities
- **Funding Trends** - Year-wise analysis
- **Policy Support** - Government initiatives overview

---

## 🖼️ Demo

### Chat Interface
Ask questions like:
- "Top 10 fintech companies in Bangalore"
- "2024 में एडटेक की कुल फंडिंग कितनी थी?" (Hindi)
- "బెంగళూరు లో టాప్ స్టార్టప్స్" (Telugu)
- "Total funding in healthcare sector"

### Insights Dashboard
View comprehensive analytics on:
- Sector-wise funding distribution
- City-wise investment patterns
- Year-over-year growth trends

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (with llama3.1:8b model)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/Prasanna070705/Prometheus.git
cd Prometheus

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
cd prometheus-ui/backend
pip install -r requirements.txt

# Start Ollama (in separate terminal)
ollama serve
ollama pull llama3.1:8b

# Run the backend
python main.py
```

### Frontend Setup

```bash
# In a new terminal
cd prometheus-ui/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Deployment

```bash
cd prometheus-ui
docker-compose up -d
```

### Access the Application
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

---

## 📁 Project Structure

```
Prometheus/
├── prometheus-ui/
│   ├── backend/
│   │   ├── main.py              # FastAPI server & RAG pipeline
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # SQLite database setup
│   │   ├── security.py          # Authentication & JWT
│   │   ├── chroma_db/           # Vector store data
│   │   ├── routes/              # API route handlers
│   │   │   ├── auth.py          # Authentication routes
│   │   │   ├── chat.py          # Chat routes
│   │   │   ├── rag.py           # RAG query routes
│   │   │   └── health.py        # Health check routes
│   │   ├── services/            # Business logic services
│   │   │   ├── rag_service.py   # RAG pipeline logic
│   │   │   ├── cache_service.py # Caching layer
│   │   │   └── whisper_service.py # Speech-to-text
│   │   └── models/              # Pydantic schemas
│   │
│   └── frontend/
│       ├── src/
│       │   ├── PrometheusApp.jsx    # Main application
│       │   ├── Insights.jsx         # Analytics dashboard
│       │   ├── Auth.jsx             # Authentication
│       │   ├── ChatHistoryOptimized.jsx # Chat history
│       │   ├── components/          # Reusable components
│       │   │   ├── chat/            # Chat components
│       │   │   └── layout/          # Layout components
│       │   ├── hooks/               # Custom React hooks
│       │   │   └── useSpeechRecognition.js
│       │   └── constants/           # Language configs
│       │       └── languages.js
│       ├── package.json
│       └── vite.config.js
│
├── dataset/
│   ├── cleaned_funding_synthetic_2010_2025.csv
│   ├── cleaned_funding_synthetic_2010_2025_extended.csv
│   └── DATASET_README.md
│
├── scripts/
│   ├── quick_test.py            # Test script for API
│   └── check_db.py              # Database verification
│
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
```http
POST /api/signup
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword"
}
```

```http
POST /api/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword"
}
```

### RAG Query
```http
POST /api/rag
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "Top 10 fintech startups in Bangalore",
  "language": "en"
}
```

### Chat History
```http
GET /api/chat-history
Authorization: Bearer <token>
```

```http
POST /api/save-chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "User question",
  "response": "AI response",
  "language": "en"
}
```

### Insights
```http
GET /api/insights
```

### Health Check
```http
GET /health
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.1:8b` | LLM model for response generation |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `JWT_SECRET` | Auto-generated | Secret key for JWT tokens |
| `DATABASE_URL` | `sqlite:///./prometheus.db` | Database connection string |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage location |

### Dataset Columns

| Column | Description |
|--------|-------------|
| `Startup Name` | Name of the startup |
| `Amount_Cleaned` | Funding amount in crores |
| `Sector_Standardized` | Industry sector |
| `City` | Headquarters city |
| `State_Standardized` | State/region |
| `Investors' Name` | Lead investors |
| `Date_Parsed` | Funding date |
| `Year` | Funding year |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | High-performance async web framework |
| ChromaDB | Vector database for embeddings |
| Sentence Transformers | Multilingual text embeddings |
| Ollama | Local LLM inference |
| SQLite | User data & chat history |
| JWT | Authentication tokens |
| Pydantic | Data validation |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| TailwindCSS | Styling |
| Framer Motion | Animations |
| TanStack Query | Data fetching & caching |
| Lucide Icons | Icon library |
| Web Speech API | Voice input |

---

## 🎯 Example Queries

| Language | Query | Expected Response |
|----------|-------|-------------------|
| English | "Top 10 companies by funding" | List of 10 highest funded companies |
| English | "Total funding in Bangalore" | Aggregated sum with company count |
| Hindi | "2024 में फिनटेक कंपनियां" | Fintech companies from 2024 |
| Hindi | "बैंगलोर में कुल फंडिंग" | Total Bangalore funding |
| Telugu | "టాప్ 5 హెల్త్‌కేర్ స్టార్టప్స్" | Top 5 healthcare startups |
| Tamil | "எட்டெக் நிதி காட்டு" | EdTech sector funding |

---

## 🧪 Testing

### Run Quick Tests
```bash
cd scripts
python quick_test.py
```

### Test Individual Languages
```python
import requests

response = requests.post(
    "http://localhost:8000/api/rag",
    json={"query": "Top 5 startups", "language": "en"}
)
print(response.json())
```

---

## 🐳 Docker Deployment

### Build and Run
```bash
cd prometheus-ui
docker-compose up -d --build
```

### Services
| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI server |
| frontend | 80 | Nginx serving React |

### Stop Services
```bash
docker-compose down
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit changes
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. Push to branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write meaningful commit messages
- Add tests for new features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Prasanna** - [GitHub](https://github.com/Prasanna070705)

---

## 🙏 Acknowledgments

- Indian Startup Funding Dataset contributors
- Ollama team for local LLM inference
- ChromaDB for vector storage
- Sentence Transformers for multilingual embeddings
- FastAPI for the excellent web framework

---

<div align="center">

**Built with ❤️ for the Indian Startup Ecosystem**

⭐ **Star this repo if you find it useful!** ⭐

[![GitHub stars](https://img.shields.io/github/stars/Prasanna070705/Prometheus?style=social)](https://github.com/Prasanna070705/Prometheus/stargazers)

</div>
