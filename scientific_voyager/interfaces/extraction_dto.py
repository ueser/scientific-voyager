"""
Data Transfer Objects for the abstract extraction and normalization pipeline.

This module defines the DTOs used to represent extracted entities, relations,
and statements from scientific abstracts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class EntityDTO:
    """Data Transfer Object for extracted entities."""
    
    text: str
    type: str
    start_char: int
    end_char: int
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    normalized_id: Optional[str] = None
    normalized_name: Optional[str] = None
    ontology_references: Dict[str, str] = field(default_factory=dict)


@dataclass
class RelationDTO:
    """Data Transfer Object for extracted relations between entities."""
    
    source_entity: EntityDTO
    target_entity: EntityDTO
    relation_type: str
    confidence: float
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    normalized_relation_type: Optional[str] = None


@dataclass
class CrossScaleRelationDTO:
    """DTO for explicit relationships between different biological scales within a statement."""
    source_scale: str
    target_scale: str
    relation_type: str  # e.g., 'causal', 'descriptive'
    description: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class StatementDTO:
    """Data Transfer Object for scientific statements extracted from text, supporting multi-label and cross-scale relationships."""
    text: str
    types: List[str] = field(default_factory=list)
    biological_scales: List[str] = field(default_factory=list)
    confidence: float = 1.0
    entities: List[EntityDTO] = field(default_factory=list)
    relations: List[RelationDTO] = field(default_factory=list)
    cross_scale_relations: List[CrossScaleRelationDTO] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence_level: Optional[str] = None
    source_text: Optional[str] = None


@dataclass
class ExtractionResultDTO:
    """Data Transfer Object for the complete extraction result."""
    
    source_text: str
    entities: List[EntityDTO] = field(default_factory=list)
    relations: List[RelationDTO] = field(default_factory=list)
    statements: List[StatementDTO] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    
    def get_entities_by_type(self, entity_type: str) -> List[EntityDTO]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.type == entity_type]
    
    def get_relations_by_type(self, relation_type: str) -> List[RelationDTO]:
        """Get all relations of a specific type."""
        return [r for r in self.relations if r.relation_type == relation_type]
    
    def get_statements_by_type(self, statement_type: str) -> List[StatementDTO]:
        """Get all statements of a specific type."""
        return [s for s in self.statements if s.type == statement_type]


@dataclass
class BiologicalEntityDTO(EntityDTO):
    """Data Transfer Object for biological entities."""
    
    organism: Optional[str] = None
    taxonomy_id: Optional[str] = None
    biological_level: Optional[str] = None  # molecular, cellular, tissue, organ, system, organism
    biological_role: Optional[str] = None  # gene, protein, metabolite, etc.


@dataclass
class MolecularEntityDTO(BiologicalEntityDTO):
    """Data Transfer Object for molecular entities."""
    
    molecular_type: Optional[str] = None  # gene, protein, metabolite, etc.
    sequence: Optional[str] = None
    structure: Optional[str] = None
    molecular_weight: Optional[float] = None
    biological_level: str = "molecular"


@dataclass
class GeneDTO(MolecularEntityDTO):
    """Data Transfer Object for gene entities."""
    
    gene_id: Optional[str] = None
    gene_symbol: Optional[str] = None
    molecular_type: str = "gene"


@dataclass
class ProteinDTO(MolecularEntityDTO):
    """Data Transfer Object for protein entities."""
    
    protein_id: Optional[str] = None
    protein_name: Optional[str] = None
    gene_id: Optional[str] = None
    molecular_type: str = "protein"


@dataclass
class DiseaseDTO(BiologicalEntityDTO):
    """Data Transfer Object for disease entities."""
    
    disease_id: Optional[str] = None
    disease_name: Optional[str] = None
    biological_level: Optional[str] = None  # can span multiple levels


@dataclass
class BiologicalProcessDTO(BiologicalEntityDTO):
    """Data Transfer Object for biological process entities."""
    
    process_id: Optional[str] = None
    process_name: Optional[str] = None
    biological_level: Optional[str] = None  # can span multiple levels
