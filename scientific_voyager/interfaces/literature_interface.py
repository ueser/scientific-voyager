"""
Literature Interface Module

This module defines the abstract interface for literature extraction
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class ILiteratureAdapter(ABC):
    """
    Interface for literature extraction adapters.
    Defines the contract for extracting scientific literature from various sources.
    """
    
    @abstractmethod
    def search_articles(self, 
                        query: str, 
                        max_results: int = 50, 
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None,
                        **kwargs) -> List[Dict[str, Any]]:
        """
        Search for articles matching the given query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            date_from: Start date for filtering articles
            date_to: End date for filtering articles
            **kwargs: Additional source-specific parameters
            
        Returns:
            List of article metadata dictionaries
            
        Raises:
            ConnectionError: If unable to connect to the literature source
            ValueError: If query is invalid
            Exception: For other unexpected errors
        """
        pass
    
    @abstractmethod
    def get_article_by_id(self, article_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific article by its ID.
        
        Args:
            article_id: Unique identifier for the article in the source system
            
        Returns:
            Dictionary containing article metadata
            
        Raises:
            ConnectionError: If unable to connect to the literature source
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        pass
    
    @abstractmethod
    def get_articles_by_ids(self, article_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed metadata for multiple articles by their IDs.
        
        Args:
            article_ids: List of unique identifiers for articles
            
        Returns:
            List of dictionaries containing article metadata
            
        Raises:
            ConnectionError: If unable to connect to the literature source
            ValueError: If any article_id is invalid
            Exception: For other unexpected errors
        """
        pass
    
    @abstractmethod
    def get_article_abstract(self, article_id: str) -> str:
        """
        Get the abstract text for a specific article.
        
        Args:
            article_id: Unique identifier for the article in the source system
            
        Returns:
            Abstract text as a string
            
        Raises:
            ConnectionError: If unable to connect to the literature source
            ValueError: If article_id is invalid
            KeyError: If article is not found or has no abstract
            Exception: For other unexpected errors
        """
        pass
    
    @abstractmethod
    def get_article_full_text(self, article_id: str) -> Optional[str]:
        """
        Get the full text for a specific article if available.
        
        Args:
            article_id: Unique identifier for the article in the source system
            
        Returns:
            Full text as a string if available, None otherwise
            
        Raises:
            ConnectionError: If unable to connect to the literature source
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        pass
    
    @abstractmethod
    def get_related_articles(self, article_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get articles related to the specified article.
        
        Args:
            article_id: Unique identifier for the reference article
            max_results: Maximum number of related articles to return
            
        Returns:
            List of related article metadata dictionaries
            
        Raises:
            ConnectionError: If unable to connect to the literature source
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        pass
