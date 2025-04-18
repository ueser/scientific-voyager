"""
Visualization Interface Module

This module defines the abstract interfaces for visualization components
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
import networkx as nx


class IGraphVisualizer(ABC):
    """
    Interface for graph visualization operations.
    Defines the contract for visualizing knowledge graphs and hierarchical models.
    """

    @abstractmethod
    def visualize_knowledge_graph(
        self,
        graph: nx.DiGraph,
        highlight_nodes: Optional[List[str]] = None,
        highlight_edges: Optional[List[tuple]] = None,
        layout: str = "force"
    ) -> Any:
        """
        Visualize a knowledge graph.
        
        Args:
            graph: NetworkX DiGraph to visualize
            highlight_nodes: Optional list of node IDs to highlight
            highlight_edges: Optional list of edge tuples to highlight
            layout: Graph layout algorithm to use
            
        Returns:
            Visualization object (implementation-specific)
            
        Raises:
            ValueError: If graph is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def visualize_hierarchical_model(
        self,
        hierarchical_graph: nx.DiGraph,
        biological_levels: Optional[List[str]] = None
    ) -> Any:
        """
        Visualize a hierarchical model across biological levels.
        
        Args:
            hierarchical_graph: NetworkX DiGraph representing the hierarchical model
            biological_levels: Optional list of biological levels to include
            
        Returns:
            Visualization object (implementation-specific)
            
        Raises:
            ValueError: If hierarchical_graph is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def export_visualization(
        self,
        visualization: Any,
        output_path: str,
        format: str = "html"
    ) -> bool:
        """
        Export a visualization to a file.
        
        Args:
            visualization: Visualization object to export
            output_path: Path to save the exported visualization
            format: Output format (html, png, svg, etc.)
            
        Returns:
            True if export was successful, False otherwise
            
        Raises:
            ValueError: If visualization or output_path is invalid
            Exception: For other unexpected errors
        """
        pass
