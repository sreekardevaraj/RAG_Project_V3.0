"""
Pipeline Manager for FastAPI
Handles pipeline lifecycle, caching, and state management
"""

from typing import Optional, Dict, Any
import threading
from backend.rag_pipeline import build_rag_pipeline
import logging

logger = logging.getLogger(__name__)


class PipelineManager:
    """
    Manages the RAG pipeline lifecycle for FastAPI.
    
    Features:
    - Thread-safe pipeline initialization
    - Pipeline caching
    - Error tracking
    - State management
    """
    
    def __init__(self):
        self.pipeline = None
        self.ready = False
        self.error: Optional[str] = None
        self.is_initializing = False
        self._lock = threading.Lock()
    
    def initialize(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Initialize the RAG pipeline.
        
        Args:
            force_rebuild: If True, rebuilds vector index from scratch
            
        Returns:
            Dictionary with status, message, and ready flag
        """
        with self._lock:
            # Prevent multiple simultaneous initialization attempts
            if self.is_initializing:
                return {
                    "status": "initializing",
                    "message": "Pipeline initialization already in progress",
                    "ready": False
                }
            
            # Skip if already ready
            if self.ready and not force_rebuild:
                return {
                    "status": "success",
                    "message": "Pipeline already initialized",
                    "ready": True
                }
            
            self.is_initializing = True
        
        try:
            logger.info(f"[PipelineManager] Initializing pipeline (force_rebuild={force_rebuild})")
            
            # Build the pipeline
            self.pipeline = build_rag_pipeline(force_rebuild=force_rebuild)
            
            self.ready = True
            self.error = None
            
            logger.info("[PipelineManager] Pipeline initialized successfully")
            return {
                "status": "success",
                "message": "Pipeline initialized successfully",
                "ready": True
            }
        
        except Exception as e:
            error_msg = f"Pipeline initialization failed: {str(e)}"
            self.error = error_msg
            self.ready = False
            
            logger.error(f"[PipelineManager] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "ready": False
            }
        
        finally:
            with self._lock:
                self.is_initializing = False
    
    def is_ready(self) -> bool:
        """Check if pipeline is ready to use"""
        return self.ready and self.pipeline is not None
    
    def get_pipeline(self):
        """Get the pipeline instance (if ready)"""
        if not self.is_ready():
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        return self.pipeline
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "ready": self.ready,
            "initializing": self.is_initializing,
            "error": self.error
        }
    
    def reset(self):
        """Reset the pipeline"""
        with self._lock:
            self.pipeline = None
            self.ready = False
            self.error = None
            self.is_initializing = False
            logger.info("[PipelineManager] Pipeline reset")
    
    def __repr__(self) -> str:
        return f"PipelineManager(ready={self.ready}, initializing={self.is_initializing}, error={self.error})"


# Global singleton instance
_pipeline_manager: Optional[PipelineManager] = None


def get_pipeline_manager() -> PipelineManager:
    """Get or create the global pipeline manager instance"""
    global _pipeline_manager
    if _pipeline_manager is None:
        _pipeline_manager = PipelineManager()
    return _pipeline_manager
