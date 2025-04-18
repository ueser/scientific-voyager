"""
LLM Interface Module

This module defines the abstract interface for LLM clients in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class ILLMClient(ABC):
    """
    Interface for Large Language Model clients.
    Defines the contract for interacting with LLMs for various NLP tasks.
    """

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for
            system_message: Optional system message to guide the model's behavior
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            Generated text
            
        Raises:
            ValueError: If the prompt is invalid
            ConnectionError: If there's an issue connecting to the LLM service
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def extract_statements(self, text: str) -> List[Dict]:
        """
        Extract statements from scientific text.
        
        Args:
            text: Scientific text to extract statements from
            
        Returns:
            List of extracted statements with metadata
            
        Raises:
            ValueError: If the text is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def categorize_statement(self, statement: str) -> Dict:
        """
        Categorize a scientific statement by type and biological level.
        
        Args:
            statement: The statement to categorize
            
        Returns:
            Dictionary with categorization information
            
        Raises:
            ValueError: If the statement is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def generate_insights(
        self,
        statements: List[Dict],
        overarching_goal: str,
        focus_area: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate insights from a collection of scientific statements.
        
        Args:
            statements: List of scientific statements with metadata
            overarching_goal: The main scientific goal guiding exploration
            focus_area: Optional focus area to limit insight generation
            
        Returns:
            List of generated insights with metadata
            
        Raises:
            ValueError: If statements list is empty or invalid
            Exception: For other unexpected errors
        """
        pass
