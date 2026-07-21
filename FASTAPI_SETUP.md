# RAG Chatbot V2 - FastAPI Integration Guide

## 📋 Project Structure

```
RAG_Project_V3.0/
├── api.py                          # ⭐ NEW: Main FastAPI application
├── start_api.py                    # ⭐ NEW: API startup script
├── client_example.py               # ⭐ NEW: Example Python client
├── Dockerfile                      # ⭐ NEW: Docker container config
├── docker-compose.yml              # ⭐ NEW: Docker Compose config
├── API_README.md                   # ⭐ NEW: Comprehensive API documentation
│
├── requirements.txt                # ✏️ UPDATED: Added FastAPI, uvicorn, etc.
├── app/
│   └── main.py                     # Streamlit UI (alternative to FastAPI)
│
├── backend/
│   ├── __init__.py
│   ├── rag_pipeline.py             # Core LangGraph pipeline
│   ├── state.py                    # Agent state definition
│   ├── memory.py                   # Chat memory management
│   ├── pipeline_manager.py         # ⭐ NEW: Pipeline lifecycle manager
│   ├── embeddings.py
│   ├── vectorstore.py
│   ├── llm.py
│   ├── loader.py
│   ├── splitter.py
│   ├── retriever.py
│   ├── router.py
│   ├── web_search.py
│   ├── export.py
│   ├── nodes/
│   │   ├── supervisor_node.py
│   │   ├── rag_node.py
│   │   ├── web_node.py
│   │   ├── analyst_node.py
│   │   ├── casual_node.py
│   │   ├── followup_node.py
│   │   └── memory_node.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── prompts.py
│   └── ...
│
├── data/
│   └── raw/                        # Store PDFs here
│
├── storage/
│   └── vector_db/                  # FAISS vector index
│
└── test_rag.py                     # CLI test script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- GROQ_API_KEY environment variable set
- pip or conda

### Option 1: Run Locally (Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variable
export GROQ_API_KEY="your_api_key_here"  # Linux/Mac
# OR
set GROQ_API_KEY=your_api_key_here      # Windows CMD
# OR
$env:GROQ_API_KEY="your_api_key_here"   # Windows PowerShell

# 3. Start the API
python start_api.py

# 4. Access in browser
# Documentation: http://localhost:8000/docs
# API Root: http://localhost:8000
```

### Option 2: Run with Docker

```bash
# 1. Create .env file with GROQ_API_KEY

# 2. Build and start
docker-compose up --build

# 3. Access in browser
# http://localhost:8000/docs
```

### Option 3: Run with Uvicorn (Advanced)

```bash
# Development mode with auto-reload
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Endpoints Summary

### Initialization
- `POST /api/initialize` - Initialize RAG pipeline
- `GET /api/pipeline-info` - Get pipeline configuration

### File Management
- `POST /api/upload` - Upload PDF file

### Question Answering
- `POST /api/ask` - Ask single question
- `POST /api/batch-ask` - Ask multiple questions

### Monitoring
- `GET /` - Root status
- `GET /health` - Health check
- `GET /status` - Pipeline status

### Export
- `POST /api/export` - Export conversation to PDF

## 🔧 Configuration

### Environment Variables (.env)
```env
GROQ_API_KEY=your_api_key_here
LLM_MODEL_NAME=llama-3.3-70b-versatile
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### FastAPI Settings
See `api.py` for:
- CORS configuration
- Request/Response models
- Pipeline state management

## 📚 Usage Examples

### Using cURL

```bash
# 1. Initialize pipeline
curl -X POST "http://localhost:8000/api/initialize" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": false}'

# 2. Ask a question
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?"}'

# 3. Check status
curl "http://localhost:8000/status"
```

### Using Python

```python
import requests

# Initialize
requests.post("http://localhost:8000/api/initialize", 
              json={"force_rebuild": False})

# Ask question
response = requests.post("http://localhost:8000/api/ask",
                        json={"question": "Hello!"})
print(response.json())
```

### Using Python Client

```bash
# Run example client
python client_example.py
```

## 🧪 Testing

### Interactive API Docs
Open: http://localhost:8000/docs
- Try endpoints directly in browser
- See request/response schemas
- Real-time API testing

### Alternative Documentation
http://localhost:8000/redoc

### Test Pipeline
```bash
python test_rag.py  # Original CLI test
```

## 🔍 Monitoring & Debugging

