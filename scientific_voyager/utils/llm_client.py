"""
LLM Client Module

This module provides a client for interacting with OpenAI's GPT-4o model
for NLP tasks, reasoning, classification, and decision making.
"""

import os
from typing import Dict, List, Optional, Union, Any

from openai import OpenAI


class LLMClient:
    """
    Client for interacting with OpenAI's GPT models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize the LLM client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: Model to use (defaults to gpt-4o)
            temperature: Temperature for sampling (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided either as an argument or "
                "through the OPENAI_API_KEY environment variable."
            )
            
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=self.api_key)
        
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
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens
        )
        
        return response.choices[0].message.content
        
    def extract_statements(self, text: str) -> List[Dict]:
        """
        Extract statements from scientific text.
        
        Args:
            text: Scientific text to extract statements from
            
        Returns:
            List of extracted statements with metadata
        """
        system_message = """
        You are an expert scientific statement extractor. Your task is to identify and extract 
        distinct scientific statements from the provided text. For each statement:
        
        1. Extract the statement text
        2. Classify the statement type (causal, descriptive, intervention, definitional)
        3. Identify the biological level (genetic, molecular, cellular, systems, organism)
        4. Assign a confidence score (0.0 to 1.0)
        5. Extract relevant entities and terms
        
        Format your response as a JSON array of statement objects.
        """
        
        prompt = f"""
        Please extract scientific statements from the following text:
        
        {text}
        
        For each statement, provide:
        - statement: The exact statement text
        - type: The statement type (causal, descriptive, intervention, definitional)
        - biological_level: The biological level (genetic, molecular, cellular, systems, organism)
        - confidence: Your confidence in the extraction and classification (0.0 to 1.0)
        - entities: List of key scientific entities mentioned
        """
        
        response = self.complete(prompt, system_message)
        
        # In a real implementation, we would parse the JSON response
        # For now, we'll return a placeholder
        # This would be enhanced in future tasks
        return []
        
    def categorize_statement(self, statement: str) -> Dict:
        """
        Categorize a scientific statement by type and biological level.
        
        Args:
            statement: The statement to categorize
            
        Returns:
            Dictionary with categorization information
        """
        system_message = """
        You are an expert scientific statement classifier. Your task is to classify 
        the provided scientific statement by:
        
        1. Statement type (causal, descriptive, intervention, definitional)
        2. Biological level (genetic, molecular, cellular, systems, organism)
        3. Confidence score (0.0 to 1.0)
        
        Format your response as a JSON object.
        """
        
        prompt = f"""
        Please classify the following scientific statement:
        
        "{statement}"
        
        Provide:
        - type: The statement type (causal, descriptive, intervention, definitional)
        - biological_level: The biological level (genetic, molecular, cellular, systems, organism)
        - confidence: Your confidence in the classification (0.0 to 1.0)
        """
        
        response = self.complete(prompt, system_message)
        
        # In a real implementation, we would parse the JSON response
        # For now, we'll return a placeholder
        # This would be enhanced in future tasks
        return {
            "statement": statement,
            "type": None,
            "biological_level": None,
            "confidence": 0.0,
        }
        
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
        """
        statements_text = "\n".join([
            f"- {s['statement']} (Type: {s['type']}, Level: {s['biological_level']})"
            for s in statements
        ])
        
        system_message = """
        You are an expert scientific insight generator. Your task is to analyze a collection
        of scientific statements and generate non-trivial insights that contribute to the
        specified overarching goal. Each insight should:
        
        1. Synthesize information from multiple statements
        2. Identify patterns, relationships, or contradictions
        3. Suggest novel hypotheses or research directions
        4. Be traceable to the source statements
        
        Format your response as a JSON array of insight objects.
        """
        
        prompt = f"""
        Please generate scientific insights based on the following statements:
        
        {statements_text}
        
        Overarching goal: {overarching_goal}
        {f"Focus area: {focus_area}" if focus_area else ""}
        
        For each insight, provide:
        - text: The insight text
        - source_statements: List of indices of the statements that led to this insight
        - confidence: Your confidence in the insight (0.0 to 1.0)
        - novelty: Assessment of how novel the insight is (0.0 to 1.0)
        - relevance: Relevance to the overarching goal (0.0 to 1.0)
        """
        
        response = self.complete(prompt, system_message)
        
        # In a real implementation, we would parse the JSON response
        # For now, we'll return a placeholder
        # This would be enhanced in future tasks
        return []
        
    def generate_tasks(
        self,
        current_knowledge: Dict,
        overarching_goal: str,
        focus_areas: Optional[List[str]] = None,
        max_tasks: int = 5
    ) -> List[Dict]:
        """
        Generate next tasks based on current knowledge and goals.
        
        Args:
            current_knowledge: Summary of current knowledge state
            overarching_goal: The main scientific goal guiding exploration
            focus_areas: Optional list of focus areas to prioritize
            max_tasks: Maximum number of tasks to generate
            
        Returns:
            List of generated tasks with metadata
        """
        knowledge_summary = "\n".join([
            f"- {k}: {v}" for k, v in current_knowledge.items()
        ])
        
        focus_areas_text = ""
        if focus_areas:
            focus_areas_text = "Focus areas:\n" + "\n".join([f"- {area}" for area in focus_areas])
        
        system_message = """
        You are an expert scientific task planner. Your task is to analyze the current
        knowledge state and generate the next most valuable tasks to pursue in order to
        advance the overarching scientific goal. Each task should:
        
        1. Be specific and actionable
        2. Address gaps in the current knowledge
        3. Build upon existing insights
        4. Contribute meaningfully to the overarching goal
        
        Format your response as a JSON array of task objects.
        """
        
        prompt = f"""
        Please generate the next scientific tasks based on:
        
        Current knowledge summary:
        {knowledge_summary}
        
        Overarching goal: {overarching_goal}
        
        {focus_areas_text}
        
        Generate up to {max_tasks} tasks. For each task, provide:
        - description: Clear description of the task
        - reasoning: Why this task is important
        - focus_keywords: List of key focus keywords
        - priority: Priority level (1-5, with 5 being highest)
        """
        
        response = self.complete(prompt, system_message)
        
        # In a real implementation, we would parse the JSON response
        # For now, we'll return a placeholder
        # This would be enhanced in future tasks
        return []
        
    def extract_terms(self, text: str) -> List[str]:
        """
        Extract biomedical terms from text.
        
        Args:
            text: Text to extract terms from
            
        Returns:
            List of extracted biomedical terms
        """
        system_message = """
        You are an expert biomedical term extractor. Your task is to identify and extract
        all biomedical terms from the provided text. Focus on:
        
        1. Genes and proteins
        2. Diseases and conditions
        3. Drugs and compounds
        4. Biological processes
        5. Anatomical structures
        6. Cell types and components
        
        Format your response as a JSON array of term objects.
        """
        
        prompt = f"""
        Please extract all biomedical terms from the following text:
        
        {text}
        
        For each term, provide:
        - term: The exact term text
        - category: The term category (gene, protein, disease, drug, process, anatomy, cell)
        - normalized_form: Standard form of the term if applicable
        """
        
        response = self.complete(prompt, system_message)
        
        # In a real implementation, we would parse the JSON response
        # For now, we'll return a placeholder
        # This would be enhanced in future tasks
        return []
