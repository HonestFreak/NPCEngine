"""
Session Service Factory for creating different types of ADK SessionService instances
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    from google.adk.sessions import InMemorySessionService, DatabaseSessionService, VertexAiSessionService
    ADK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google ADK sessions not available: {e}")
    ADK_AVAILABLE = False
    # Mock classes for development
    class InMemorySessionService:
        def __init__(self, **kwargs):
            pass
    class DatabaseSessionService:
        def __init__(self, **kwargs):
            pass
    class VertexAiSessionService:
        def __init__(self, **kwargs):
            pass


class SessionServiceFactory:
    """Factory for creating different types of SessionService instances"""
    
    @staticmethod
    def create_session_service(persistence_config: Dict[str, Any]):
        """
        Create a SessionService based on persistence configuration
        
        Args:
            persistence_config: Dictionary containing persistence configuration
                - type: 'memory', 'database', or 'vertexai'
                - database_url: Database connection string (for database type)
                - vertexai_project: GCP project ID (for vertexai type)
                - vertexai_location: GCP location (for vertexai type)
                - vertexai_corpus: RAG Corpus ID (optional, for vertexai type)
        
        Returns:
            SessionService instance
        """
        if not ADK_AVAILABLE:
            logger.warning("ADK not available, returning mock InMemorySessionService")
            return InMemorySessionService()
        
        persistence_type = persistence_config.get('type', 'memory')
        
        try:
            if persistence_type == 'memory':
                logger.info("Creating InMemorySessionService")
                return InMemorySessionService()
            
            elif persistence_type == 'database':
                database_url = persistence_config.get('database_url')
                if not database_url:
                    raise ValueError("database_url is required for database persistence")
                
                logger.info(f"Creating DatabaseSessionService with URL: {database_url}")
                return DatabaseSessionService(db_url=database_url)
            
            elif persistence_type == 'vertexai':
                project_id = persistence_config.get('vertexai_project')
                location = persistence_config.get('vertexai_location', 'us-central1')
                
                if not project_id:
                    raise ValueError("vertexai_project is required for Vertex AI persistence")
                
                kwargs = {
                    'project': project_id,
                    'location': location
                }
                
                # Add RAG corpus if specified
                corpus_id = persistence_config.get('vertexai_corpus')
                if corpus_id:
                    kwargs['rag_corpus'] = f"projects/{project_id}/locations/{location}/ragCorpora/{corpus_id}"
                
                logger.info(f"Creating VertexAiSessionService with project: {project_id}, location: {location}")
                return VertexAiSessionService(**kwargs)
            
            else:
                raise ValueError(f"Unknown persistence type: {persistence_type}")
                
        except Exception as e:
            logger.error(f"Failed to create SessionService with config {persistence_config}: {e}")
            logger.warning("Falling back to InMemorySessionService")
            return InMemorySessionService()


class SessionServiceManager:
    """Manager for handling multiple session services and configurations"""
    
    def __init__(self):
        self._session_services: Dict[str, Any] = {}
        self._default_service = None
    
    def get_or_create_session_service(self, session_id: str, persistence_config: Dict[str, Any]):
        """
        Get existing session service for a session or create a new one
        
        Args:
            session_id: Unique session identifier
            persistence_config: Persistence configuration
            
        Returns:
            SessionService instance
        """
        # For now, we'll create one service per session
        # In production, you might want to pool services by configuration
        if session_id not in self._session_services:
            self._session_services[session_id] = SessionServiceFactory.create_session_service(
                persistence_config
            )
        
        return self._session_services[session_id]
    
    def get_default_session_service(self):
        """Get the default InMemory session service for backwards compatibility"""
        if self._default_service is None:
            self._default_service = SessionServiceFactory.create_session_service({'type': 'memory'})
        return self._default_service
    
    def remove_session_service(self, session_id: str):
        """Remove session service for a completed session"""
        if session_id in self._session_services:
            del self._session_services[session_id]
    
    def get_active_services_info(self) -> Dict[str, Any]:
        """Get information about active session services"""
        return {
            'active_services': len(self._session_services),
            'service_types': [type(service).__name__ for service in self._session_services.values()],
            'has_default': self._default_service is not None
        }


# Global session service manager instance
session_service_manager = SessionServiceManager() 