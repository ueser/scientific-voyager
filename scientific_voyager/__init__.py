"""
Scientific Voyager

An AI-driven exploratory research platform for scientific literature,
focusing on multi-scale biological understanding and hierarchical emergent behaviors.
"""

__version__ = "0.1.0"
__author__ = "Scientific Voyager Team"

# Core components
from scientific_voyager.core.execution_engine import ExecutionEngine
from scientific_voyager.core.statement_extractor import StatementExtractor
from scientific_voyager.core.knowledge_graph import KnowledgeGraph
from scientific_voyager.core.insights_generator import InsightsGenerator
from scientific_voyager.core.task_generator import TaskGenerator
from scientific_voyager.core.triangulation import TriangulationEngine
from scientific_voyager.core.hierarchical_model import HierarchicalModel
from scientific_voyager.core.emergent_insights import EmergentInsightsManager

# Data components
from scientific_voyager.data.data_manager import DataManager
from scientific_voyager.data.pubmed_source import PubMedSource
from scientific_voyager.data.processing_pipeline import ProcessingPipeline
from scientific_voyager.data.database_manager import DatabaseManager

# Utility components
from scientific_voyager.utils.config import Config
from scientific_voyager.utils.llm_client import LLMClient

# Visualization components
from scientific_voyager.visualization.graph_visualizer import GraphVisualizer