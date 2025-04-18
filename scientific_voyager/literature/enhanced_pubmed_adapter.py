"""
Enhanced PubMed API Adapter Module

This module implements an enhanced adapter for the PubMed API with caching and error handling.
It handles API authentication, searching, and fetching article metadata with robust
error handling, retry mechanisms, and caching.
"""

import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from xml.etree import ElementTree
import json

from scientific_voyager.interfaces.literature_interface import ILiteratureAdapter
from scientific_voyager.config.config_manager import get_config
from scientific_voyager.utils.cache import cached, get_cache_manager
from scientific_voyager.utils.error_handling import (
    retry, rate_limit, RetryStrategy, NetworkError, APIError, RateLimitError
)


# Cache TTL constants (in seconds)
SEARCH_CACHE_TTL = 3600  # 1 hour
ARTICLE_CACHE_TTL = 86400  # 1 day
ABSTRACT_CACHE_TTL = 86400  # 1 day
RELATED_CACHE_TTL = 43200  # 12 hours


class PubMedAdapter(ILiteratureAdapter):
    """
    Enhanced adapter for the PubMed API that implements the ILiteratureAdapter interface.
    Includes caching, rate limiting, and robust error handling.
    """
    
    # PubMed API endpoints
    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    ELINK_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
    ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    # PubMed database name
    DATABASE = "pubmed"
    
    # Rate limiting parameters (default: 3 requests per second)
    DEFAULT_REQUESTS_PER_SECOND = 3
    
    def __init__(self):
        """Initialize the PubMed adapter."""
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        
        # Get API key from configuration
        self.api_key = self.config.get_config_dto().api_keys.get("pubmed")
        
        # Get rate limiting configuration
        self.requests_per_second = self.config.get("pubmed.requests_per_second", 
                                                 self.DEFAULT_REQUESTS_PER_SECOND)
        
        # Initialize cache
        self.cache_manager = get_cache_manager()
        
        self.logger.info(f"Initialized enhanced PubMed adapter with rate limit: {self.requests_per_second} req/s")
    
    @rate_limit(calls=3, period=1.0, raise_on_limit=False)
    @retry(max_attempts=3, strategy=RetryStrategy.EXPONENTIAL_JITTER, base_delay=1.0, max_delay=30.0)
    def _make_request(self, url: str, params: Dict[str, Any]) -> requests.Response:
        """
        Make a request to the PubMed API with rate limiting and retry logic.
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If unable to connect to the PubMed API
            APIError: If the API returns an error response
            Exception: For other unexpected errors
        """
        # Add API key to parameters if available
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            self.logger.debug(f"Making request to {url} with params: {params}")
            response = requests.get(url, params=params, timeout=30)
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"PubMed API returned status code {response.status_code}"
                self.logger.error(error_msg)
                raise APIError(error_msg, status_code=response.status_code, response=response.text)
            
            return response
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout connecting to PubMed API: {e}")
            raise NetworkError(f"Timeout connecting to PubMed API: {e}")
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error to PubMed API: {e}")
            raise NetworkError(f"Unable to connect to PubMed API: {e}")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error to PubMed API: {e}")
            raise NetworkError(f"Error fetching data from PubMed API: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in PubMed API request: {e}")
            raise
    
    def _format_date(self, date: datetime) -> str:
        """
        Format a datetime object for PubMed API queries.
        
        Args:
            date: Datetime object
            
        Returns:
            Formatted date string (YYYY/MM/DD)
        """
        return date.strftime("%Y/%m/%d")
    
    def _parse_article_xml(self, article_xml: ElementTree.Element) -> Dict[str, Any]:
        """
        Parse article XML from PubMed API response.
        
        Args:
            article_xml: XML element for an article
            
        Returns:
            Dictionary containing normalized article metadata
        """
        try:
            # Extract PubMed ID
            pmid = article_xml.find(".//PMID")
            pmid_text = pmid.text if pmid is not None else None
            
            # Extract article title
            title_element = article_xml.find(".//ArticleTitle")
            title = title_element.text if title_element is not None else "No title available"
            
            # Extract journal information
            journal_element = article_xml.find(".//Journal")
            journal_title = None
            if journal_element is not None:
                journal_title_element = journal_element.find(".//Title")
                journal_title = journal_title_element.text if journal_title_element is not None else None
            
            # Extract publication date
            pub_date = None
            pub_date_element = article_xml.find(".//PubDate")
            if pub_date_element is not None:
                year_element = pub_date_element.find("Year")
                month_element = pub_date_element.find("Month")
                day_element = pub_date_element.find("Day")
                
                year = year_element.text if year_element is not None else None
                month = month_element.text if month_element is not None else "01"
                day = day_element.text if day_element is not None else "01"
                
                if year:
                    # Handle month names
                    month_map = {
                        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                    }
                    
                    if month in month_map:
                        month = month_map[month]
                    
                    # Ensure month and day are two digits
                    if len(month) == 1:
                        month = f"0{month}"
                    if len(day) == 1:
                        day = f"0{day}"
                    
                    pub_date = f"{year}-{month}-{day}"
            
            # Extract authors
            authors = []
            author_list = article_xml.find(".//AuthorList")
            if author_list is not None:
                for author_element in author_list.findall(".//Author"):
                    last_name = author_element.find("LastName")
                    fore_name = author_element.find("ForeName")
                    
                    if last_name is not None:
                        author_name = last_name.text
                        if fore_name is not None:
                            author_name = f"{fore_name.text} {author_name}"
                        authors.append(author_name)
            
            # Extract abstract
            abstract_text = ""
            abstract_element = article_xml.find(".//Abstract")
            if abstract_element is not None:
                abstract_parts = []
                for abstract_part in abstract_element.findall(".//AbstractText"):
                    label = abstract_part.get("Label")
                    text = abstract_part.text or ""
                    
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                
                abstract_text = " ".join(abstract_parts)
            
            # Extract keywords
            keywords = []
            keyword_list = article_xml.find(".//KeywordList")
            if keyword_list is not None:
                for keyword_element in keyword_list.findall(".//Keyword"):
                    if keyword_element.text:
                        keywords.append(keyword_element.text)
            
            # Extract DOI
            doi = None
            article_id_list = article_xml.find(".//ArticleIdList")
            if article_id_list is not None:
                for article_id_element in article_id_list.findall(".//ArticleId"):
                    if article_id_element.get("IdType") == "doi":
                        doi = article_id_element.text
            
            # Build article metadata
            article_metadata = {
                "pmid": pmid_text,
                "title": title,
                "journal": journal_title,
                "pub_date": pub_date,
                "authors": authors,
                "abstract": abstract_text,
                "keywords": keywords,
                "doi": doi
            }
            
            return article_metadata
            
        except Exception as e:
            self.logger.error(f"Error parsing article XML: {e}")
            raise ValueError(f"Error parsing article XML: {e}")
    
    @cached(ttl=SEARCH_CACHE_TTL, use_disk=True, key_prefix="search")
    def search_articles(self, 
                        query: str, 
                        max_results: int = 50, 
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None,
                        **kwargs) -> List[Dict[str, Any]]:
        """
        Search for articles matching the given query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            date_from: Start date for filtering articles
            date_to: End date for filtering articles
            **kwargs: Additional source-specific parameters
                - sort: Sort order (e.g., "relevance", "pub_date")
                - fields: Specific fields to search in
                
        Returns:
            List of article metadata dictionaries
            
        Raises:
            NetworkError: If unable to connect to PubMed
            APIError: If the API returns an error response
            ValueError: If query is invalid
            Exception: For other unexpected errors
        """
        if not query:
            raise ValueError("Search query cannot be empty")
        
        # Build date range for query if provided
        date_range = ""
        if date_from or date_to:
            if date_from:
                date_range = f"{self._format_date(date_from)}[PDAT]"
                
            if date_to:
                if date_range:
                    date_range += f" : {self._format_date(date_to)}[PDAT]"
                else:
                    date_range = f"{self._format_date(date_to)}[PDAT]"
            
            # Combine date range with query
            query = f"({query}) AND ({date_range})"
        
        # Handle sort parameter
        sort = kwargs.get("sort", "relevance")
        sort_mapping = {
            "relevance": "relevance",
            "pub_date": "pub+date",
            "first_author": "first+author"
        }
        sort_param = sort_mapping.get(sort, "relevance")
        
        # Build request parameters for esearch
        params = {
            "db": self.DATABASE,
            "term": query,
            "retmax": max_results,
            "sort": sort_param,
            "retmode": "json"
        }
        
        try:
            # First, search for article IDs
            response = self._make_request(self.ESEARCH_URL, params)
            search_data = response.json()
            
            # Extract article IDs
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                self.logger.info(f"No articles found for query: {query}")
                return []
            
            # Fetch detailed information for each article
            return self.get_articles_by_ids(id_list)
            
        except Exception as e:
            self.logger.error(f"Error searching articles with query '{query}': {e}")
            raise
    
    @cached(ttl=ARTICLE_CACHE_TTL, use_disk=True, key_prefix="article")
    def get_article_by_id(self, article_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific article by its ID.
        
        Args:
            article_id: PubMed ID for the article
            
        Returns:
            Dictionary containing article metadata
            
        Raises:
            NetworkError: If unable to connect to PubMed
            APIError: If the API returns an error response
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        if not article_id:
            raise ValueError("Article ID cannot be empty")
        
        # Build request parameters for efetch
        params = {
            "db": self.DATABASE,
            "id": article_id,
            "retmode": "xml"
        }
        
        try:
            response = self._make_request(self.EFETCH_URL, params)
            
            # Parse XML response
            root = ElementTree.fromstring(response.text)
            
            # Find the article element
            article_element = root.find(".//PubmedArticle")
            if article_element is None:
                raise KeyError(f"Article not found for ID: {article_id}")
            
            # Parse article XML
            article_metadata = self._parse_article_xml(article_element)
            
            return article_metadata
            
        except Exception as e:
            self.logger.error(f"Error fetching article with ID {article_id}: {e}")
            raise
    
    def get_articles_by_ids(self, article_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed metadata for multiple articles by their IDs.
        
        Args:
            article_ids: List of PubMed IDs
            
        Returns:
            List of dictionaries containing article metadata
            
        Raises:
            NetworkError: If unable to connect to PubMed
            APIError: If the API returns an error response
            ValueError: If any article_id is invalid
            Exception: For other unexpected errors
        """
        if not article_ids:
            return []
        
        # Validate article IDs
        for article_id in article_ids:
            if not article_id:
                raise ValueError("Article ID cannot be empty")
        
        # Fetch articles in batches to avoid large requests
        batch_size = 50
        all_articles = []
        
        for i in range(0, len(article_ids), batch_size):
            batch_ids = article_ids[i:i+batch_size]
            
            # Build request parameters for efetch
            params = {
                "db": self.DATABASE,
                "id": ",".join(batch_ids),
                "retmode": "xml"
            }
            
            try:
                response = self._make_request(self.EFETCH_URL, params)
                
                # Parse XML response
                root = ElementTree.fromstring(response.text)
                
                # Find all article elements
                article_elements = root.findall(".//PubmedArticle")
                
                # Parse each article XML
                for article_element in article_elements:
                    try:
                        article_metadata = self._parse_article_xml(article_element)
                        all_articles.append(article_metadata)
                    except Exception as e:
                        self.logger.warning(f"Error parsing article: {e}")
                        # Continue with other articles
                
            except Exception as e:
                self.logger.error(f"Error fetching articles batch: {e}")
                raise
        
        return all_articles
    
    @cached(ttl=ABSTRACT_CACHE_TTL, use_disk=True, key_prefix="abstract")
    def get_article_abstract(self, article_id: str) -> Optional[str]:
        """
        Get the abstract text for a specific article.
        
        Args:
            article_id: PubMed ID for the article
            
        Returns:
            Abstract text as a string
            
        Raises:
            NetworkError: If unable to connect to PubMed
            APIError: If the API returns an error response
            ValueError: If article_id is invalid
            KeyError: If article is not found or has no abstract
            Exception: For other unexpected errors
        """
        try:
            article = self.get_article_by_id(article_id)
            abstract = article.get("abstract")
            
            if not abstract:
                self.logger.warning(f"No abstract found for article ID: {article_id}")
                return None
            
            return abstract
            
        except Exception as e:
            self.logger.error(f"Error fetching abstract for article ID {article_id}: {e}")
            raise
    
    def get_article_full_text(self, article_id: str) -> Optional[str]:
        """
        Get the full text for a specific article if available.
        Note: PubMed API does not directly provide full text. This method
        attempts to find a link to the full text or returns None.
        
        Args:
            article_id: PubMed ID for the article
            
        Returns:
            Full text as a string if available, None otherwise
            
        Raises:
            NetworkError: If unable to connect to PubMed
            APIError: If the API returns an error response
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        try:
            article = self.get_article_by_id(article_id)
            
            # PubMed API doesn't provide full text directly
            # Return None with a warning
            self.logger.warning(f"Full text not available through PubMed API for article ID: {article_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching full text for article ID {article_id}: {e}")
            raise
    
    @cached(ttl=RELATED_CACHE_TTL, use_disk=True, key_prefix="related")
    def get_related_articles(self, article_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get articles related to the specified article using PubMed's elink API.
        
        Args:
            article_id: PubMed ID for the reference article
            max_results: Maximum number of related articles to return
            
        Returns:
            List of related article metadata dictionaries
            
        Raises:
            NetworkError: If unable to connect to PubMed
            APIError: If the API returns an error response
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        if not article_id:
            raise ValueError("Article ID cannot be empty")
        
        # Build request parameters for elink
        params = {
            "dbfrom": self.DATABASE,
            "db": self.DATABASE,
            "id": article_id,
            "linkname": "pubmed_pubmed",
            "retmode": "json"
        }
        
        try:
            response = self._make_request(self.ELINK_URL, params)
            link_data = response.json()
            
            # Extract related article IDs
            link_set = link_data.get("linksets", [{}])[0]
            link_list = link_set.get("linksetdbs", [{}])[0].get("links", [])
            
            if not link_list:
                self.logger.info(f"No related articles found for article ID: {article_id}")
                return []
            
            # Limit the number of related articles
            related_ids = [str(link.get("id")) for link in link_list[:max_results]]
            
            # Fetch detailed information for each related article
            return self.get_articles_by_ids(related_ids)
            
        except Exception as e:
            self.logger.error(f"Error fetching related articles for ID {article_id}: {e}")
            raise
