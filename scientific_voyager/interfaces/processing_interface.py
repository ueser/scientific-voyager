"""
Processing Interface Module

This module defines the abstract interfaces for processing components
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class IStatementExtractor(ABC):
    """
    Interface for statement extraction operations.
    Defines the contract for extracting statements from scientific text.
    """

    @abstractmethod
    def extract_statements(self, text: str) -> List[Dict]:
        """
        Extract scientific statements from text.
        
        Args:
            text: Scientific text to extract statements from
            
        Returns:
            List of extracted statements with metadata
            
        Raises:
            ValueError: If text is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def batch_extract(self, texts: List[str]) -> List[List[Dict]]:
        """
        Extract statements from multiple texts.
        
        Args:
            texts: List of scientific texts to extract statements from
            
        Returns:
            List of lists of extracted statements with metadata
            
        Raises:
            ValueError: If texts list is invalid or empty
            Exception: For other unexpected errors
        """
        pass


class IProcessingPipeline(ABC):
    """
    Interface for data processing pipeline operations.
    Defines the contract for processing scientific data through multiple stages.
    """

    @abstractmethod
    def process_query(self, query: str, max_results: int = 10) -> Dict:
        """
        Process a search query through the entire pipeline.
        
        Args:
            query: Search query for scientific literature
            max_results: Maximum number of results to process
            
        Returns:
            Dictionary containing processing results and metadata
            
        Raises:
            ValueError: If query is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def process_article(self, article_id: str) -> Dict:
        """
        Process a specific article through the pipeline.
        
        Args:
            article_id: ID of the article to process
            
        Returns:
            Dictionary containing processing results and metadata
            
        Raises:
            ValueError: If article_id is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def batch_process(self, article_ids: List[str]) -> List[Dict]:
        """
        Process multiple articles through the pipeline.
        
        Args:
            article_ids: List of article IDs to process
            
        Returns:
            List of dictionaries containing processing results and metadata
            
        Raises:
            ValueError: If article_ids list is invalid or empty
            Exception: For other unexpected errors
        """
        pass
