# RAG Chatbot V2 - FastAPI Documentation

## Overview

This is a FastAPI wrapper for the RAG Chatbot V2 multi-agent system. The API provides RESTful endpoints for:
- **Initializing** the RAG pipeline
- **Uploading** PDF documents
- **Asking questions** to the chatbot
- **Exporting** conversation history
- **Monitoring** pipeline status

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  (HTTP Endpoints, Request/Response Handling, CORS)          │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴────────────┐
         │  Pipeline Manager      │
         │  (Lifecycle, Caching)  │
         └───────────┬────────────┘
                     │
         ┌───────────┴────────────────────────────────────────┐
         │        LangGraph Multi-Agent System                │
         │  ┌─────────┬──────────┬──────────┬──────────┐      │
         │  │Supervisor│   RAG   │   Web    │ Analyst  │      │
         │  │  Node    │  Node   │  Node    │  Node    │      │
         │  └────┬────┴─────┬────┴────┬────┴────┬─────┘      │
         │       │FollowUp ├─ Memory ├─ Casual │            │
         │       └─────────┴─────────┴─────────┘             │
         └───────────────────────────────────────────────────┘
```

## Getting Started

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use Docker
docker-compose up --build
```

### 2. Set Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Start the API

**Option A: Direct Python**
```bash
python start_api.py
```

**Option B: Using Uvicorn**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Option C: Docker**
```bash
docker-compose up
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health & Status

#### `GET /` 
Root endpoint - returns API status

**Response:**
```json
{
  "message": "RAG Chatbot V2 API",
  "status": "online",
  "docs": "/docs",
  "pipeline_ready": false
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "pipeline_ready": false,
  "error": null
}
```

#### `GET /status`
Get pipeline status

**Response:**
```json
{
  "ready": false,
  "error": null
}
```

### Pipeline Management

#### `POST /api/initialize`
Initialize and build the RAG pipeline

**Request:**
```json
{
  "force_rebuild": false
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Pipeline initialized successfully",
  "ready": true
}
```

**Response (Error):**
```json
{
  "error": "Pipeline initialization failed: ...",
  "status_code": 500
}
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/api/initialize" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": false}'
```

#### `GET /api/pipeline-info`
Get pipeline configuration and capabilities

**Response:**
```json
{
  "ready": true,
  "agents": ["Supervisor", "RAG", "Web", "Analyst", "Casual", "FollowUp", "Memory"],
  "capabilities": [
    "PDF Question Answering (RAG)",
    "Web Search",
    "Document Analysis",
    "Casual Conversation",
    "Conversation Memory",
    "Follow-up Suggestions"
  ],
  "models": {
    "llm": "llama-3.3-70b-versatile (Groq)",
    "embeddings": "all-MiniLM-L6-v2"
  }
}
```

### File Management

#### `POST /api/upload`
Upload a PDF file for processing

**Request:**
- Content-Type: `multipart/form-data`
- File field: `file` (PDF file)

**Response (Success):**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "message": "File 'document.pdf' uploaded successfully. Call /api/initialize with force_rebuild=true to re-index."
}
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/document.pdf"
```

### Question Answering

#### `POST /api/ask`
Ask a question to the chatbot

**Request:**
```json
{
  "question": "What is the document about?"
}
```

**Response (Success):**
```json
{
  "question": "What is the document about?",
  "answer": "Based on the document, it discusses...",
  "source": "PDF",
  "details": [
    {
      "source": "document.pdf",
      "page": 5
    }
  ],
  "followups": [
    "Can you explain more about...",
    "How does this relate to...",
    "What are the implications of..."
  ]
}
```

**Response (Not Initialized):**
```json
{
  "error": "Pipeline not initialized. Call /api/initialize first.",
  "status_code": 503
}
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

#### `POST /api/batch-ask`
Ask multiple questions in a single request

**Request:**
```json
{
  "questions": [
    "What is the main topic?",
    "Who is the author?",
    "What are the key findings?"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "question": "What is the main topic?",
      "answer": "The main topic is...",
      "source": "PDF",
      "error": null
    },
    {
      "question": "Who is the author?",
      "answer": "The author is...",
      "source": "PDF",
      "error": null
    },
    {
      "question": "What are the key findings?",
      "answer": "The key findings include...",
      "source": "PDF",
      "error": null
    }
  ],
  "total": 3
}
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/api/batch-ask" \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "What is the main topic?",
      "What are the key findings?"
    ]
  }'
