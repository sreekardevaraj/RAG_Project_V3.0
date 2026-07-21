"""
Startup script for RAG Chatbot V2 FastAPI Application
Run this script to start the API server
"""

import sys
import os
import uvicorn

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  RAG Chatbot V3 - FastAPI Server Startup")
    print("="*60)
    print("\n📍 Starting API server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print("\n💡 Tip: Call POST /api/initialize first to build the pipeline")
    print("="*60 + "\n")
    
    # Start the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development)
        log_level="info"
    )
