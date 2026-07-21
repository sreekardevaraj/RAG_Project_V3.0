"""
Validation script to verify FastAPI setup is correct
"""

import sys
import os

# Add workspace to path
workspace_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, workspace_path)

def validate_imports():
    """Validate all imports work correctly"""
    print("✓ Checking imports...")
    
    try:
        from fastapi import FastAPI
        print("  ✓ FastAPI")
    except ImportError as e:
        print(f"  ✗ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print("  ✓ Uvicorn")
    except ImportError as e:
        print(f"  ✗ Uvicorn: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("  ✓ Pydantic")
    except ImportError as e:
        print(f"  ✗ Pydantic: {e}")
        return False
    
    try:
        import api
        print("  ✓ api.py")
    except ImportError as e:
        print(f"  ✗ api.py: {e}")
        return False
    
    try:
        from backend.pipeline_manager import get_pipeline_manager
        print("  ✓ pipeline_manager.py")
    except ImportError as e:
        print(f"  ✗ pipeline_manager.py: {e}")
        return False
    
    return True


def validate_api_structure():
    """Validate API structure"""
    print("\n✓ Checking API structure...")
    
    try:
        from api import app
        print("  ✓ FastAPI app instance")
        
        # Check routes
        routes = [route.path for route in app.routes]
        required_routes = [
            "/",
            "/health",
            "/status",
            "/api/initialize",
            "/api/upload",
            "/api/ask",
            "/api/batch-ask",
            "/api/pipeline-info",
            "/api/export"
        ]
        
        for route in required_routes:
            if route in routes or any(route in r for r in routes):
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} not found")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def validate_config():
    """Validate configuration"""
    print("\n✓ Checking configuration...")
    
    try:
        from config.settings import (
            GROQ_API_KEY,
            LLM_MODEL_NAME,
            EMBEDDING_MODEL_NAME,
            RAW_PDF_DIR,
            VECTOR_DB_DIR
        )
        
        if GROQ_API_KEY:
            print("  ✓ GROQ_API_KEY set")
        else:
            print("  ✗ GROQ_API_KEY not set")
        
        print(f"  ✓ LLM: {LLM_MODEL_NAME}")
        print(f"  ✓ Embeddings: {EMBEDDING_MODEL_NAME}")
        print(f"  ✓ PDF Dir: {RAW_PDF_DIR}")
        print(f"  ✓ Vector DB Dir: {VECTOR_DB_DIR}")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def validate_directories():
    """Validate required directories exist"""
    print("\n✓ Checking directories...")
    
    from config.settings import RAW_PDF_DIR, VECTOR_DB_DIR
    
    dirs = [RAW_PDF_DIR, VECTOR_DB_DIR]
    
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (creating...)")
            os.makedirs(dir_path, exist_ok=True)
            print(f"    ✓ Created")
    
    return True


def main():
    """Run all validations"""
    print("\n" + "="*60)
    print("  FastAPI RAG Chatbot V2 - Setup Validation")
    print("="*60 + "\n")
    
    results = []
    
    # Run validations
    results.append(("Imports", validate_imports()))
    results.append(("API Structure", validate_api_structure()))
    results.append(("Configuration", validate_config()))
    results.append(("Directories", validate_directories()))
    
    # Summary
    print("\n" + "="*60)
    print("  Validation Summary")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("="*60 + "\n")
    
    if all_passed:
        print("✅ All validations passed!")
        print("\n🚀 Ready to start API:")
        print("   python start_api.py\n")
        return 0
    else:
        print("❌ Some validations failed!")
        print("\nFix the issues above and try again.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
