"""
Insights Generator Module

This module implements the Insights Chain functionality for generating and recording
non-trivial insights derived from multiple scientific abstracts.
Uses OpenAI's GPT-4o model for reasoning and insight generation.
"""

from typing import Dict, List, Optional, Set, Tuple

from scientific_voyager.utils.llm_client import LLMClient


class InsightsGenerator:
    """
    Generates and manages scientific insights from the knowledge graph.
    Uses OpenAI's GPT-4o model for reasoning and insight generation.
    """

    def __init__(self, knowledge_graph=None, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the insights generator.
        
        Args:
            knowledge_graph: Reference to the knowledge graph to use for insight generation
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: Model to use (defaults to gpt-4o)
        """
        self.knowledge_graph = knowledge_graph
        self.insights = []
        self.llm_client = LLMClient(api_key=api_key, model=model)
        
    def generate_insights(
        self, 
        statements: List[Dict],
        overarching_goal: str,
        focus_area: Optional[str] = None,
        biological_level: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[Dict]:
        """
        Generate insights based on the provided statements using GPT-4o.
        
        Args:
            statements: List of scientific statements with metadata
            overarching_goal: The main scientific goal guiding exploration
            focus_area: Optional focus area to limit insight generation
            biological_level: Optional biological level to focus on
            min_confidence: Minimum confidence threshold for insights
            
        Returns:
            List of generated insights with metadata
        """
        # Filter statements by biological level if specified
        if biological_level:
            filtered_statements = [s for s in statements if s.get("biological_level") == biological_level]
        else:
            filtered_statements = statements
            
        # Generate insights using the LLM client
        insights = self.llm_client.generate_insights(
            statements=filtered_statements,
            overarching_goal=overarching_goal,
            focus_area=focus_area
        )
        
        # Filter by confidence if specified
        if min_confidence > 0:
            insights = [i for i in insights if i.get("confidence", 0) >= min_confidence]
            
        return insights
        
    def record_insight(
        self, 
        insight_text: str,
        source_statements: List[str],
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Record a new insight with its source statements and metadata.
        
        Args:
            insight_text: The text of the insight
            source_statements: List of statement IDs that led to this insight
            metadata: Additional metadata about the insight
            
        Returns:
            Unique ID of the recorded insight
        """
        if metadata is None:
            metadata = {}
            
        insight_id = f"insight_{len(self.insights) + 1}"
        
        insight = {
            "id": insight_id,
            "text": insight_text,
            "source_statements": source_statements,
            "metadata": metadata,
            "timestamp": None  # Will be implemented in a future task
        }
        
        self.insights.append(insight)
        return insight_id
        
    def get_insights(
        self,
        focus_area: Optional[str] = None,
        biological_level: Optional[str] = None,
        source_statement: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve insights based on filtering criteria.
        
        Args:
            focus_area: Optional focus area to filter by
            biological_level: Optional biological level to filter by
            source_statement: Optional source statement ID to filter by
            
        Returns:
            List of insights matching the criteria
        """
        # Placeholder for future implementation
        return self.insights
