"""
Knowledge Interface Module

This module defines the abstract interfaces for knowledge management components
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
import networkx as nx


class IKnowledgeGraph(ABC):
    """
    Interface for knowledge graph operations.
    Defines the contract for managing the knowledge graph of scientific statements.
    """

    @abstractmethod
    def add_statement(self, statement_id: str, metadata: Dict) -> None:
        """
        Add a statement node to the knowledge graph.
        
        Args:
            statement_id: Unique identifier for the statement
            metadata: Statement metadata including type, biological level, etc.
            
        Raises:
            ValueError: If statement_id or metadata is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def add_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        relationship_type: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a relationship between two statements in the knowledge graph.
        
        Args:
            source_id: Source statement ID
            target_id: Target statement ID
            relationship_type: Type of relationship (supports, contradicts, etc.)
            metadata: Additional metadata about the relationship
            
        Raises:
            ValueError: If source_id, target_id, or relationship_type is invalid
            KeyError: If source_id or target_id does not exist in the graph
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_related_statements(
        self, 
        statement_id: str, 
        relationship_type: Optional[str] = None,
        max_depth: int = 1
    ) -> List[Dict]:
        """
        Get statements related to the given statement.
        
        Args:
            statement_id: ID of the statement to find relations for
            relationship_type: Optional filter for relationship type
            max_depth: Maximum depth to traverse in the graph
            
        Returns:
            List of related statements with their relationship information
            
        Raises:
            ValueError: If statement_id is invalid
            KeyError: If statement_id does not exist in the graph
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def export_to_neo4j(self, connection_uri: str, username: str, password: str) -> bool:
        """
        Export the knowledge graph to Neo4j database.
        
        Args:
            connection_uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            
        Returns:
            True if export was successful, False otherwise
            
        Raises:
            ValueError: If connection parameters are invalid
            ConnectionError: If there's an issue connecting to Neo4j
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_graph(self) -> nx.DiGraph:
        """
        Get the underlying NetworkX graph.
        
        Returns:
            The NetworkX DiGraph representing the knowledge graph
        """
        pass


class IHierarchicalModel(ABC):
    """
    Interface for hierarchical model operations.
    Defines the contract for managing the multi-scale hierarchical model.
    """

    @abstractmethod
    def classify_statement(self, statement: str) -> Dict:
        """
        Classify a scientific statement by biological level and type.
        
        Args:
            statement: The scientific statement to classify
            
        Returns:
            Classification result with biological level, type, and confidence
            
        Raises:
            ValueError: If statement is invalid or empty
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def map_hierarchical_relationships(
        self,
        statements: List[Dict]
    ) -> nx.DiGraph:
        """
        Map hierarchical relationships between statements across biological levels.
        
        Args:
            statements: List of classified scientific statements
            
        Returns:
            NetworkX DiGraph representing the hierarchical relationships
            
        Raises:
            ValueError: If statements list is invalid or empty
            Exception: For other unexpected errors
        """
        pass
