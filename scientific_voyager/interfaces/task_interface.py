"""
Task Interface Module

This module defines the abstract interfaces for task generation components
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class ITaskGenerator(ABC):
    """
    Interface for task generation operations.
    Defines the contract for generating research tasks based on insights.
    """

    @abstractmethod
    def generate_tasks(
        self,
        insights: List[Dict],
        overarching_goal: str,
        existing_tasks: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Generate research tasks based on insights.
        
        Args:
            insights: List of insights to generate tasks from
            overarching_goal: The main scientific goal guiding task generation
            existing_tasks: Optional list of existing tasks to avoid duplication
            
        Returns:
            List of generated tasks with metadata
            
        Raises:
            ValueError: If insights list is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def prioritize_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Prioritize research tasks based on importance and feasibility.
        
        Args:
            tasks: List of tasks to prioritize
            
        Returns:
            List of prioritized tasks with priority scores
            
        Raises:
            ValueError: If tasks list is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def evaluate_task_completion(self, task: Dict, results: Dict) -> Dict:
        """
        Evaluate the completion of a research task.
        
        Args:
            task: The task to evaluate
            results: Results from task execution
            
        Returns:
            Evaluation results with completion metrics
            
        Raises:
            ValueError: If task or results are invalid
            Exception: For other unexpected errors
        """
        pass
