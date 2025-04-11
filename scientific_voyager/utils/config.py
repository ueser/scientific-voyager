"""
Configuration Module

This module handles configuration settings for the Scientific Voyager platform,
including environment variables and API keys.
"""

import os
from typing import Dict, Optional, Any


class Config:
    """
    Configuration manager for the Scientific Voyager platform.
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            env_file: Optional path to .env file
        """
        self.config = {}
        self._load_environment(env_file)
        
    def _load_environment(self, env_file: Optional[str] = None) -> None:
        """
        Load environment variables from .env file if available.
        
        Args:
            env_file: Optional path to .env file
        """
        # Environment variables are already loaded by the application
        # This is just a placeholder for future implementation if needed
        pass
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        # First check if the value is in the config dictionary
        if key in self.config:
            return self.config[key]
            
        # Then check environment variables
        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value
            
        # Finally return the default value
        return default
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        
    def get_openai_api_key(self) -> Optional[str]:
        """
        Get the OpenAI API key.
        
        Returns:
            OpenAI API key or None if not found
        """
        return self.get("OPENAI_API_KEY")
        
    def get_model_name(self, default: str = "gpt-4o") -> str:
        """
        Get the model name to use.
        
        Args:
            default: Default model name if not configured
            
        Returns:
            Model name
        """
        return self.get("OPENAI_MODEL", default)
        
    def get_pubmed_api_key(self) -> Optional[str]:
        """
        Get the PubMed API key.
        
        Returns:
            PubMed API key or None if not found
        """
        return self.get("PUBMED_API_KEY")
        
    def get_neo4j_connection_info(self) -> Dict[str, str]:
        """
        Get Neo4j connection information.
        
        Returns:
            Dictionary with Neo4j connection information
        """
        return {
            "uri": self.get("NEO4J_URI", "bolt://localhost:7687"),
            "username": self.get("NEO4J_USERNAME", "neo4j"),
            "password": self.get("NEO4J_PASSWORD", "")
        }
        
    def get_chroma_connection_info(self) -> Dict[str, Any]:
        """
        Get ChromaDB connection information.
        
        Returns:
            Dictionary with ChromaDB connection information
        """
        return {
            "host": self.get("CHROMA_HOST", "localhost"),
            "port": int(self.get("CHROMA_PORT", "8000")),
            "collection_name": self.get("CHROMA_COLLECTION", "scientific_voyager")
        }
