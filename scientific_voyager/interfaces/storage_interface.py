"""
Storage interfaces for the Scientific Voyager platform.

This module defines the interfaces for storing and retrieving statements,
entities, and other data objects in the system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
from uuid import UUID

from scientific_voyager.interfaces.extraction_dto import StatementDTO, EntityDTO, RelationDTO
from scientific_voyager.interfaces.classification_dto import ClassificationResultDTO


class IStorageAdapter(ABC):
    """Interface for storage adapters that persist data objects."""
    
    @abstractmethod
    def save_statement(self, statement: StatementDTO) -> UUID:
        """
        Save a statement to storage.
        
        Args:
            statement: The statement to save
            
        Returns:
            The UUID of the saved statement
        """
        pass
    
    @abstractmethod
    def get_statement(self, statement_id: Union[str, UUID]) -> Optional[StatementDTO]:
        """
        Retrieve a statement by ID.
        
        Args:
            statement_id: The ID of the statement to retrieve
            
        Returns:
            The statement if found, None otherwise
        """
        pass
    
    @abstractmethod
    def save_classification(self, classification: ClassificationResultDTO) -> UUID:
        """
        Save a classification result to storage.
        
        Args:
            classification: The classification result to save
            
        Returns:
            The UUID of the saved classification
        """
        pass
    
    @abstractmethod
    def get_classification(self, classification_id: Union[str, UUID]) -> Optional[ClassificationResultDTO]:
        """
        Retrieve a classification result by ID.
        
        Args:
            classification_id: The ID of the classification to retrieve
            
        Returns:
            The classification result if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_classifications_for_statement(self, statement_id: Union[str, UUID]) -> List[ClassificationResultDTO]:
        """
        Retrieve all classification results for a statement.
        
        Args:
            statement_id: The ID of the statement
            
        Returns:
            List of classification results for the statement
        """
        pass
    
    @abstractmethod
    def save_entity(self, entity: EntityDTO) -> UUID:
        """
        Save an entity to storage.
        
        Args:
            entity: The entity to save
            
        Returns:
            The UUID of the saved entity
        """
        pass
    
    @abstractmethod
    def get_entity(self, entity_id: Union[str, UUID]) -> Optional[EntityDTO]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def save_relation(self, relation: RelationDTO) -> UUID:
        """
        Save a relation to storage.
        
        Args:
            relation: The relation to save
            
        Returns:
            The UUID of the saved relation
        """
        pass
    
    @abstractmethod
    def get_relation(self, relation_id: Union[str, UUID]) -> Optional[RelationDTO]:
        """
        Retrieve a relation by ID.
        
        Args:
            relation_id: The ID of the relation to retrieve
            
        Returns:
            The relation if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search_statements(self, query: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[StatementDTO]:
        """
        Search for statements matching the query.
        
        Args:
            query: The search query (field-value pairs)
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching statements
        """
        pass
    
    @abstractmethod
    def search_classifications(self, query: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[ClassificationResultDTO]:
        """
        Search for classifications matching the query.
        
        Args:
            query: The search query (field-value pairs)
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching classifications
        """
        pass


class IIndexManager(ABC):
    """Interface for managing indexes on stored data."""
    
    @abstractmethod
    def create_index(self, collection: str, field: str) -> bool:
        """
        Create an index on a field in a collection.
        
        Args:
            collection: The collection to create the index on
            field: The field to index
            
        Returns:
            True if the index was created successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def drop_index(self, collection: str, field: str) -> bool:
        """
        Drop an index on a field in a collection.
        
        Args:
            collection: The collection containing the index
            field: The indexed field
            
        Returns:
            True if the index was dropped successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def list_indexes(self, collection: str) -> List[str]:
        """
        List all indexes on a collection.
        
        Args:
            collection: The collection to list indexes for
            
        Returns:
            List of indexed fields
        """
        pass


class IUIDGenerator(ABC):
    """Interface for generating unique identifiers."""
    
    @abstractmethod
    def generate_uid(self, prefix: Optional[str] = None) -> UUID:
        """
        Generate a unique identifier.
        
        Args:
            prefix: Optional prefix for the UID
            
        Returns:
            A unique identifier
        """
        pass
    
    @abstractmethod
    def validate_uid(self, uid: Union[str, UUID]) -> bool:
        """
        Validate a unique identifier.
        
        Args:
            uid: The UID to validate
            
        Returns:
            True if the UID is valid, False otherwise
        """
        pass
