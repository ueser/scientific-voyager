"""
Interfaces for the abstract extraction and normalization pipeline.

This module defines the interfaces for extracting structured information from
scientific article abstracts and normalizing the extracted data.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class IExtractor(ABC):
    """
    Interface for extractors that process scientific article abstracts.
    """
    
    @abstractmethod
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract entities from the given text.
        
        Args:
            text: The text to extract entities from, typically a scientific abstract
            
        Returns:
            A dictionary mapping entity types to lists of extracted entities.
            Each entity is represented as a dictionary with at least 'text' and 'type' keys.
        """
        pass
    
    @abstractmethod
    def extract_relations(self, text: str, entities: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> List[Dict[str, Any]]:
        """
        Extract relations between entities from the given text.
        
        Args:
            text: The text to extract relations from
            entities: Optional pre-extracted entities. If not provided, entities will be extracted first.
            
        Returns:
            A list of extracted relations. Each relation is represented as a dictionary
            with at least 'source', 'target', and 'relation_type' keys.
        """
        pass
    
    @abstractmethod
    def extract_statements(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract scientific statements from the given text.
        
        Args:
            text: The text to extract statements from
            
        Returns:
            A list of extracted statements. Each statement is represented as a dictionary
            with at least 'text', 'confidence', and 'type' keys.
        """
        pass


class INormalizer(ABC):
    """
    Interface for normalizers that standardize extracted information.
    """
    
    @abstractmethod
    def normalize_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize an entity by linking it to standard ontologies or vocabularies.
        
        Args:
            entity: The entity to normalize
            
        Returns:
            The normalized entity with additional standardization information
        """
        pass
    
    @abstractmethod
    def normalize_relation(self, relation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a relation by standardizing its type and properties.
        
        Args:
            relation: The relation to normalize
            
        Returns:
            The normalized relation with standardized properties
        """
        pass


class IExtractionPipeline(ABC):
    """
    Interface for the complete extraction and normalization pipeline.
    """
    
    @abstractmethod
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process the given text through the complete extraction and normalization pipeline.
        
        Args:
            text: The text to process, typically a scientific abstract
            
        Returns:
            A dictionary containing all extracted and normalized information
        """
        pass
    
    @abstractmethod
    def batch_process(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple texts through the complete extraction and normalization pipeline.
        
        Args:
            texts: A list of texts to process
            
        Returns:
            A list of dictionaries containing all extracted and normalized information for each text
        """
        pass