```

### Export

#### `POST /api/export`
Export conversation to PDF

**Request:**
```json
{
  "title": "Chat History",
  "filename": "chat_export.pdf"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Export functionality can be integrated"
}
```

## Common Workflows

### Workflow 1: Complete Q&A Flow

```bash
# 1. Initialize pipeline
curl -X POST "http://localhost:8000/api/initialize" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": false}'

# 2. Upload PDF (optional)
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"

# 3. Reinitialize if new PDF uploaded
curl -X POST "http://localhost:8000/api/initialize" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": true}'

# 4. Ask questions
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?"}'

# 5. Export conversation
curl -X POST "http://localhost:8000/api/export" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Chat", "filename": "export.pdf"}'
```

### Workflow 2: Programmatic Usage (Python)

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Initialize
response = requests.post(f"{BASE_URL}/initialize", json={"force_rebuild": False})
print(response.json())

# Ask questions
response = requests.post(f"{BASE_URL}/ask", json={"question": "What is the document about?"})
answer_data = response.json()
print(f"Answer: {answer_data['answer']}")
print(f"Source: {answer_data['source']}")

# Batch questions
response = requests.post(f"{BASE_URL}/batch-ask", json={
    "questions": ["Question 1?", "Question 2?"]
})
for result in response.json()["results"]:
    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}")
```

### Workflow 3: Using Docker

```bash
# Build and start
docker-compose up --build

# In another terminal, interact with API
curl http://localhost:8000/health

# To stop
docker-compose down
```

## Response Types

### Source Types
- **PDF**: Question answered from uploaded PDF documents
- **Web**: Question answered using web search
- **Analyst**: Analytical response or document analysis
- **Chat**: Casual conversation or greeting

### Agent Types
- **Supervisor**: Routes questions to appropriate agent
- **RAG Agent**: Answers from PDF documents
- **Web Agent**: Searches the web for information
- **Analyst Agent**: Performs document analysis and summaries
- **Casual Agent**: Handles greetings and small talk
- **FollowUp Agent**: Generates follow-up questions
- **Memory Agent**: Manages conversation history

## Error Handling

### Common Errors

| Status Code | Description | Solution |
|---|---|---|
| 400 | Bad Request | Check request JSON format |
| 503 | Service Unavailable | Call `/api/initialize` first |
| 500 | Internal Server Error | Check logs and retry |

### Error Response Format

```json
{
  "error": "Error message",
  "status_code": 500
}
```

## Configuration

### Environment Variables (in `.env`)

```env
GROQ_API_KEY=your_api_key_here
LLM_MODEL_NAME=llama-3.3-70b-versatile
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_MEMORY_MESSAGES=10
NUM_FOLLOWUP_QUESTIONS=3
WEB_SEARCH_MAX_RESULTS=5
RELEVANCE_THRESHOLD=0.45
```

### Settings

See `config/settings.py` for configuration:
- Chunk size and overlap for document splitting
- Vector database location
- LLM model selection
- Memory limits
- Web search settings

## Performance Considerations

1. **First Initialization**: Takes longer due to building vector index
2. **Subsequent Requests**: Much faster due to caching
3. **Large Files**: May take time to process, consider chunking
4. **Concurrent Requests**: API handles multiple concurrent requests
5. **Memory**: FAISS vector store cached in memory after first load

## Troubleshooting

### Pipeline fails to initialize
- Check `GROQ_API_KEY` is set correctly
- Check PDF files are in `data/raw/` directory
- Check internet connection for LLM API

### Upload fails
- Ensure file is a valid PDF
- Check file permissions
- Verify `data/raw/` directory exists

### Slow responses
- First request after initialization is slower (LLM warmup)
- Check network connection
- Monitor available memory

## Development

### Run with Hot Reload
```bash
uvicorn api:app --reload
```

### Run Tests (if available)
```bash
pytest tests/
```

### View Logs
```bash
# From docker-compose
docker-compose logs rag-api

# From direct run
# Check console output
```

## Integration Examples

### FastAPI-based Web Application
See `app/main.py` for Streamlit example. Can be replaced with any web framework.

### Mobile App Integration
Call API endpoints from mobile backend:
```swift
let url = URL(string: "http://api.example.com/api/ask")
var request = URLRequest(url: url!)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
let json = ["question": "What is this document?"]
request.httpBody = try JSONSerialization.data(withJSONObject: json)
```

## Support & Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **GitHub Issues**: [Your repo]
- **Documentation**: [Your docs site]

## License

[Your License]