### View Logs
```bash
# Direct run
python start_api.py

# Docker
docker-compose logs rag-api

# Docker (follow logs)
docker-compose logs -f rag-api
```

### Check Pipeline Status
```bash
curl http://localhost:8000/status
```

### Get Pipeline Info
```bash
curl http://localhost:8000/api/pipeline-info
```

## ⚙️ Advanced Usage

### Multi-Agent Architecture

The API wraps a LangGraph multi-agent system:

1. **Supervisor Agent** - Routes questions to appropriate agent
2. **RAG Agent** - Answers from PDFs
3. **Web Agent** - Searches the web
4. **Analyst Agent** - Analyzes documents
5. **Casual Agent** - Handles small talk
6. **FollowUp Agent** - Generates follow-up questions
7. **Memory Agent** - Manages conversation history

### Response Sources

- **PDF** - Answer from uploaded PDFs (RAG)
- **Web** - Answer from web search
- **Analyst** - Analysis or summary
- **Chat** - Small talk response

### Custom Workflows

See `client_example.py` for:
- Basic usage
- PDF workflow
- Batch questions
- Interactive chat
- Pipeline info

## 🐛 Troubleshooting

### API won't start
- Check GROQ_API_KEY is set
- Check port 8000 is not in use
- Run: `python start_api.py`

### Pipeline initialization fails
- Verify GROQ_API_KEY
- Check internet connection
- Look for error in logs

### File upload fails
- Ensure file is valid PDF
- Check `data/raw/` directory exists
- Check file permissions

### Slow responses
- First request initializes LLM (normal)
- Check network connection
- Monitor available memory

## 📖 Documentation

- **API Docs**: [API_README.md](API_README.md)
- **API Interactive**: http://localhost:8000/docs
- **Example Code**: [client_example.py](client_example.py)
- **Config**: [config/settings.py](config/settings.py)

## 🚢 Deployment

### Development
```bash
python start_api.py
```

### Production with Docker
```bash
docker-compose up -d
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api:app
```

### Cloud Deployment
- AWS ECS, Lambda
- Google Cloud Run
- Azure Container Instances
- Heroku (with Procfile)

## 📝 Key Features Added

✅ **Complete REST API** - Full FastAPI implementation
✅ **Multiple Endpoints** - Initialize, upload, ask, batch, export
✅ **Error Handling** - Comprehensive error responses
✅ **CORS Support** - Access from any origin
✅ **Async Support** - File uploads with async/await
✅ **Interactive Docs** - Swagger UI at /docs
✅ **Pipeline Manager** - Thread-safe lifecycle management
✅ **Docker Ready** - Dockerfile and docker-compose included
✅ **Example Client** - Python client with examples
✅ **Batch Processing** - Ask multiple questions at once

## 🔗 API Architecture

```
Client (Browser/Python/Mobile)
           ↓
    FastAPI (api.py)
           ↓
    Pipeline Manager (backend/pipeline_manager.py)
           ↓
    LangGraph Pipeline (backend/rag_pipeline.py)
           ↓
    ┌──────────────────────────────────┐
    │    Multi-Agent System            │
    │  ┌────────────────────────────┐  │
    │  │   Supervisor Agent         │  │
    │  └──┬──┬──┬──────────────────┘  │
    │     │  │  └─ Casual Agent       │
    │  ┌──┴──┴────────────────────┐   │
    │  ├─ RAG Agent               │   │
    │  ├─ Web Agent               │   │
    │  ├─ Analyst Agent           │   │
    │  └─ FollowUp Agent          │   │
    │  └─ Memory Agent            │   │
    └──────────────────────────────────┘
           ↓
    ┌──────────────────────────────────┐
    │    Vector Store & External APIs  │
    │  • FAISS (Vector DB)             │
    │  • Groq LLM                      │
    │  • Web Search                    │
    └──────────────────────────────────┘
```

## 🎯 Next Steps

1. **Install** - Follow Quick Start
2. **Test** - Use /docs interface
3. **Integrate** - Use client_example.py as template
4. **Deploy** - Use docker-compose for production
5. **Monitor** - Check /status and /health endpoints

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Test endpoint: `http://localhost:8000/docs`
3. Review examples: [client_example.py](client_example.py)
4. Check config: [config/settings.py](config/settings.py)

---

**Version**: 2.0.0 (FastAPI Edition)
**Last Updated**: 2024
**Status**: Production Ready
