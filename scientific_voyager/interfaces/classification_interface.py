"""
Classification interfaces for the Scientific Voyager platform.

This module defines interfaces for classifying scientific statements into
biological scales and statement types.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from enum import Enum, auto

from scientific_voyager.interfaces.extraction_dto import StatementDTO


class BiologicalScale(Enum):
    """Biological scales for statement classification."""
    
    GENETIC = "genetic"  # Genetic/genomic level (DNA, genes, etc.)
    MOLECULAR = "molecular"  # Molecular level (proteins, metabolites, etc.)
    CELLULAR = "cellular"  # Cellular level (cell types, organelles, etc.)
    TISSUE = "tissue"  # Tissue level (tissue types, histology, etc.)
    ORGAN = "organ"  # Organ level (heart, liver, brain, etc.)
    SYSTEM = "system"  # System level (nervous system, immune system, etc.)
    ORGANISM = "organism"  # Whole organism level (physiology, behavior, etc.)
    POPULATION = "population"  # Population level (epidemiology, etc.)
    ECOSYSTEM = "ecosystem"  # Ecosystem level (environmental interactions, etc.)
    UNKNOWN = "unknown"  # Unknown or unclassified scale


class StatementType(Enum):
    """Types of scientific statements."""
    
    CAUSAL = "causal"  # Causal relationship (A causes B)
    CORRELATIONAL = "correlational"  # Correlational relationship (A is associated with B)
    DESCRIPTIVE = "descriptive"  # Descriptive statement (A has property B)
    DEFINITIONAL = "definitional"  # Definition (A is defined as B)
    METHODOLOGICAL = "methodological"  # Methodological statement (A is measured using B)
    COMPARATIVE = "comparative"  # Comparative statement (A is greater/less than B)
    INTERVENTION = "intervention"  # Intervention statement (A treatment affects B)
    PREDICTIVE = "predictive"  # Predictive statement (A predicts B)
    HYPOTHESIS = "hypothesis"  # Hypothesis statement (A might cause B)
    REVIEW = "review"  # Review statement (summarizing existing knowledge)
    UNKNOWN = "unknown"  # Unknown or unclassified statement type


class IClassifier(ABC):
    """
    Interface for classifying scientific statements.
    
    This interface defines methods for classifying scientific statements
    into biological scales and statement types.
    """
    
    @abstractmethod
    def classify_scale(self, statement: StatementDTO) -> Tuple[BiologicalScale, float]:
        """
        Classify a statement into a biological scale.
        
        Args:
            statement: The statement to classify
            
        Returns:
            Tuple of (biological scale, confidence score)
        """
        pass
    
    @abstractmethod
    def classify_type(self, statement: StatementDTO) -> Tuple[StatementType, float]:
        """
        Classify a statement into a statement type.
        
        Args:
            statement: The statement to classify
            
        Returns:
            Tuple of (statement type, confidence score)
        """
        pass
    
    @abstractmethod
    def classify_statement(self, 
                          statement: StatementDTO) -> Dict[str, Any]:
        """
        Classify a statement into both scale and type.
        
        Args:
            statement: The statement to classify
            
        Returns:
            Dictionary with classification results
        """
        pass
    
    @abstractmethod
    def batch_classify(self, 
                      statements: List[StatementDTO]) -> List[Dict[str, Any]]:
        """
        Classify multiple statements in batch.
        
        Args:
            statements: List of statements to classify
            
        Returns:
            List of classification results
        """
        pass


class IClassificationValidator(ABC):
    """
    Interface for validating classification results.
    
    This interface defines methods for validating and improving
    the quality of classification results.
    """
    
    @abstractmethod
    def validate_classification(self, 
                               statement: StatementDTO,
                               classification: Dict[str, Any]) -> bool:
        """
        Validate a classification result.
        
        Args:
            statement: The classified statement
            classification: The classification result
            
        Returns:
            True if the classification is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def suggest_improvements(self, 
                            statement: StatementDTO,
                            classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest improvements for a classification result.
        
        Args:
            statement: The classified statement
            classification: The classification result
            
        Returns:
            Dictionary with suggested improvements
        """
        pass


class IFeedbackCollector(ABC):
    """
    Interface for collecting feedback on classification results.
    
    This interface defines methods for collecting and processing
    feedback on classification results to improve future classifications.
    """
    
    @abstractmethod
    def collect_feedback(self, 
                        statement: StatementDTO,
                        classification: Dict[str, Any],
                        feedback: Dict[str, Any]) -> None:
        """
        Collect feedback on a classification result.
        
        Args:
            statement: The classified statement
            classification: The classification result
            feedback: The feedback data
        """
        pass
    
    @abstractmethod
    def process_feedback(self) -> Dict[str, Any]:
        """
        Process collected feedback to improve the classifier.
        
        Returns:
            Dictionary with processing results
        """
        pass


class ITaxonomyManager(ABC):
    """
    Interface for managing classification taxonomies.
    
    This interface defines methods for managing and updating
    the taxonomies used for classification.
    """
    
    @abstractmethod
    def get_scale_taxonomy(self) -> Dict[str, Any]:
        """
        Get the current biological scale taxonomy.
        
        Returns:
            Dictionary representing the scale taxonomy
        """
        pass
    
    @abstractmethod
    def get_type_taxonomy(self) -> Dict[str, Any]:
        """
        Get the current statement type taxonomy.
        
        Returns:
            Dictionary representing the type taxonomy
        """
        pass
    
    @abstractmethod
    def update_scale_taxonomy(self, taxonomy: Dict[str, Any]) -> None:
        """
        Update the biological scale taxonomy.
        
        Args:
            taxonomy: The new taxonomy
        """
        pass
    
    @abstractmethod
    def update_type_taxonomy(self, taxonomy: Dict[str, Any]) -> None:
        """
        Update the statement type taxonomy.
        
        Args:
            taxonomy: The new taxonomy
        """
        pass
