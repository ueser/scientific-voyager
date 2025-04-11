"""
Execution Engine Module

This module implements the main execution engine for the Scientific Voyager platform,
coordinating the various components and managing the exploration workflow.
Uses OpenAI's GPT-4o for NLP tasks, reasoning, classification, and decision making,
with a focus on identifying hierarchical emergent behaviors through generalized triangulation.
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
import time
from datetime import datetime

# Core components
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
from scientific_voyager.utils.llm_client import LLMClient
from scientific_voyager.utils.config import Config

# Visualization components
from scientific_voyager.visualization.graph_visualizer import GraphVisualizer


class ExecutionEngine:
    """
    Main execution engine for the Scientific Voyager platform.
    Uses OpenAI's GPT-4o for NLP tasks, reasoning, classification, and decision making.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the execution engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        
        # Get OpenAI API key and model from config
        self.openai_api_key = self.config.get("openai_api_key")
        self.model = self.config.get("model", "gpt-4o")
        
        # Initialize LLM client if API key is available
        self.llm_client = None
        if self.openai_api_key:
            self.llm_client = LLMClient(
                api_key=self.openai_api_key,
                model=self.model
            )
            self.logger.info(f"Initialized LLM client with model: {self.model}")
        else:
            self.logger.warning("No OpenAI API key provided. LLM features will not be available.")
        
        # Core components
        self.data_manager = None
        self.data_source = None
        self.statement_extractor = None
        self.knowledge_graph = None
        self.insights_generator = None
        self.task_generator = None
        
        # New components
        self.processing_pipeline = None
        self.database_manager = None
        self.hierarchical_model = None
        self.triangulation_engine = None
        self.emergent_insights_manager = None
        self.graph_visualizer = None
        
        # Exploration state
        self.exploration_state = {
            "status": "not_started",
            "current_iteration": 0,
            "max_iterations": 0,
            "overarching_goal": "",
            "initial_query": "",
            "focus_areas": [],
            "biological_level": None,
            "start_time": None,
            "end_time": None,
            "statements_extracted": 0,
            "insights_generated": 0,
            "emergent_insights": 0,
            "tasks_generated": 0
        }
        
    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger for the execution engine.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("scientific_voyager")
        logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        return logger
        
    def initialize_components(self) -> None:
        """
        Initialize all components of the execution engine.
        """
        self.logger.info("Initializing Scientific Voyager components")
        
        # Initialize data manager
        storage_type = self.config.get("storage_type", "local")
        self.data_manager = DataManager(storage_type=storage_type)
        self.logger.info(f"Initialized data manager with storage type: {storage_type}")
        
        # Initialize database manager if configured
        if self.config.get("use_neo4j") or self.config.get("use_chroma"):
            db_config = {}
            if self.config.get("use_neo4j"):
                db_config.update({
                    "use_neo4j": True,
                    "neo4j_uri": self.config.get("neo4j_uri", "bolt://localhost:7687"),
                    "neo4j_username": self.config.get("neo4j_username", "neo4j"),
                    "neo4j_password": self.config.get("neo4j_password")
                })
                
            if self.config.get("use_chroma"):
                db_config.update({
                    "use_chroma": True,
                    "chroma_host": self.config.get("chroma_host", "localhost"),
                    "chroma_port": self.config.get("chroma_port", 8000)
                })
                
            self.database_manager = DatabaseManager(config=db_config)
            self.logger.info("Initialized database manager")
        
        # Initialize PubMed data source
        pubmed_api_key = self.config.get("pubmed_api_key")
        self.data_source = PubMedSource(
            api_key=pubmed_api_key,
            openai_api_key=self.openai_api_key,
            model=self.model
        )
        self.logger.info("Initialized PubMed data source")
        
        # Initialize statement extractor
        self.statement_extractor = StatementExtractor(
            api_key=self.openai_api_key,
            model=self.model
        )
        self.logger.info("Initialized statement extractor")
        
        # Initialize processing pipeline
        processing_config = {
            "batch_size": self.config.get("batch_size", 10),
            "max_workers": self.config.get("max_workers", 4)
        }
        self.processing_pipeline = ProcessingPipeline(
            data_source=self.data_source,
            statement_extractor=self.statement_extractor,
            llm_client=self.llm_client,
            config=processing_config
        )
        self.logger.info("Initialized processing pipeline")
        
        # Initialize knowledge graph
        self.knowledge_graph = KnowledgeGraph()
        self.logger.info("Initialized knowledge graph")
        
        # Initialize hierarchical model
        self.hierarchical_model = HierarchicalModel(
            llm_client=self.llm_client
        )
        self.logger.info("Initialized hierarchical model")
        
        # Initialize triangulation engine
        self.triangulation_engine = TriangulationEngine(
            llm_client=self.llm_client
        )
        self.logger.info("Initialized triangulation engine")
        
        # Initialize insights generator
        self.insights_generator = InsightsGenerator(
            knowledge_graph=self.knowledge_graph,
            api_key=self.openai_api_key,
            model=self.model
        )
        self.logger.info("Initialized insights generator")
        
        # Initialize emergent insights manager
        self.emergent_insights_manager = EmergentInsightsManager(
            triangulation_engine=self.triangulation_engine,
            llm_client=self.llm_client
        )
        self.logger.info("Initialized emergent insights manager")
        
        # Initialize task generator
        self.task_generator = TaskGenerator(
            knowledge_graph=self.knowledge_graph,
            insights_generator=self.insights_generator,
            api_key=self.openai_api_key,
            model=self.model
        )
        self.logger.info("Initialized task generator")
        
        # Initialize visualization components
        self.graph_visualizer = GraphVisualizer()
        self.logger.info("Initialized graph visualizer")
        
        self.logger.info("All components initialized successfully")
        
    def run_exploration(
        self,
        overarching_goal: str,
        initial_query: str,
        max_iterations: int = 10,
        focus_areas: Optional[List[str]] = None,
        biological_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run an autonomous exploration process.
        
        Args:
            overarching_goal: The main scientific goal guiding exploration
            initial_query: Initial search query to start exploration
            max_iterations: Maximum number of exploration iterations
            focus_areas: Optional list of focus areas to prioritize
            biological_level: Optional biological level to focus on
            
        Returns:
            Dictionary containing exploration results
        """
        # Update exploration state
        self.exploration_state = {
            "status": "running",
            "current_iteration": 0,
            "max_iterations": max_iterations,
            "overarching_goal": overarching_goal,
            "initial_query": initial_query,
            "focus_areas": focus_areas or [],
            "biological_level": biological_level,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "statements_extracted": 0,
            "insights_generated": 0,
            "emergent_insights": 0,
            "tasks_generated": 0
        }
        
        self.logger.info(f"Starting exploration with goal: {overarching_goal}")
        self.logger.info(f"Initial query: {initial_query}")
        
        try:
            # Ensure all components are initialized
            if not all([self.data_source, self.statement_extractor, self.knowledge_graph,
                       self.insights_generator, self.task_generator]):
                self.initialize_components()
            
            # Run the exploration process
            for iteration in range(max_iterations):
                self.exploration_state["current_iteration"] = iteration + 1
                self.logger.info(f"Starting iteration {iteration + 1} of {max_iterations}")
                
                # 1. Fetch relevant scientific literature based on current query
                query = initial_query if iteration == 0 else self._generate_next_query()
                self.logger.info(f"Using query: {query}")
                
                # 2. Process the literature and extract statements
                # This is a placeholder for the actual implementation
                self.logger.info("Processing literature and extracting statements...")
                time.sleep(1)  # Simulate processing time
                self.exploration_state["statements_extracted"] += 5  # Placeholder
                
                # 3. Categorize statements using hierarchical model
                self.logger.info("Categorizing statements using hierarchical model...")
                time.sleep(1)  # Simulate processing time
                
                # 4. Generate insights using triangulation
                self.logger.info("Generating insights using triangulation...")
                time.sleep(1)  # Simulate processing time
                self.exploration_state["insights_generated"] += 3  # Placeholder
                
                # 5. Identify emergent insights
                self.logger.info("Identifying emergent insights...")
                time.sleep(1)  # Simulate processing time
                self.exploration_state["emergent_insights"] += 1  # Placeholder
                
                # 6. Generate next tasks
                self.logger.info("Generating next research tasks...")
                time.sleep(1)  # Simulate processing time
                self.exploration_state["tasks_generated"] += 2  # Placeholder
                
                self.logger.info(f"Completed iteration {iteration + 1}")
            
            # Mark exploration as complete
            self.exploration_state["status"] = "completed"
            self.exploration_state["end_time"] = datetime.now().isoformat()
            
            self.logger.info("Exploration completed successfully")
            return {
                "status": "success",
                "message": "Exploration completed successfully",
                "results": {
                    "statements_extracted": self.exploration_state["statements_extracted"],
                    "insights_generated": self.exploration_state["insights_generated"],
                    "emergent_insights": self.exploration_state["emergent_insights"],
                    "tasks_generated": self.exploration_state["tasks_generated"]
                }
            }
            
        except Exception as e:
            self.exploration_state["status"] = "failed"
            self.exploration_state["end_time"] = datetime.now().isoformat()
            
            error_message = f"Exploration failed: {str(e)}"
            self.logger.error(error_message)
            return {
                "status": "error",
                "message": error_message
            }
        
    def get_exploration_status(self) -> Dict[str, Any]:
        """
        Get the current status of the exploration process.
        
        Returns:
            Dictionary containing current exploration status
        """
        return self.exploration_state
    
    def _generate_next_query(self) -> str:
        """
        Generate the next search query based on current state.
        
        Returns:
            Next search query string
        """
        # This is a placeholder for the actual implementation
        # In a real implementation, this would use the task generator
        # to determine the next most promising research direction
        return f"Extended research on {self.exploration_state['initial_query']}"
    
    def visualize_knowledge_graph(self, output_path: Optional[str] = None) -> Any:
        """
        Visualize the current knowledge graph.
        
        Args:
            output_path: Optional path to save the visualization
            
        Returns:
            Visualization object
        """
        if not self.graph_visualizer or not self.knowledge_graph:
            self.logger.warning("Cannot visualize: graph visualizer or knowledge graph not initialized")
            return None
            
        return self.graph_visualizer.visualize_knowledge_graph(
            graph=self.knowledge_graph.graph,
            output_path=output_path
        )
    
    def visualize_biological_levels(self, output_path: Optional[str] = None) -> Any:
        """
        Visualize statements by biological level.
        
        Args:
            output_path: Optional path to save the visualization
            
        Returns:
            Visualization object
        """
        if not self.graph_visualizer or not self.hierarchical_model:
            self.logger.warning("Cannot visualize: graph visualizer or hierarchical model not initialized")
            return None
            
        # This is a placeholder for the actual implementation
        # In a real implementation, this would get the actual data from the hierarchical model
        data = {
            "genetic": [],
            "molecular": [],
            "cellular": [],
            "systems": [],
            "organism": []
        }
        
        return self.graph_visualizer.visualize_biological_levels(
            data=data,
            output_path=output_path
        )
