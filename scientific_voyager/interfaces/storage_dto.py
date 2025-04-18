"""
Data Transfer Objects for the storage system.

This module defines the DTOs used to represent stored data objects,
including their metadata and relationships.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from uuid import UUID, uuid4

from scientific_voyager.interfaces.extraction_dto import StatementDTO, EntityDTO, RelationDTO
from scientific_voyager.interfaces.classification_dto import ClassificationResultDTO


class BaseStoredObject:
    """Base class for stored objects with common metadata."""
    
    def __init__(self, uid=None, created_at=None, updated_at=None, version=1, metadata=None):
        self.uid = uid if uid is not None else uuid4()
        self.created_at = created_at if created_at is not None else datetime.now()
        self.updated_at = updated_at if updated_at is not None else datetime.now()
        self.version = version
        self.metadata = metadata if metadata is not None else {}


class StoredStatementDTO(BaseStoredObject):
    """DTO for a stored statement with its metadata."""
    
    def __init__(self, statement, source_id=None, source_type=None, extraction_id=None,
                 classification_ids=None, entity_ids=None, relation_ids=None, tags=None,
                 uid=None, created_at=None, updated_at=None, version=1, metadata=None):
        super().__init__(uid, created_at, updated_at, version, metadata)
        self.statement = statement
        self.source_id = source_id
        self.source_type = source_type
        self.extraction_id = extraction_id
        self.classification_ids = classification_ids if classification_ids is not None else []
        self.entity_ids = entity_ids if entity_ids is not None else []
        self.relation_ids = relation_ids if relation_ids is not None else []
        self.tags = tags if tags is not None else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "uid": str(self.uid),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "statement": {
                "text": self.statement.text,
                "types": getattr(self.statement, "types", []),
                "biological_scales": getattr(self.statement, "biological_scales", []),
                "cross_scale_relations": getattr(self.statement, "cross_scale_relations", []),
                "confidence": self.statement.confidence,
                "metadata": self.statement.metadata
            },
            "source_id": str(self.source_id) if self.source_id else None,
            "source_type": self.source_type,
            "extraction_id": str(self.extraction_id) if self.extraction_id else None,
            "classification_ids": [str(cid) for cid in self.classification_ids],
            "entity_ids": [str(eid) for eid in self.entity_ids],
            "relation_ids": [str(rid) for rid in self.relation_ids],
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoredStatementDTO':
        """Create from dictionary representation."""
        statement = StatementDTO(
            text=data["statement"]["text"],
            types=data["statement"].get("types", []),
            biological_scales=data["statement"].get("biological_scales", []),
            cross_scale_relations=data["statement"].get("cross_scale_relations", []),
            confidence=data["statement"]["confidence"],
            metadata=data["statement"].get("metadata", {})
        )
        
        return cls(
            uid=UUID(data["uid"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
            statement=statement,
            source_id=UUID(data["source_id"]) if data.get("source_id") else None,
            source_type=data.get("source_type"),
            extraction_id=UUID(data["extraction_id"]) if data.get("extraction_id") else None,
            classification_ids=[UUID(cid) for cid in data.get("classification_ids", [])],
            entity_ids=[UUID(eid) for eid in data.get("entity_ids", [])],
            relation_ids=[UUID(rid) for rid in data.get("relation_ids", [])],
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


class StoredClassificationDTO(BaseStoredObject):
    """DTO for a stored classification result with its metadata."""
    
    def __init__(self, classification, statement_id, validator_id=None, is_validated=False,
                 validation_score=0.0, feedback_ids=None, uid=None, created_at=None, 
                 updated_at=None, version=1, metadata=None):
        super().__init__(uid, created_at, updated_at, version, metadata)
        self.classification = classification
        self.statement_id = statement_id
        self.validator_id = validator_id
        self.is_validated = is_validated
        self.validation_score = validation_score
        self.feedback_ids = feedback_ids if feedback_ids is not None else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "uid": str(self.uid),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "classification": self.classification.to_dict(),
            "statement_id": str(self.statement_id),
            "validator_id": str(self.validator_id) if self.validator_id else None,
            "is_validated": self.is_validated,
            "validation_score": self.validation_score,
            "feedback_ids": [str(fid) for fid in self.feedback_ids],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoredClassificationDTO':
        """Create from dictionary representation."""
        from scientific_voyager.interfaces.classification_dto import ClassificationResultDTO
        
        return cls(
            uid=UUID(data["uid"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
            classification=ClassificationResultDTO.from_dict(data["classification"]),
            statement_id=UUID(data["statement_id"]),
            validator_id=UUID(data["validator_id"]) if data.get("validator_id") else None,
            is_validated=data["is_validated"],
            validation_score=data["validation_score"],
            feedback_ids=[UUID(fid) for fid in data.get("feedback_ids", [])],
            metadata=data.get("metadata", {})
        )


@dataclass
@dataclass
class StoredEntityDTO(BaseStoredObject):
    """DTO for a stored entity with its metadata."""
    
    entity: EntityDTO
    statement_ids: List[UUID] = field(default_factory=list)
    normalized_ids: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "uid": str(self.uid),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "entity": {
                "text": self.entity.text,
                "type": self.entity.type,
                "start_char": self.entity.start_char,
                "end_char": self.entity.end_char,
                "confidence": self.entity.confidence,
                "normalized_id": self.entity.normalized_id,
                "normalized_name": self.entity.normalized_name,
                "ontology_references": self.entity.ontology_references,
                "metadata": self.entity.metadata
            },
            "statement_ids": [str(sid) for sid in self.statement_ids],
            "normalized_ids": self.normalized_ids,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoredEntityDTO':
        """Create from dictionary representation."""
        entity = EntityDTO(
            text=data["entity"]["text"],
            type=data["entity"]["type"],
            start_char=data["entity"]["start_char"],
            end_char=data["entity"]["end_char"],
            confidence=data["entity"]["confidence"],
            normalized_id=data["entity"].get("normalized_id"),
            normalized_name=data["entity"].get("normalized_name"),
            ontology_references=data["entity"].get("ontology_references", {}),
            metadata=data["entity"].get("metadata", {})
        )
        
        return cls(
            uid=UUID(data["uid"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
            entity=entity,
            statement_ids=[UUID(sid) for sid in data.get("statement_ids", [])],
            normalized_ids=data.get("normalized_ids", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
@dataclass
class StoredRelationDTO(BaseStoredObject):
    """DTO for a stored relation with its metadata."""
    
    relation: RelationDTO
    source_entity_id: UUID
    target_entity_id: UUID
    statement_ids: List[UUID] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "uid": str(self.uid),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "relation": {
                "relation_type": self.relation.relation_type,
                "confidence": self.relation.confidence,
                "bidirectional": self.relation.bidirectional,
                "normalized_relation_type": self.relation.normalized_relation_type,
                "metadata": self.relation.metadata
            },
            "statement_ids": [str(sid) for sid in self.statement_ids],
            "source_entity_id": str(self.source_entity_id),
            "target_entity_id": str(self.target_entity_id),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], source_entity: EntityDTO, target_entity: EntityDTO) -> 'StoredRelationDTO':
        """Create from dictionary representation."""
        relation = RelationDTO(
            source_entity=source_entity,
            target_entity=target_entity,
            relation_type=data["relation"]["relation_type"],
            confidence=data["relation"]["confidence"],
            bidirectional=data["relation"]["bidirectional"],
            normalized_relation_type=data["relation"].get("normalized_relation_type"),
            metadata=data["relation"].get("metadata", {})
        )
        
        return cls(
            uid=UUID(data["uid"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
            relation=relation,
            statement_ids=[UUID(sid) for sid in data.get("statement_ids", [])],
            source_entity_id=UUID(data["source_entity_id"]),
            target_entity_id=UUID(data["target_entity_id"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class StorageStatsDTO:
    """DTO for storage system statistics."""
    
    total_statements: int = 0
    total_classifications: int = 0
    total_entities: int = 0
    total_relations: int = 0
    statement_types: Dict[str, int] = field(default_factory=dict)
    entity_types: Dict[str, int] = field(default_factory=dict)
    relation_types: Dict[str, int] = field(default_factory=dict)
    biological_scales: Dict[str, int] = field(default_factory=dict)
    classification_types: Dict[str, int] = field(default_factory=dict)
    storage_size_bytes: int = 0
    index_size_bytes: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_statements": self.total_statements,
            "total_classifications": self.total_classifications,
            "total_entities": self.total_entities,
            "total_relations": self.total_relations,
            "statement_types": self.statement_types,
            "entity_types": self.entity_types,
            "relation_types": self.relation_types,
            "biological_scales": self.biological_scales,
            "classification_types": self.classification_types,
            "storage_size_bytes": self.storage_size_bytes,
            "index_size_bytes": self.index_size_bytes,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageStatsDTO':
        """Create from dictionary representation."""
        return cls(
            total_statements=data["total_statements"],
            total_classifications=data["total_classifications"],
            total_entities=data["total_entities"],
            total_relations=data["total_relations"],
            statement_types=data["statement_types"],
            entity_types=data["entity_types"],
            relation_types=data["relation_types"],
            biological_scales=data["biological_scales"],
            classification_types=data["classification_types"],
            storage_size_bytes=data["storage_size_bytes"],
            index_size_bytes=data["index_size_bytes"],
            last_updated=datetime.fromisoformat(data["last_updated"])
        )
