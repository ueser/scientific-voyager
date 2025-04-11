"""
Emergent Insights Module

This module implements functionality for identifying, analyzing, and managing
emergent insights derived from hierarchical relationships and triangulation
across scientific statements.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import logging
import uuid
from datetime import datetime

from scientific_voyager.utils.llm_client import LLMClient
from scientific_voyager.core.triangulation import TriangulationEngine


class EmergentInsightsManager:
    """
    Manages the identification, analysis, and storage of emergent insights
    derived from hierarchical relationships and triangulation.
    """

    def __init__(
        self, 
        triangulation_engine: Optional[TriangulationEngine] = None,
        llm_client: Optional[LLMClient] = None, 
        config: Optional[Dict] = None
    ):
        """
        Initialize the emergent insights manager.
        
        Args:
            triangulation_engine: Engine for triangulating across statements
            llm_client: LLM client for insight analysis
            config: Configuration dictionary
        """
        self.triangulation_engine = triangulation_engine
        self.llm_client = llm_client
        self.config = config or {}
        self.logger = logging.getLogger("scientific_voyager.emergent_insights")
        self.insights = []
        
    def generate_emergent_insights(
        self,
        statements: List[Dict],
        overarching_goal: str,
        focus_area: Optional[str] = None,
        biological_level: Optional[str] = None,
        min_confidence: float = 0.7,
        max_insights: int = 5
    ) -> List[Dict]:
        """
        Generate emergent insights through triangulation and analysis.
        
        Args:
            statements: List of scientific statements
            overarching_goal: The main scientific goal guiding exploration
            focus_area: Optional focus area to limit insight generation
            biological_level: Optional biological level to focus on
            min_confidence: Minimum confidence threshold for insights
            max_insights: Maximum number of insights to generate
            
        Returns:
            List of generated emergent insights with metadata
        """
        if not statements or len(statements) < 3:
            self.logger.warning("Insufficient statements for emergent insight generation")
            return []
            
        # Use triangulation engine if available
        if self.triangulation_engine:
            triangulation_results = self.triangulation_engine.triangulate(
                statements=statements,
                biological_level=biological_level,
                min_confidence=min_confidence,
                max_results=max_insights
            )
            
            # Convert triangulation results to insights
            insights = self._convert_triangulation_to_insights(
                triangulation_results=triangulation_results,
                statements=statements,
                overarching_goal=overarching_goal
            )
        # Fall back to LLM client if no triangulation engine
        elif self.llm_client:
            insights = self._generate_insights_with_llm(
                statements=statements,
                overarching_goal=overarching_goal,
                focus_area=focus_area,
                biological_level=biological_level,
                min_confidence=min_confidence,
                max_insights=max_insights
            )
        else:
            self.logger.warning("No triangulation engine or LLM client available")
            return []
            
        # Store the generated insights
        self.insights.extend(insights)
        return insights
        
    def _convert_triangulation_to_insights(
        self,
        triangulation_results: List[Dict],
        statements: List[Dict],
        overarching_goal: str
    ) -> List[Dict]:
        """
        Convert triangulation results to emergent insights.
        
        Args:
            triangulation_results: Results from triangulation
            statements: Original statements used for triangulation
            overarching_goal: The main scientific goal
            
        Returns:
            List of emergent insights
        """
        insights = []
        
        for result in triangulation_results:
            # Get source statements
            source_indices = result.get("statement_indices", [])
            source_statements = []
            
            for idx in source_indices:
                if 1 <= idx <= len(statements):
                    source_statements.append(statements[idx - 1])
            
            # Create insight
            insight = {
                "id": str(uuid.uuid4()),
                "text": result.get("insight", ""),
                "emergent_behavior": result.get("emergent_behavior", ""),
                "biological_level": result.get("biological_level", ""),
                "source_statements": source_statements,
                "confidence": result.get("confidence", 0.0),
                "relevance_to_goal": self._assess_relevance_to_goal(
                    result.get("insight", ""), overarching_goal
                ),
                "novelty": self._assess_novelty(result.get("insight", "")),
                "timestamp": datetime.now().isoformat(),
                "type": "triangulation"
            }
            
            insights.append(insight)
            
        return insights
        
    def _generate_insights_with_llm(
        self,
        statements: List[Dict],
        overarching_goal: str,
        focus_area: Optional[str] = None,
        biological_level: Optional[str] = None,
        min_confidence: float = 0.7,
        max_insights: int = 5
    ) -> List[Dict]:
        """
        Generate emergent insights using the LLM client.
        
        Args:
            statements: List of scientific statements
            overarching_goal: The main scientific goal
            focus_area: Optional focus area
            biological_level: Optional biological level
            min_confidence: Minimum confidence threshold
            max_insights: Maximum number of insights
            
        Returns:
            List of emergent insights
        """
        # Filter statements by biological level if specified
        if biological_level:
            filtered_statements = [s for s in statements if s.get("biological_level") == biological_level]
        else:
            filtered_statements = statements
            
        if len(filtered_statements) < 3:
            self.logger.warning(f"Insufficient statements for insight generation at level: {biological_level}")
            return []
            
        # Prepare statements for LLM prompt
        statements_text = "\n".join([
            f"{i+1}. {s.get('statement', '')}" + 
            f" (Type: {s.get('type', 'unknown')}, Level: {s.get('biological_level', 'unknown')})"
            for i, s in enumerate(filtered_statements)
        ])
        
        # Create system prompt for insight generation
        system_message = """
        You are an expert scientific insight generator. Your task is to identify emergent insights 
        by analyzing relationships across multiple scientific statements. Focus on discovering 
        hierarchical emergent behaviors in biological systems that wouldn't be obvious from 
        individual statements alone.
        
        For each insight:
        1. Identify the emergent behavior or pattern
        2. Explain how it emerges from the underlying statements
        3. Assess confidence and novelty
        4. Explain relevance to the overarching scientific goal
        
        Format your response as a JSON array of insight objects.
        """
        
        # Create user prompt for insight generation
        prompt = f"""
        Please analyze the following scientific statements and identify emergent insights 
        that reveal hierarchical emergent behaviors:
        
        {statements_text}
        
        Overarching scientific goal: {overarching_goal}
        {f"Focus area: {focus_area}" if focus_area else ""}
        
        For each insight, provide:
        - insight: The emergent scientific insight
        - emergent_behavior: Description of the hierarchical emergent behavior
        - biological_level: The biological level of the emergent behavior
        - statement_indices: List of statement indices (1-based) that support this insight
        - confidence: Your confidence in this insight (0.0 to 1.0)
        - novelty: Assessment of how novel the insight is (0.0 to 1.0)
        - relevance: Relevance to the overarching goal (0.0 to 1.0)
        - explanation: Why this insight represents an emergent behavior
        
        Limit your response to the top {max_insights} most significant insights 
        with confidence >= {min_confidence}.
        """
        
        try:
            response = self.llm_client.complete(prompt, system_message)
            # In a real implementation, we would parse the JSON response
            # For now, we'll return a placeholder
            # This would be enhanced in future tasks
            return []
        except Exception as e:
            self.logger.error(f"Error during LLM insight generation: {e}")
            return []
            
    def _assess_relevance_to_goal(self, insight: str, goal: str) -> float:
        """
        Assess the relevance of an insight to the overarching goal.
        
        Args:
            insight: The insight text
            goal: The overarching scientific goal
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not self.llm_client:
            return 0.5  # Default middle value
            
        # Create system prompt for relevance assessment
        system_message = """
        You are an expert in assessing the relevance of scientific insights to research goals.
        Your task is to determine how relevant a given insight is to an overarching scientific goal.
        
        Provide a relevance score from 0.0 (not relevant) to 1.0 (highly relevant).
        """
        
        # Create user prompt for relevance assessment
        prompt = f"""
        Please assess the relevance of this scientific insight to the overarching goal:
        
        Insight: "{insight}"
        
        Overarching goal: "{goal}"
        
        Provide a single relevance score from 0.0 (not relevant) to 1.0 (highly relevant).
        """
        
        try:
            response = self.llm_client.complete(prompt, system_message)
            # In a real implementation, we would parse the response to extract the score
            # For now, we'll return a placeholder
            return 0.5
        except Exception as e:
            self.logger.error(f"Error assessing relevance: {e}")
            return 0.5
            
    def _assess_novelty(self, insight: str) -> float:
        """
        Assess the novelty of an insight compared to existing insights.
        
        Args:
            insight: The insight text
            
        Returns:
            Novelty score (0.0 to 1.0)
        """
        if not self.insights or not self.llm_client:
            return 1.0  # If no existing insights or no LLM, assume maximum novelty
            
        # Get existing insight texts
        existing_insights = [i.get("text", "") for i in self.insights]
        
        # If there are too many existing insights, sample a subset
        if len(existing_insights) > 10:
            import random
            existing_insights = random.sample(existing_insights, 10)
            
        existing_insights_text = "\n".join([
            f"{i+1}. {text}" for i, text in enumerate(existing_insights)
        ])
        
        # Create system prompt for novelty assessment
        system_message = """
        You are an expert in assessing the novelty of scientific insights.
        Your task is to determine how novel a given insight is compared to existing insights.
        
        Provide a novelty score from 0.0 (not novel) to 1.0 (highly novel).
        """
        
        # Create user prompt for novelty assessment
        prompt = f"""
        Please assess the novelty of this new scientific insight compared to existing insights:
        
        New insight: "{insight}"
        
        Existing insights:
        {existing_insights_text}
        
        Provide a single novelty score from 0.0 (not novel) to 1.0 (highly novel).
        """
        
        try:
            response = self.llm_client.complete(prompt, system_message)
            # In a real implementation, we would parse the response to extract the score
            # For now, we'll return a placeholder
            return 0.8
        except Exception as e:
            self.logger.error(f"Error assessing novelty: {e}")
            return 0.8
            
    def get_insights(
        self,
        biological_level: Optional[str] = None,
        min_confidence: float = 0.0,
        min_relevance: float = 0.0,
        min_novelty: float = 0.0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get insights based on filtering criteria.
        
        Args:
            biological_level: Optional biological level to filter by
            min_confidence: Minimum confidence threshold
            min_relevance: Minimum relevance threshold
            min_novelty: Minimum novelty threshold
            limit: Maximum number of insights to return
            
        Returns:
            List of insights matching the criteria
        """
        filtered_insights = self.insights
        
        # Apply filters
        if biological_level:
            filtered_insights = [
                i for i in filtered_insights 
                if i.get("biological_level") == biological_level
            ]
            
        filtered_insights = [
            i for i in filtered_insights 
            if i.get("confidence", 0.0) >= min_confidence and
               i.get("relevance_to_goal", 0.0) >= min_relevance and
               i.get("novelty", 0.0) >= min_novelty
        ]
        
        # Sort by a combined score of confidence, relevance, and novelty
        sorted_insights = sorted(
            filtered_insights,
            key=lambda i: (
                i.get("confidence", 0.0) * 0.4 + 
                i.get("relevance_to_goal", 0.0) * 0.4 + 
                i.get("novelty", 0.0) * 0.2
            ),
            reverse=True
        )
        
        # Limit the number of results
        return sorted_insights[:limit]
