"""
PubMed API Adapter Module

This module implements the adapter for the PubMed API to fetch scientific literature data.
It handles API authentication, searching, and fetching article metadata.
"""

import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from xml.etree import ElementTree

from scientific_voyager.interfaces.literature_interface import ILiteratureAdapter
from scientific_voyager.config.config_manager import get_config


class PubMedAdapter(ILiteratureAdapter):
    """
    Adapter for the PubMed API that implements the ILiteratureAdapter interface.
    Handles fetching scientific literature data from PubMed.
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
        self.min_request_interval = 1.0 / self.requests_per_second
        
        # Track last request time for rate limiting
        self.last_request_time = 0
        
        self.logger.info(f"Initialized PubMed adapter with rate limit: {self.requests_per_second} req/s")
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting by waiting if necessary."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.4f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> requests.Response:
        """
        Make a request to the PubMed API with rate limiting.
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            Response object
            
        Raises:
            ConnectionError: If unable to connect to the PubMed API
            Exception: For other unexpected errors
        """
        # Add API key to parameters if available
        if self.api_key:
            params["api_key"] = self.api_key
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        try:
            self.logger.debug(f"Making request to {url} with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to PubMed API: {e}")
            if isinstance(e, requests.exceptions.ConnectionError):
                raise ConnectionError(f"Unable to connect to PubMed API: {e}")
            else:
                raise Exception(f"Error fetching data from PubMed API: {e}")
    
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
                    # Convert month name to number if needed
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
                    
                    last_name_text = last_name.text if last_name is not None else ""
                    fore_name_text = fore_name.text if fore_name is not None else ""
                    
                    if last_name_text or fore_name_text:
                        author_name = f"{last_name_text}, {fore_name_text}".strip(", ")
                        authors.append(author_name)
            
            # Extract abstract
            abstract_text = ""
            abstract_element = article_xml.find(".//Abstract")
            if abstract_element is not None:
                for abstract_part in abstract_element.findall(".//AbstractText"):
                    # Check if there's a label
                    label = abstract_part.get("Label")
                    if label:
                        part_text = f"{label}: {abstract_part.text}" if abstract_part.text else f"{label}:"
                    else:
                        part_text = abstract_part.text or ""
                    
                    if part_text:
                        if abstract_text:
                            abstract_text += "\n\n" + part_text
                        else:
                            abstract_text = part_text
            
            # Extract DOI
            doi = None
            article_id_list = article_xml.find(".//ArticleIdList")
            if article_id_list is not None:
                for article_id in article_id_list.findall(".//ArticleId"):
                    if article_id.get("IdType") == "doi":
                        doi = article_id.text
                        break
            
            # Extract keywords
            keywords = []
            keyword_list = article_xml.find(".//KeywordList")
            if keyword_list is not None:
                for keyword in keyword_list.findall(".//Keyword"):
                    if keyword.text:
                        keywords.append(keyword.text)
            
            # Create normalized article metadata
            article_data = {
                "article_id": pmid_text,
                "source": "pubmed",
                "title": title,
                "abstract": abstract_text,
                "authors": authors,
                "journal": journal_title,
                "publication_date": pub_date,
                "doi": doi,
                "keywords": keywords,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/" if pmid_text else None
            }
            
            return article_data
        
        except Exception as e:
            self.logger.error(f"Error parsing article XML: {e}")
            # Return minimal article data with error information
            return {
                "article_id": article_xml.find(".//PMID").text if article_xml.find(".//PMID") is not None else "unknown",
                "source": "pubmed",
                "title": "Error parsing article",
                "abstract": f"Error parsing article: {str(e)}",
                "authors": [],
                "journal": None,
                "publication_date": None,
                "doi": None,
                "keywords": [],
                "url": None,
                "parse_error": str(e)
            }
    
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
            ConnectionError: If unable to connect to PubMed
            ValueError: If query is invalid
            Exception: For other unexpected errors
        """
        if not query:
            raise ValueError("Search query cannot be empty")
        
        self.logger.info(f"Searching PubMed for: {query} (max_results={max_results})")
        
        # Build search query with date range if provided
        search_query = query
        if date_from and date_to:
            date_range = f"{self._format_date(date_from)}:{self._format_date(date_to)}[Date - Publication]"
            search_query = f"{search_query} AND {date_range}"
        elif date_from:
            date_range = f"{self._format_date(date_from)}[Date - Publication]"
            search_query = f"{search_query} AND {date_range}"
        elif date_to:
            date_range = f"{self._format_date(date_to)}[Date - Publication]"
            search_query = f"{search_query} AND {date_range}"
        
        # Set up search parameters
        search_params = {
            "db": self.DATABASE,
            "term": search_query,
            "retmax": max_results,
            "retmode": "json",
            "usehistory": "y"
        }
        
        # Add sort parameter if provided
        if "sort" in kwargs:
            search_params["sort"] = kwargs["sort"]
        
        # Step 1: Search for article IDs
        try:
            search_response = self._make_request(self.ESEARCH_URL, search_params)
            search_data = search_response.json()
            
            if "esearchresult" not in search_data or "idlist" not in search_data["esearchresult"]:
                self.logger.warning(f"Unexpected search response format: {search_data}")
                return []
            
            article_ids = search_data["esearchresult"]["idlist"]
            
            if not article_ids:
                self.logger.info(f"No articles found for query: {query}")
                return []
            
            self.logger.info(f"Found {len(article_ids)} articles for query: {query}")
            
            # Step 2: Fetch article details
            return self.get_articles_by_ids(article_ids)
            
        except Exception as e:
            self.logger.error(f"Error searching PubMed: {e}")
            raise
    
    def get_article_by_id(self, article_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific article by its ID.
        
        Args:
            article_id: PubMed ID for the article
            
        Returns:
            Dictionary containing article metadata
            
        Raises:
            ConnectionError: If unable to connect to PubMed
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        if not article_id:
            raise ValueError("Article ID cannot be empty")
        
        self.logger.info(f"Fetching article details for PubMed ID: {article_id}")
        
        # Set up fetch parameters
        fetch_params = {
            "db": self.DATABASE,
            "id": article_id,
            "retmode": "xml"
        }
        
        try:
            # Fetch article details
            fetch_response = self._make_request(self.EFETCH_URL, fetch_params)
            
            # Parse XML response
            root = ElementTree.fromstring(fetch_response.text)
            
            # Find the article element
            article_element = root.find(".//PubmedArticle")
            
            if article_element is None:
                raise KeyError(f"Article not found for ID: {article_id}")
            
            # Parse article XML
            article_data = self._parse_article_xml(article_element)
            
            return article_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching article from PubMed: {e}")
            raise
        except ElementTree.ParseError as e:
            self.logger.error(f"Error parsing XML response: {e}")
            raise Exception(f"Error parsing PubMed response: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching article: {e}")
            raise
    
    def get_articles_by_ids(self, article_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed metadata for multiple articles by their IDs.
        
        Args:
            article_ids: List of PubMed IDs
            
        Returns:
            List of dictionaries containing article metadata
            
        Raises:
            ConnectionError: If unable to connect to PubMed
            ValueError: If any article_id is invalid
            Exception: For other unexpected errors
        """
        if not article_ids:
            return []
        
        self.logger.info(f"Fetching details for {len(article_ids)} articles")
        
        # Set up fetch parameters
        fetch_params = {
            "db": self.DATABASE,
            "id": ",".join(article_ids),
            "retmode": "xml"
        }
        
        try:
            # Fetch article details
            fetch_response = self._make_request(self.EFETCH_URL, fetch_params)
            
            # Parse XML response
            root = ElementTree.fromstring(fetch_response.text)
            
            # Find all article elements
            article_elements = root.findall(".//PubmedArticle")
            
            if not article_elements:
                self.logger.warning(f"No articles found for IDs: {article_ids}")
                return []
            
            # Parse each article XML
            articles_data = []
            for article_element in article_elements:
                article_data = self._parse_article_xml(article_element)
                articles_data.append(article_data)
            
            self.logger.info(f"Successfully fetched {len(articles_data)} articles")
            return articles_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching articles from PubMed: {e}")
            raise
        except ElementTree.ParseError as e:
            self.logger.error(f"Error parsing XML response: {e}")
            raise Exception(f"Error parsing PubMed response: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching articles: {e}")
            raise
    
    def get_article_abstract(self, article_id: str) -> str:
        """
        Get the abstract text for a specific article.
        
        Args:
            article_id: PubMed ID for the article
            
        Returns:
            Abstract text as a string
            
        Raises:
            ConnectionError: If unable to connect to PubMed
            ValueError: If article_id is invalid
            KeyError: If article is not found or has no abstract
            Exception: For other unexpected errors
        """
        article_data = self.get_article_by_id(article_id)
        
        if not article_data.get("abstract"):
            raise KeyError(f"No abstract found for article ID: {article_id}")
        
        return article_data["abstract"]
    
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
            ConnectionError: If unable to connect to PubMed
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        self.logger.info(f"Attempting to find full text for PubMed ID: {article_id}")
        
        # PubMed API doesn't directly provide full text
        # This would typically involve additional services or web scraping
        # For now, we'll just return None and log a message
        self.logger.info(f"Full text retrieval not directly supported by PubMed API for ID: {article_id}")
        return None
    
    def get_related_articles(self, article_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get articles related to the specified article using PubMed's elink API.
        
        Args:
            article_id: PubMed ID for the reference article
            max_results: Maximum number of related articles to return
            
        Returns:
            List of related article metadata dictionaries
            
        Raises:
            ConnectionError: If unable to connect to PubMed
            ValueError: If article_id is invalid
            KeyError: If article is not found
            Exception: For other unexpected errors
        """
        if not article_id:
            raise ValueError("Article ID cannot be empty")
        
        self.logger.info(f"Finding articles related to PubMed ID: {article_id}")
        
        # Set up elink parameters
        elink_params = {
            "db": self.DATABASE,
            "id": article_id,
            "dbfrom": self.DATABASE,
            "linkname": "pubmed_pubmed",
            "retmode": "json"
        }
        
        try:
            # Get related article IDs
            elink_response = self._make_request(self.ELINK_URL, elink_params)
            elink_data = elink_response.json()
            
            # Extract related article IDs
            related_ids = []
            
            if "linksets" in elink_data and elink_data["linksets"]:
                linkset = elink_data["linksets"][0]
                if "linksetdbs" in linkset:
                    for linksetdb in linkset["linksetdbs"]:
                        if linksetdb.get("linkname") == "pubmed_pubmed":
                            related_ids = linksetdb.get("links", [])
                            break
            
            if not related_ids:
                self.logger.info(f"No related articles found for ID: {article_id}")
                return []
            
            # Limit the number of related articles
            related_ids = related_ids[:max_results]
            
            self.logger.info(f"Found {len(related_ids)} related articles for ID: {article_id}")
            
            # Fetch details for related articles
            return self.get_articles_by_ids(related_ids)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error finding related articles: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error finding related articles: {e}")
            raise
