"""
PubMed Data Source Module

This module handles fetching and processing data from PubMed for the Scientific Voyager platform.
Uses OpenAI's GPT-4o model for term extraction and data processing.
"""

from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup

from scientific_voyager.utils.llm_client import LLMClient


class PubMedSource:
    """
    Handles fetching and processing data from PubMed.
    Uses OpenAI's GPT-4o model for term extraction and data processing.
    """

    def __init__(self, api_key: Optional[str] = None, openai_api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the PubMed data source.
        
        Args:
            api_key: Optional API key for NCBI E-utilities
            openai_api_key: Optional API key for OpenAI (defaults to OPENAI_API_KEY environment variable)
            model: Model to use for NLP tasks (defaults to gpt-4o)
        """
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.llm_client = LLMClient(api_key=openai_api_key, model=model)
        
    def search(
        self, 
        query: str, 
        max_results: int = 10, 
        sort: str = "relevance"
    ) -> List[str]:
        """
        Search PubMed for articles matching the query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort: Sort order ("relevance", "date")
            
        Returns:
            List of PubMed IDs (PMIDs) matching the query
        """
        # Placeholder for future implementation
        # Will use NCBI E-utilities API
        return []
        
    def fetch_abstract(self, pmid: str) -> Optional[Dict]:
        """
        Fetch the abstract for a given PubMed ID.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary containing article metadata and abstract text
        """
        # Placeholder for future implementation
        # Will use NCBI E-utilities API
        return None
        
    def fetch_multiple_abstracts(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch abstracts for multiple PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of dictionaries containing article metadata and abstract text
        """
        results = []
        for pmid in pmids:
            abstract = self.fetch_abstract(pmid)
            if abstract:
                results.append(abstract)
        return results
        
    def extract_terms(self, abstract: Dict) -> List[str]:
        """
        Extract biomedical terms from an abstract using GPT-4o.
        
        Args:
            abstract: Abstract dictionary
            
        Returns:
            List of extracted biomedical terms
        """
        if not abstract or "text" not in abstract:
            return []
            
        # Use the LLM client to extract terms
        return self.llm_client.extract_terms(abstract["text"])
