"""
Graph Visualizer Module

This module provides visualization capabilities for the knowledge graph
and other structured data in the Scientific Voyager platform.
"""

from typing import Dict, List, Optional, Tuple, Any
import networkx as nx
import matplotlib.pyplot as plt


class GraphVisualizer:
    """
    Visualizes knowledge graphs and other structured data.
    """

    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the graph visualizer.
        
        Args:
            figsize: Figure size for matplotlib plots
        """
        self.figsize = figsize
        
    def visualize_knowledge_graph(
        self,
        graph: nx.DiGraph,
        highlight_nodes: Optional[List[str]] = None,
        node_color_map: Optional[Dict[str, str]] = None,
        edge_color_map: Optional[Dict[str, str]] = None,
        output_path: Optional[str] = None
    ) -> Any:
        """
        Visualize a knowledge graph.
        
        Args:
            graph: NetworkX DiGraph to visualize
            highlight_nodes: Optional list of node IDs to highlight
            node_color_map: Optional mapping of node types to colors
            edge_color_map: Optional mapping of edge types to colors
            output_path: Optional path to save the visualization
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Default color maps if not provided
        if node_color_map is None:
            node_color_map = {
                "genetic": "blue",
                "molecular": "green",
                "cellular": "orange",
                "systems": "red",
                "organism": "purple",
                "default": "gray"
            }
            
        if edge_color_map is None:
            edge_color_map = {
                "supports": "green",
                "contradicts": "red",
                "relates_to": "blue",
                "default": "gray"
            }
            
        # Prepare node colors
        node_colors = []
        for node in graph.nodes():
            if highlight_nodes and node in highlight_nodes:
                node_colors.append("yellow")
            else:
                node_type = graph.nodes[node].get("biological_level", "default")
                node_colors.append(node_color_map.get(node_type, node_color_map["default"]))
                
        # Prepare edge colors
        edge_colors = []
        for edge in graph.edges():
            edge_type = graph.edges[edge].get("relationship_type", "default")
            edge_colors.append(edge_color_map.get(edge_type, edge_color_map["default"]))
            
        # Draw the graph
        pos = nx.spring_layout(graph)
        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, ax=ax)
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, ax=ax)
        nx.draw_networkx_labels(graph, pos, ax=ax)
        
        plt.title("Scientific Voyager Knowledge Graph")
        plt.axis("off")
        
        if output_path:
            plt.savefig(output_path)
            
        return fig
        
    def visualize_biological_levels(
        self,
        data: Dict[str, List[Dict]],
        output_path: Optional[str] = None
    ) -> Any:
        """
        Visualize statements by biological level.
        
        Args:
            data: Dictionary mapping biological levels to lists of statements
            output_path: Optional path to save the visualization
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        levels = list(data.keys())
        counts = [len(statements) for statements in data.values()]
        
        ax.bar(levels, counts)
        ax.set_xlabel("Biological Level")
        ax.set_ylabel("Number of Statements")
        ax.set_title("Statements by Biological Level")
        
        if output_path:
            plt.savefig(output_path)
            
        return fig
