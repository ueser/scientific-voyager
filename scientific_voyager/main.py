"""
Scientific Voyager Main Application

This module serves as the main entry point for the Scientific Voyager platform.
Uses OpenAI's GPT-4o for NLP tasks, reasoning, classification, and decision making,
with a focus on identifying hierarchical emergent behaviors through generalized triangulation.
"""

import argparse
import logging
import os
import sys
from typing import Dict, List, Optional, Any

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


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    log_level = getattr(logging, level.upper())
    
    logger = logging.getLogger("scientific_voyager")
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Scientific Voyager - AI-driven exploratory research platform"
    )
    
    # Exploration parameters
    exploration_group = parser.add_argument_group("Exploration Parameters")
    exploration_group.add_argument(
        "--goal", 
        type=str, 
        help="Overarching scientific goal for exploration"
    )
    
    exploration_group.add_argument(
        "--query", 
        type=str, 
        help="Initial search query to start exploration"
    )
    
    exploration_group.add_argument(
        "--iterations", 
        type=int, 
        default=10,
        help="Maximum number of exploration iterations"
    )
    
    exploration_group.add_argument(
        "--focus", 
        type=str, 
        nargs="+",
        help="Focus areas to prioritize during exploration"
    )
    
    exploration_group.add_argument(
        "--biological-level",
        type=str,
        choices=["genetic", "molecular", "cellular", "systems", "organism"],
        help="Biological level to focus on"
    )
    
    # API configuration
    api_group = parser.add_argument_group("API Configuration")
    api_group.add_argument(
        "--openai-api-key",
        type=str,
        help="OpenAI API key (defaults to OPENAI_API_KEY environment variable)"
    )
    
    api_group.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        choices=["gpt-4o", "gpt-4o-mini"],
        help="OpenAI model to use (defaults to gpt-4o)"
    )
    
    api_group.add_argument(
        "--pubmed-api-key",
        type=str,
        help="PubMed API key (defaults to PUBMED_API_KEY environment variable)"
    )
    
    # Database configuration
    db_group = parser.add_argument_group("Database Configuration")
    db_group.add_argument(
        "--use-neo4j",
        action="store_true",
        help="Use Neo4j for graph storage"
    )
    
    db_group.add_argument(
        "--neo4j-uri",
        type=str,
        default="bolt://localhost:7687",
        help="Neo4j connection URI"
    )
    
    db_group.add_argument(
        "--neo4j-username",
        type=str,
        default="neo4j",
        help="Neo4j username"
    )
    
    db_group.add_argument(
        "--neo4j-password",
        type=str,
        help="Neo4j password"
    )
    
    db_group.add_argument(
        "--use-chroma",
        action="store_true",
        help="Use ChromaDB for vector storage"
    )
    
    db_group.add_argument(
        "--chroma-host",
        type=str,
        default="localhost",
        help="ChromaDB host"
    )
    
    db_group.add_argument(
        "--chroma-port",
        type=int,
        default=8000,
        help="ChromaDB port"
    )
    
    # System configuration
    system_group = parser.add_argument_group("System Configuration")
    system_group.add_argument(
        "--log-level", 
        type=str, 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    system_group.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for processing"
    )
    
    system_group.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of worker threads"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the Scientific Voyager application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    args = parse_arguments()
    logger = setup_logging(args.log_level)
    
    logger.info("Starting Scientific Voyager platform")
    
    # Initialize configuration
    config = Config()
    
    # Set API keys from command line arguments if provided
    if args.openai_api_key:
        config.set("OPENAI_API_KEY", args.openai_api_key)
    elif not config.get_openai_api_key():
        logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or use --openai-api-key.")
        
    if args.pubmed_api_key:
        config.set("PUBMED_API_KEY", args.pubmed_api_key)
        
    # Set model from command line argument
    config.set("OPENAI_MODEL", args.model)
    
    # Set database configuration
    db_config = {}
    if args.use_neo4j:
        db_config.update({
            "use_neo4j": True,
            "neo4j_uri": args.neo4j_uri,
            "neo4j_username": args.neo4j_username,
            "neo4j_password": args.neo4j_password
        })
        
    if args.use_chroma:
        db_config.update({
            "use_chroma": True,
            "chroma_host": args.chroma_host,
            "chroma_port": args.chroma_port
        })
    
    # Set processing configuration
    processing_config = {
        "batch_size": args.batch_size,
        "max_workers": args.max_workers
    }
    
    # Verify OpenAI API key is available
    openai_api_key = config.get_openai_api_key()
    if not openai_api_key:
        logger.error("OpenAI API key is required for Scientific Voyager to function.")
        return 1
        
    logger.info(f"Using OpenAI model: {config.get_model_name()}")
    
    # Initialize components
    try:
        # Initialize LLM client
        llm_client = LLMClient(
            api_key=openai_api_key,
            model=config.get_model_name()
        )
        
        # Initialize database manager if configured
        database_manager = None
        if db_config:
            database_manager = DatabaseManager(config=db_config)
            logger.info("Initialized database manager")
        
        # Initialize data source
        pubmed_source = PubMedSource(
            api_key=config.get_pubmed_api_key(),
            openai_api_key=openai_api_key,
            model=config.get_model_name()
        )
        logger.info("Initialized PubMed data source")
        
        # Initialize statement extractor
        statement_extractor = StatementExtractor(
            api_key=openai_api_key,
            model=config.get_model_name()
        )
        logger.info("Initialized statement extractor")
        
        # Initialize processing pipeline
        processing_pipeline = ProcessingPipeline(
            data_source=pubmed_source,
            statement_extractor=statement_extractor,
            llm_client=llm_client,
            config=processing_config
        )
        logger.info("Initialized processing pipeline")
        
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        logger.info("Initialized knowledge graph")
        
        # Initialize hierarchical model
        hierarchical_model = HierarchicalModel(
            llm_client=llm_client
        )
        logger.info("Initialized hierarchical model")
        
        # Initialize triangulation engine
        triangulation_engine = TriangulationEngine(
            llm_client=llm_client
        )
        logger.info("Initialized triangulation engine")
        
        # Initialize insights generator
        insights_generator = InsightsGenerator(
            knowledge_graph=knowledge_graph,
            api_key=openai_api_key,
            model=config.get_model_name()
        )
        logger.info("Initialized insights generator")
        
        # Initialize emergent insights manager
        emergent_insights_manager = EmergentInsightsManager(
            triangulation_engine=triangulation_engine,
            llm_client=llm_client
        )
        logger.info("Initialized emergent insights manager")
        
        # Initialize task generator
        task_generator = TaskGenerator(
            knowledge_graph=knowledge_graph,
            insights_generator=insights_generator,
            api_key=openai_api_key,
            model=config.get_model_name()
        )
        logger.info("Initialized task generator")
        
        # Initialize visualization components
        graph_visualizer = GraphVisualizer()
        logger.info("Initialized graph visualizer")
        
        # Initialize the execution engine with all components
        engine_config = {
            "openai_api_key": openai_api_key,
            "model": config.get_model_name(),
            "pubmed_api_key": config.get_pubmed_api_key(),
            **db_config,
            **processing_config
        }
        
        engine = ExecutionEngine(config=engine_config)
        engine.data_manager = DataManager(storage_type="local")
        engine.data_source = pubmed_source
        engine.statement_extractor = statement_extractor
        engine.knowledge_graph = knowledge_graph
        engine.insights_generator = insights_generator
        engine.task_generator = task_generator
        
        # Add new components
        engine.processing_pipeline = processing_pipeline
        engine.database_manager = database_manager
        engine.hierarchical_model = hierarchical_model
        engine.triangulation_engine = triangulation_engine
        engine.emergent_insights_manager = emergent_insights_manager
        engine.graph_visualizer = graph_visualizer
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        return 1
    
    # Run exploration if goal and query are provided
    if args.goal and args.query:
        logger.info(f"Running exploration with goal: {args.goal}")
        logger.info(f"Initial query: {args.query}")
        
        exploration_params = {
            "overarching_goal": args.goal,
            "initial_query": args.query,
            "max_iterations": args.iterations,
            "focus_areas": args.focus
        }
        
        # Add biological level if specified
        if args.biological_level:
            exploration_params["biological_level"] = args.biological_level
            logger.info(f"Focusing on biological level: {args.biological_level}")
        
        result = engine.run_exploration(**exploration_params)
        
        if result["status"] != "success":
            logger.error(f"Exploration failed: {result['message']}")
            return 1
    else:
        logger.info("No goal or query provided, skipping exploration")
    
    logger.info("Scientific Voyager platform execution completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
