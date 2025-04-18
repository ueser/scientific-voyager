"""
Analysis Interface Module

This module defines the abstract interfaces for analysis components
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class IInsightsGenerator(ABC):
    """
    Interface for insight generation operations.
    Defines the contract for generating insights from scientific statements.
    """

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
            ValueError: If statements list is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def evaluate_insight(self, insight: Dict, statements: List[Dict]) -> Dict:
        """
        Evaluate the quality and novelty of an insight.
        
        Args:
            insight: The insight to evaluate
            statements: List of statements the insight is based on
            
        Returns:
            Evaluation results with quality metrics
            
        Raises:
            ValueError: If insight or statements are invalid
            Exception: For other unexpected errors
        """
        pass


class ITriangulationEngine(ABC):
    """
    Interface for triangulation operations.
    Defines the contract for implementing the triangulation methodology.
    """

    @abstractmethod
    def triangulate(
        self,
        statements: List[Dict],
        focus_area: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform triangulation on a set of scientific statements.
        
        Args:
            statements: List of scientific statements to triangulate
            focus_area: Optional focus area to guide triangulation
            
        Returns:
            List of triangulation results with metadata
            
        Raises:
            ValueError: If statements list is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def evaluate_triangulation(self, triangulation_result: Dict) -> Dict:
        """
        Evaluate the strength and validity of a triangulation result.
        
        Args:
            triangulation_result: The triangulation result to evaluate
            
        Returns:
            Evaluation results with strength metrics
            
        Raises:
            ValueError: If triangulation_result is invalid
            Exception: For other unexpected errors
        """
        pass


class IEmergentInsightsManager(ABC):
    """
    Interface for emergent insights management.
    Defines the contract for identifying and managing emergent insights.
    """

    @abstractmethod
    def identify_emergent_insights(
        self,
        insights: List[Dict],
        statements: List[Dict],
        hierarchical_model: Any
    ) -> List[Dict]:
        """
        Identify emergent insights across biological levels.
        
        Args:
            insights: List of insights to analyze
            statements: List of statements the insights are based on
            hierarchical_model: Hierarchical model for multi-scale analysis
            
        Returns:
            List of emergent insights with metadata
            
        Raises:
            ValueError: If insights or statements lists are invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def rank_emergent_insights(self, emergent_insights: List[Dict]) -> List[Dict]:
        """
        Rank emergent insights by novelty, significance, and evidence strength.
        
        Args:
            emergent_insights: List of emergent insights to rank
            
        Returns:
            List of ranked emergent insights with ranking scores
            
        Raises:
            ValueError: If emergent_insights list is invalid
            Exception: For other unexpected errors
        """
        pass
