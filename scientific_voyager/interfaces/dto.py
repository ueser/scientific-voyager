"""
Data Transfer Objects (DTOs) Module

This module defines the data structures used for communication between components
in the Scientific Voyager platform. These DTOs establish clear contracts for data
exchange between different layers of the system.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatementType(Enum):
    """Enumeration of scientific statement types."""
    CAUSAL = "causal"
    DESCRIPTIVE = "descriptive"
    INTERVENTION = "intervention"
    DEFINITIONAL = "definitional"
    UNKNOWN = "unknown"


class BiologicalLevel(Enum):
    """Enumeration of biological levels."""
    GENETIC = "genetic"
    MOLECULAR = "molecular"
    CELLULAR = "cellular"
    SYSTEMS = "systems"
    ORGANISM = "organism"
    UNKNOWN = "unknown"


class RelationshipType(Enum):
    """Enumeration of relationship types between statements."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    REFINES = "refines"
    CAUSAL = "causal"
    COMPOSITIONAL = "compositional"
    REGULATORY = "regulatory"
    UNKNOWN = "unknown"


@dataclass
class StatementDTO:
    """Data transfer object for scientific statements."""
    uid: Optional[str] = None
    text: str = ""
    source: Optional[str] = None
    statement_type: StatementType = StatementType.UNKNOWN
    biological_level: BiologicalLevel = BiologicalLevel.UNKNOWN
    confidence: float = 0.0
    entities: List[str] = None
    metadata: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.entities is None:
            self.entities = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class RelationshipDTO:
    """Data transfer object for relationships between statements."""
    uid: Optional[str] = None
    source_id: str = ""
    target_id: str = ""
    relationship_type: RelationshipType = RelationshipType.UNKNOWN
    confidence: float = 0.0
    description: str = ""
    metadata: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class InsightDTO:
    """Data transfer object for scientific insights."""
    uid: Optional[str] = None
    text: str = ""
    statement_ids: List[str] = None
    novelty_score: float = 0.0
    significance_score: float = 0.0
    evidence_strength: float = 0.0
    focus_area: Optional[str] = None
    biological_levels: List[BiologicalLevel] = None
    metadata: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.statement_ids is None:
            self.statement_ids = []
        if self.biological_levels is None:
            self.biological_levels = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class EmergentInsightDTO:
    """Data transfer object for emergent insights across biological levels."""
    uid: Optional[str] = None
    text: str = ""
    insight_ids: List[str] = None
    statement_ids: List[str] = None
    lower_level: BiologicalLevel = BiologicalLevel.UNKNOWN
    higher_level: BiologicalLevel = BiologicalLevel.UNKNOWN
    emergence_score: float = 0.0
    novelty_score: float = 0.0
    significance_score: float = 0.0
    evidence_strength: float = 0.0
    metadata: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.insight_ids is None:
            self.insight_ids = []
        if self.statement_ids is None:
            self.statement_ids = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TaskDTO:
    """Data transfer object for research tasks."""
    uid: Optional[str] = None
    title: str = ""
    description: str = ""
    insight_ids: List[str] = None
    priority: int = 0
    feasibility: float = 0.0
    status: str = "pending"
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    metadata: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.insight_ids is None:
            self.insight_ids = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TriangulationResultDTO:
    """Data transfer object for triangulation results."""
    uid: Optional[str] = None
    statement_ids: List[str] = None
    conclusion: str = ""
    confidence: float = 0.0
    supporting_evidence: List[str] = None
    contradicting_evidence: List[str] = None
    biological_level: BiologicalLevel = BiologicalLevel.UNKNOWN
    metadata: Dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.statement_ids is None:
            self.statement_ids = []
        if self.supporting_evidence is None:
            self.supporting_evidence = []
        if self.contradicting_evidence is None:
            self.contradicting_evidence = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ExplorationStateDTO:
    """Data transfer object for exploration state."""
    uid: Optional[str] = None
    status: str = "not_started"
    current_iteration: int = 0
    max_iterations: int = 0
    overarching_goal: str = ""
    initial_query: str = ""
    focus_areas: List[str] = None
    biological_level: Optional[BiologicalLevel] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    statements_extracted: int = 0
    insights_generated: int = 0
    emergent_insights: int = 0
    tasks_generated: int = 0
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.focus_areas is None:
            self.focus_areas = []
        if self.metadata is None:
            self.metadata = {}
        if self.start_time is None and self.status != "not_started":
            self.start_time = datetime.now()


@dataclass
class ConfigDTO:
    """Data transfer object for configuration settings."""
    environment: str = "development"
    debug: bool = False
    api_keys: Dict[str, str] = None
    llm_settings: Dict[str, Any] = None
    database_settings: Dict[str, Any] = None
    search_settings: Dict[str, Any] = None
    logging_level: str = "INFO"
    max_concurrent_tasks: int = 5
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.api_keys is None:
            self.api_keys = {}
        if self.llm_settings is None:
            self.llm_settings = {
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        if self.database_settings is None:
            self.database_settings = {
                "type": "sqlite",
                "path": "data/voyager.db"
            }
        if self.search_settings is None:
            self.search_settings = {
                "max_results": 50,
                "min_relevance": 0.7
            }
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResultDTO:
    """Data transfer object for search results."""
    uid: Optional[str] = None
    query: str = ""
    article_id: str = ""
    title: str = ""
    authors: List[str] = None
    abstract: str = ""
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    full_text: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.authors is None:
            self.authors = []
        if self.metadata is None:
            self.metadata = {}
