"""
Classification data transfer objects for the Scientific Voyager platform.

This module defines data transfer objects for representing classification
results and related data.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
from datetime import datetime

from scientific_voyager.interfaces.classification_interface import (
    BiologicalScale, StatementType
)


@dataclass
class ClassificationResultDTO:
    """
    Data transfer object for a statement classification result.
    
    Attributes:
        statement_id: ID of the classified statement
        statement_text: Text of the classified statement
        biological_scale: Classified biological scale
        scale_confidence: Confidence score for the scale classification (0-1)
        statement_type: Classified statement type
        type_confidence: Confidence score for the type classification (0-1)
        classification_time: Time when the classification was performed
        metadata: Additional metadata about the classification
    """
    
    statement_id: str
    statement_text: str
    biological_scale: BiologicalScale
    scale_confidence: float
    statement_type: StatementType
    type_confidence: float
    classification_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        return {
            "statement_id": self.statement_id,
            "statement_text": self.statement_text,
            "biological_scale": self.biological_scale.value,
            "scale_confidence": self.scale_confidence,
            "statement_type": self.statement_type.value,
            "type_confidence": self.type_confidence,
            "classification_time": self.classification_time.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassificationResultDTO':
        """
        Create a DTO from a dictionary.
        
        Args:
            data: Dictionary representation of the DTO
            
        Returns:
            ClassificationResultDTO instance
        """
        # Convert string values to enum values
        biological_scale = BiologicalScale(data.get("biological_scale", "unknown"))
        statement_type = StatementType(data.get("statement_type", "unknown"))
        
        # Parse datetime
        classification_time = datetime.fromisoformat(data.get("classification_time", datetime.now().isoformat()))
        
        return cls(
            statement_id=data.get("statement_id", ""),
            statement_text=data.get("statement_text", ""),
            biological_scale=biological_scale,
            scale_confidence=data.get("scale_confidence", 0.0),
            statement_type=statement_type,
            type_confidence=data.get("type_confidence", 0.0),
            classification_time=classification_time,
            metadata=data.get("metadata", {})
        )


@dataclass
class BatchClassificationResultDTO:
    """
    Data transfer object for batch classification results.
    
    Attributes:
        results: List of classification results
        batch_id: Unique identifier for the batch
        batch_time: Time when the batch was processed
        metadata: Additional metadata about the batch
    """
    
    results: List[ClassificationResultDTO]
    batch_id: str
    batch_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        return {
            "results": [result.to_dict() for result in self.results],
            "batch_id": self.batch_id,
            "batch_time": self.batch_time.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchClassificationResultDTO':
        """
        Create a DTO from a dictionary.
        
        Args:
            data: Dictionary representation of the DTO
            
        Returns:
            BatchClassificationResultDTO instance
        """
        # Parse results
        results = [
            ClassificationResultDTO.from_dict(result_data)
            for result_data in data.get("results", [])
        ]
        
        # Parse datetime
        batch_time = datetime.fromisoformat(data.get("batch_time", datetime.now().isoformat()))
        
        return cls(
            results=results,
            batch_id=data.get("batch_id", ""),
            batch_time=batch_time,
            metadata=data.get("metadata", {})
        )


@dataclass
class FeedbackDTO:
    """
    Data transfer object for classification feedback.
    
    Attributes:
        statement_id: ID of the classified statement
        original_classification: Original classification result
        corrected_scale: Corrected biological scale (if any)
        corrected_type: Corrected statement type (if any)
        feedback_text: Textual feedback
        feedback_source: Source of the feedback (e.g., "user", "expert", "system")
        feedback_time: Time when the feedback was provided
        metadata: Additional metadata about the feedback
    """
    
    statement_id: str
    original_classification: ClassificationResultDTO
    corrected_scale: Optional[BiologicalScale] = None
    corrected_type: Optional[StatementType] = None
    feedback_text: str = ""
    feedback_source: str = "user"
    feedback_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        return {
            "statement_id": self.statement_id,
            "original_classification": self.original_classification.to_dict(),
            "corrected_scale": self.corrected_scale.value if self.corrected_scale else None,
            "corrected_type": self.corrected_type.value if self.corrected_type else None,
            "feedback_text": self.feedback_text,
            "feedback_source": self.feedback_source,
            "feedback_time": self.feedback_time.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackDTO':
        """
        Create a DTO from a dictionary.
        
        Args:
            data: Dictionary representation of the DTO
            
        Returns:
            FeedbackDTO instance
        """
        # Parse original classification
        original_classification = ClassificationResultDTO.from_dict(
            data.get("original_classification", {})
        )
        
        # Convert string values to enum values if present
        corrected_scale = None
        if data.get("corrected_scale"):
            corrected_scale = BiologicalScale(data.get("corrected_scale"))
        
        corrected_type = None
        if data.get("corrected_type"):
            corrected_type = StatementType(data.get("corrected_type"))
        
        # Parse datetime
        feedback_time = datetime.fromisoformat(data.get("feedback_time", datetime.now().isoformat()))
        
        return cls(
            statement_id=data.get("statement_id", ""),
            original_classification=original_classification,
            corrected_scale=corrected_scale,
            corrected_type=corrected_type,
            feedback_text=data.get("feedback_text", ""),
            feedback_source=data.get("feedback_source", "user"),
            feedback_time=feedback_time,
            metadata=data.get("metadata", {})
        )


@dataclass
class TaxonomyNodeDTO:
    """
    Data transfer object for a taxonomy node.
    
    Attributes:
        id: Node identifier
        name: Node name
        description: Node description
        parent_id: ID of the parent node (if any)
        children: List of child node IDs
        attributes: Additional attributes for the node
    """
    
    id: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "children": self.children,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxonomyNodeDTO':
        """
        Create a DTO from a dictionary.
        
        Args:
            data: Dictionary representation of the DTO
            
        Returns:
            TaxonomyNodeDTO instance
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            children=data.get("children", []),
            attributes=data.get("attributes", {})
        )


@dataclass
class TaxonomyDTO:
    """
    Data transfer object for a complete taxonomy.
    
    Attributes:
        id: Taxonomy identifier
        name: Taxonomy name
        description: Taxonomy description
        nodes: Dictionary of nodes by ID
        root_id: ID of the root node
        version: Taxonomy version
        last_updated: Time when the taxonomy was last updated
        metadata: Additional metadata about the taxonomy
    """
    
    id: str
    name: str
    description: str = ""
    nodes: Dict[str, TaxonomyNodeDTO] = field(default_factory=dict)
    root_id: Optional[str] = None
    version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "root_id": self.root_id,
            "version": self.version,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxonomyDTO':
        """
        Create a DTO from a dictionary.
        
        Args:
            data: Dictionary representation of the DTO
            
        Returns:
            TaxonomyDTO instance
        """
        # Parse nodes
        nodes = {
            node_id: TaxonomyNodeDTO.from_dict(node_data)
            for node_id, node_data in data.get("nodes", {}).items()
        }
        
        # Parse datetime
        last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            nodes=nodes,
            root_id=data.get("root_id"),
            version=data.get("version", "1.0.0"),
            last_updated=last_updated,
            metadata=data.get("metadata", {})
        )
