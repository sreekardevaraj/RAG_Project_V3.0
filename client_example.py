"""
Example Python Client for RAG Chatbot V2 API
Demonstrates how to interact with the FastAPI endpoints
"""

import requests
import json
import time
from typing import List, Dict, Any
from pathlib import Path

class RAGChatbotClient:
    """Client for RAG Chatbot V2 FastAPI API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def health_check(self) -> Dict[str, Any]:
        """Check if API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        response = self.session.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()
    
    def initialize_pipeline(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Initialize the RAG pipeline"""
        payload = {"force_rebuild": force_rebuild}
        response = self.session.post(f"{self.base_url}/api/initialize", json=payload)
        response.raise_for_status()
        return response.json()
    
    def upload_pdf(self, file_path: str) -> Dict[str, Any]:
        """Upload a PDF file"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(f"{self.base_url}/api/upload", files=files)
        
        response.raise_for_status()
        return response.json()
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a single question"""
        payload = {"question": question}
        response = self.session.post(f"{self.base_url}/api/ask", json=payload)
        response.raise_for_status()
        return response.json()
    
    def batch_ask(self, questions: List[str]) -> Dict[str, Any]:
        """Ask multiple questions"""
        payload = {"questions": questions}
        response = self.session.post(f"{self.base_url}/api/batch-ask", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline information"""
        response = self.session.get(f"{self.base_url}/api/pipeline-info")
        response.raise_for_status()
        return response.json()
    
    def export_chat(self, title: str = "Chat History", filename: str = "export.pdf") -> Dict[str, Any]:
        """Export chat history to PDF"""
        payload = {
            "title": title,
            "filename": filename
        }
        response = self.session.post(f"{self.base_url}/api/export", json=payload)
        response.raise_for_status()
        return response.json()


def example_basic_usage():
    """Example: Basic usage"""
    print("\n" + "="*60)
    print("Example 1: Basic Usage")
    print("="*60)
    
    client = RAGChatbotClient()
    
    # Check health
    print("\n1️⃣  Checking API health...")
    health = client.health_check()
    print(f"   Status: {health}")
    
    # Initialize pipeline
    print("\n2️⃣  Initializing pipeline...")
    result = client.initialize_pipeline(force_rebuild=False)
    print(f"   {result['message']}")
    
    # Ask a question
    print("\n3️⃣  Asking a question...")
    answer = client.ask_question("Hello, who are you?")
    print(f"   Question: {answer['question']}")
    print(f"   Answer: {answer['answer'][:100]}...")
    print(f"   Source: {answer['source']}")


def example_pdf_workflow():
    """Example: Upload PDF and ask questions"""
    print("\n" + "="*60)
    print("Example 2: PDF Upload & Q&A Workflow")
    print("="*60)
    
    client = RAGChatbotClient()
    
    # Initialize
    print("\n1️⃣  Initializing pipeline...")
    client.initialize_pipeline()
    
    # Upload PDF
    print("\n2️⃣  Uploading PDF...")
    pdf_path = "sample.pdf"  # Change to your PDF path
    try:
        result = client.upload_pdf(pdf_path)
        print(f"   ✅ {result['message']}")
        
        # Reinitialize with force_rebuild
        print("\n3️⃣  Rebuilding index with new PDF...")
        client.initialize_pipeline(force_rebuild=True)
        
        # Ask questions about the PDF
        print("\n4️⃣  Asking questions about PDF...")
        questions = [
            "What is this document about?",
            "What are the main topics?",
            "Can you summarize it?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n   Q{i}: {question}")
            answer = client.ask_question(question)
            print(f"   A: {answer['answer'][:150]}...")
            print(f"   📎 Source: {answer['source']}")
    
    except FileNotFoundError:
        print(f"   ⚠️  PDF not found: {pdf_path}")


def example_batch_questions():
    """Example: Ask multiple questions at once"""
    print("\n" + "="*60)
    print("Example 3: Batch Questions")
    print("="*60)
    
    client = RAGChatbotClient()
    
    # Initialize
    print("\n1️⃣  Initializing pipeline...")
    client.initialize_pipeline()
    
    # Batch questions
    print("\n2️⃣  Asking multiple questions...")
    questions = [
        "What is the main topic?",
        "Who is mentioned in this document?",
        "What are the key takeaways?"
    ]
    
    result = client.batch_ask(questions)
    
    print(f"\n   Asked {result['total']} questions:")
    for i, item in enumerate(result['results'], 1):
        print(f"\n   Q{i}: {item['question']}")
        if item['error']:
            print(f"       ❌ Error: {item['error']}")
        else:
            print(f"       ✅ {item['answer'][:100]}...")
            print(f"       📍 Source: {item['source']}")


def example_pipeline_info():
    """Example: Get pipeline information"""
    print("\n" + "="*60)
    print("Example 4: Pipeline Information")
    print("="*60)
    
    client = RAGChatbotClient()
    
    print("\n1️⃣  Fetching pipeline info...")
    info = client.get_pipeline_info()
    
    print(f"\n   Agents: {', '.join(info['agents'])}")
    print(f"\n   Capabilities:")
    for cap in info['capabilities']:
        print(f"      • {cap}")
    print(f"\n   Models:")
    print(f"      • LLM: {info['models']['llm']}")
    print(f"      • Embeddings: {info['models']['embeddings']}")


def example_interactive_chat():
    """Example: Interactive chat session"""
    print("\n" + "="*60)
    print("Example 5: Interactive Chat")
    print("="*60)
    
    client = RAGChatbotClient()
    
    # Initialize
    print("\n🚀 Starting interactive session...")
    print("Type 'exit' to quit\n")
    
    try:
        client.initialize_pipeline()
        
        while True:
            question = input("You: ").strip()
            
            if question.lower() in ["exit", "quit"]:
                print("Goodbye! 👋")
                break
            
            if not question:
                continue
            
            try:
                answer = client.ask_question(question)
                print(f"\nAssistant: {answer['answer']}")
                print(f"📍 Source: {answer['source']}")
                
                if answer['followups']:
                    print("\n💡 Follow-up questions:")
                    for fu in answer['followups']:
                        print(f"   • {fu}")
                print()
            
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")


def main():
    """Run examples"""
    print("\n" + "🤖 RAG Chatbot V2 - API Client Examples" + "\n")
    
    try:
        # Uncomment examples to run
        example_basic_usage()
        example_pipeline_info()
        # example_pdf_workflow()
        # example_batch_questions()
        # example_interactive_chat()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("   Make sure the API is running: python start_api.py")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")


if __name__ == "__main__":
    main()
