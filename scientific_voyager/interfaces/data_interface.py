"""
Data Interface Module

This module defines the abstract interfaces for data management components
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class IDataManager(ABC):
    """
    Interface for data management operations.
    Defines the contract for storing and retrieving various data entities.
    """

    @abstractmethod
    def generate_uid(self) -> str:
        """
        Generate a unique identifier.
        
        Returns:
            A unique identifier string
            
        Raises:
            Exception: If UID generation fails
        """
        pass
        
    @abstractmethod
    def store_statement(self, statement: Dict) -> str:
        """
        Store a statement and assign a UID if not present.
        
        Args:
            statement: Statement data to store
            
        Returns:
            UID of the stored statement
            
        Raises:
            ValueError: If statement data is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def store_insight(self, insight: Dict) -> str:
        """
        Store an insight and assign a UID if not present.
        
        Args:
            insight: Insight data to store
            
        Returns:
            UID of the stored insight
            
        Raises:
            ValueError: If insight data is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def store_task(self, task: Dict) -> str:
        """
        Store a task and assign a UID if not present.
        
        Args:
            task: Task data to store
            
        Returns:
            UID of the stored task
            
        Raises:
            ValueError: If task data is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_statement(self, uid: str) -> Optional[Dict]:
        """
        Retrieve a statement by its UID.
        
        Args:
            uid: UID of the statement to retrieve
            
        Returns:
            Statement data or None if not found
            
        Raises:
            ValueError: If UID is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_insight(self, uid: str) -> Optional[Dict]:
        """
        Retrieve an insight by its UID.
        
        Args:
            uid: UID of the insight to retrieve
            
        Returns:
            Insight data or None if not found
            
        Raises:
            ValueError: If UID is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_task(self, uid: str) -> Optional[Dict]:
        """
        Retrieve a task by its UID.
        
        Args:
            uid: UID of the task to retrieve
            
        Returns:
            Task data or None if not found
            
        Raises:
            ValueError: If UID is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def search_statements(self, query: Dict) -> List[Dict]:
        """
        Search for statements based on query parameters.
        
        Args:
            query: Query parameters for searching
            
        Returns:
            List of matching statements
            
        Raises:
            ValueError: If query is invalid
            Exception: For other unexpected errors
        """
        pass


class IDataSource(ABC):
    """
    Interface for data sources.
    Defines the contract for retrieving data from external sources.
    """
    
    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for scientific literature based on a query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with metadata
            
        Raises:
            ValueError: If query is invalid or empty
            ConnectionError: If there's an issue connecting to the data source
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def fetch_article(self, article_id: str) -> Dict:
        """
        Fetch a specific article by its ID.
        
        Args:
            article_id: ID of the article to fetch
            
        Returns:
            Article data including full text if available
            
        Raises:
            ValueError: If article_id is invalid
            ConnectionError: If there's an issue connecting to the data source
            Exception: For other unexpected errors
        """
        pass


class IDatabaseManager(ABC):
    """
    Interface for database management operations.
    Defines the contract for interacting with various database backends.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            ConnectionError: If there's an issue connecting to the database
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the database.
        
        Returns:
            True if disconnection successful, False otherwise
            
        Raises:
            Exception: For unexpected errors
        """
        pass
        
    @abstractmethod
    def store_graph(self, graph: Any) -> bool:
        """
        Store a knowledge graph in the database.
        
        Args:
            graph: The graph to store
            
        Returns:
            True if storage successful, False otherwise
            
        Raises:
            ValueError: If graph is invalid
            ConnectionError: If there's an issue with the database connection
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def query(self, query_string: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a query against the database.
        
        Args:
            query_string: The query string to execute
            params: Optional parameters for the query
            
        Returns:
            List of query results
            
        Raises:
            ValueError: If query is invalid
            ConnectionError: If there's an issue with the database connection
            Exception: For other unexpected errors
        """
        pass
