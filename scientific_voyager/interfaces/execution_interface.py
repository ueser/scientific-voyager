"""
Execution Interface Module

This module defines the abstract interface for the execution engine
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class IExecutionEngine(ABC):
    """
    Interface for the main execution engine.
    Defines the contract for coordinating the various components of the system.
    """

    @abstractmethod
    def initialize_components(self) -> None:
        """
        Initialize all components of the execution engine.
        
        Raises:
            ValueError: If configuration is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def start_exploration(
        self,
        overarching_goal: str,
        initial_query: str,
        max_iterations: int = 5,
        focus_areas: Optional[List[str]] = None,
        biological_level: Optional[str] = None
    ) -> Dict:
        """
        Start a scientific exploration process.
        
        Args:
            overarching_goal: The main scientific goal guiding exploration
            initial_query: Initial search query to begin exploration
            max_iterations: Maximum number of exploration iterations
            focus_areas: Optional list of focus areas to guide exploration
            biological_level: Optional biological level to focus on
            
        Returns:
            Dictionary containing exploration results and metadata
            
        Raises:
            ValueError: If parameters are invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def run_iteration(self) -> Dict:
        """
        Run a single iteration of the exploration process.
        
        Returns:
            Dictionary containing iteration results and metadata
            
        Raises:
            ValueError: If exploration has not been started
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_exploration_state(self) -> Dict:
        """
        Get the current state of the exploration process.
        
        Returns:
            Dictionary containing the current exploration state
            
        Raises:
            Exception: For unexpected errors
        """
        pass
        
    @abstractmethod
    def export_results(self, output_path: str, format: str = "json") -> bool:
        """
        Export exploration results to a file.
        
        Args:
            output_path: Path to save the exported results
            format: Output format (json, csv, etc.)
            
        Returns:
            True if export was successful, False otherwise
            
        Raises:
            ValueError: If output_path or format is invalid
            Exception: For other unexpected errors
        """
        pass
