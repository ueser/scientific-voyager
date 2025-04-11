"""
Statement Extractor Module

This module is responsible for extracting statements from scientific literature
and categorizing them into different types and biological levels.
Uses OpenAI's GPT-4o model for NLP tasks.
"""

from typing import Dict, List, Optional, Tuple

from scientific_voyager.utils.llm_client import LLMClient


class StatementExtractor:
    """
    Extracts and categorizes statements from scientific literature.
    Uses OpenAI's GPT-4o model for NLP tasks.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the StatementExtractor.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: Model to use (defaults to gpt-4o)
        """
        self.llm_client = LLMClient(api_key=api_key, model=model)

    def extract_statements(self, text: str) -> List[Dict]:
        """
        Extract statements from the provided text using GPT-4o.

        Args:
            text: Scientific text to extract statements from.

        Returns:
            List of extracted statements with their metadata.
        """
        return self.llm_client.extract_statements(text)

    def categorize_statement(self, statement: str) -> Dict:
        """
        Categorize a statement by type and biological level using GPT-4o.

        Statement types:
        - Causal
        - Descriptive
        - Intervention
        - Definitional

        Biological levels:
        - Genetic
        - Molecular
        - Cellular
        - Systems
        - Organism

        Args:
            statement: The statement to categorize.

        Returns:
            Dictionary with categorization information.
        """
        return self.llm_client.categorize_statement(statement)
