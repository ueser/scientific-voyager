"""
Hierarchical Model Module

This module implements the multi-scale hierarchical model for categorizing and
analyzing scientific statements across different biological levels, with a focus
on identifying hierarchical emergent behaviors.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import logging
import networkx as nx

from scientific_voyager.utils.llm_client import LLMClient


class HierarchicalModel:
    """
    Implements a multi-scale hierarchical model for categorizing and analyzing
    scientific statements across different biological levels.
    """

    # Define biological levels from lowest to highest
    BIOLOGICAL_LEVELS = ["genetic", "molecular", "cellular", "systems", "organism"]
    
    # Define statement types
    STATEMENT_TYPES = ["causal", "descriptive", "intervention", "definitional"]
    
    def __init__(self, llm_client: Optional[LLMClient] = None, config: Optional[Dict] = None):
        """
        Initialize the hierarchical model.
        
        Args:
            llm_client: LLM client for classification and analysis
            config: Configuration dictionary
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.logger = logging.getLogger("scientific_voyager.hierarchical_model")
        self.hierarchy_graph = nx.DiGraph()
        
    def classify_statement(self, statement: str) -> Dict:
        """
        Classify a scientific statement by biological level and type.
        
        Args:
            statement: The scientific statement to classify
            
        Returns:
            Classification result with biological level, type, and confidence
        """
        if not self.llm_client:
            self.logger.warning("No LLM client available for classification")
            return {
                "statement": statement,
                "biological_level": None,
                "type": None,
                "confidence": 0.0
            }
            
        return self.llm_client.categorize_statement(statement)
        
    def map_hierarchical_relationships(
        self,
        statements: List[Dict]
    ) -> nx.DiGraph:
        """
        Map hierarchical relationships between statements across biological levels.
        
        Args:
            statements: List of classified scientific statements
            
        Returns:
            NetworkX DiGraph representing the hierarchical relationships
        """
        # Create a new directed graph
        graph = nx.DiGraph()
        
        # Add all statements as nodes
        for i, statement in enumerate(statements):
            node_id = f"statement_{i}"
            graph.add_node(
                node_id,
                statement=statement.get("statement", ""),
                biological_level=statement.get("biological_level", "unknown"),
                type=statement.get("type", "unknown"),
                confidence=statement.get("confidence", 0.0)
            )
        
        # Map relationships between statements across adjacent biological levels
        for level_idx in range(len(self.BIOLOGICAL_LEVELS) - 1):
            lower_level = self.BIOLOGICAL_LEVELS[level_idx]
            higher_level = self.BIOLOGICAL_LEVELS[level_idx + 1]
            
            # Get statements at each level
            lower_nodes = [
                node for node, attrs in graph.nodes(data=True)
                if attrs.get("biological_level") == lower_level
            ]
            
            higher_nodes = [
                node for node, attrs in graph.nodes(data=True)
                if attrs.get("biological_level") == higher_level
            ]
            
            # If we have statements at both levels, identify relationships
            if lower_nodes and higher_nodes:
                self._identify_cross_level_relationships(
                    graph, lower_nodes, higher_nodes, lower_level, higher_level
                )
        
        self.hierarchy_graph = graph
        return graph
        
    def _identify_cross_level_relationships(
        self,
        graph: nx.DiGraph,
        lower_nodes: List[str],
        higher_nodes: List[str],
        lower_level: str,
        higher_level: str
    ) -> None:
        """
        Identify relationships between statements at adjacent biological levels.
        
        Args:
            graph: The hierarchical graph
            lower_nodes: Nodes at the lower biological level
            higher_nodes: Nodes at the higher biological level
            lower_level: The lower biological level name
            higher_level: The higher biological level name
        """
        if not self.llm_client:
            self.logger.warning("No LLM client available for relationship identification")
            return
            
        # For each pair of lower and higher level statements, check for relationships
        for lower_node in lower_nodes:
            lower_statement = graph.nodes[lower_node].get("statement", "")
            
            for higher_node in higher_nodes:
                higher_statement = graph.nodes[higher_node].get("statement", "")
                
                # Use LLM to determine if there's a relationship
                relationship = self._check_relationship(
                    lower_statement, higher_statement, lower_level, higher_level
                )
                
                if relationship["has_relationship"]:
                    graph.add_edge(
                        lower_node,
                        higher_node,
                        relationship_type=relationship["relationship_type"],
                        confidence=relationship["confidence"],
                        description=relationship["description"]
                    )
                    
    def _check_relationship(
        self,
        lower_statement: str,
        higher_statement: str,
        lower_level: str,
        higher_level: str
    ) -> Dict:
        """
        Check if there's a hierarchical relationship between two statements.
        
        Args:
            lower_statement: Statement at the lower biological level
            higher_statement: Statement at the higher biological level
            lower_level: The lower biological level name
            higher_level: The higher biological level name
            
        Returns:
            Dictionary with relationship information
        """
        # Create system prompt for relationship checking
        system_message = """
        You are an expert in biological hierarchies. Your task is to determine if there is a 
        hierarchical relationship between two scientific statements at different biological levels.
        
        A hierarchical relationship exists when:
        1. The lower-level mechanism contributes to or explains the higher-level phenomenon
        2. The higher-level phenomenon emerges from or depends on the lower-level mechanism
        3. There is a causal or compositional relationship between the two levels
        
        Format your response as a JSON object.
        """
        
        # Create user prompt for relationship checking
        prompt = f"""
        Determine if there is a hierarchical relationship between these two scientific statements:
        
        Lower-level statement ({lower_level}): "{lower_statement}"
        
        Higher-level statement ({higher_level}): "{higher_statement}"
        
        Provide:
        - has_relationship: true/false indicating if a hierarchical relationship exists
        - relationship_type: "causal", "compositional", "regulatory", or "none"
        - confidence: your confidence in this assessment (0.0 to 1.0)
        - description: brief description of the relationship if it exists
        """
        
        try:
            response = self.llm_client.complete(prompt, system_message)
            # In a real implementation, we would parse the JSON response
            # For now, we'll return a placeholder
            # This would be enhanced in future tasks
            return {
                "has_relationship": False,
                "relationship_type": "none",
                "confidence": 0.0,
                "description": ""
            }
        except Exception as e:
            self.logger.error(f"Error checking relationship: {e}")
            return {
                "has_relationship": False,
                "relationship_type": "none",
                "confidence": 0.0,
                "description": ""
            }
            
    def identify_emergent_behaviors(self, graph: Optional[nx.DiGraph] = None) -> List[Dict]:
        """
        Identify potential emergent behaviors from the hierarchical model.
        
        Args:
            graph: Optional graph to analyze (uses self.hierarchy_graph if None)
            
        Returns:
            List of identified emergent behaviors with metadata
        """
        g = graph if graph is not None else self.hierarchy_graph
        
        if not g or g.number_of_nodes() == 0:
            self.logger.warning("No hierarchy graph available for emergent behavior analysis")
            return []
            
        # Find potential emergent behavior patterns
        emergent_behaviors = []
        
        # Pattern 1: Multiple lower-level nodes connecting to the same higher-level node
        for node in g.nodes():
            # Get node attributes
            attrs = g.nodes[node]
            level = attrs.get("biological_level")
            
            # Skip if not a higher-level node
            if level not in self.BIOLOGICAL_LEVELS[1:]:
                continue
                
            # Get all predecessors (lower-level nodes that connect to this node)
            predecessors = list(g.predecessors(node))
            
            # If multiple lower-level nodes connect to this higher-level node,
            # this might indicate an emergent behavior
            if len(predecessors) >= 2:
                emergent_behaviors.append({
                    "type": "convergent",
                    "higher_node": node,
                    "lower_nodes": predecessors,
                    "biological_level": level,
                    "description": f"Multiple {self.BIOLOGICAL_LEVELS[self.BIOLOGICAL_LEVELS.index(level) - 1]} mechanisms potentially contributing to {level} behavior"
                })
                
        # Pattern 2: Chains of three or more nodes across different levels
        # Find all simple paths of length >= 2
        for source in g.nodes():
            for target in g.nodes():
                if source == target:
                    continue
                    
                # Get source and target levels
                source_level = g.nodes[source].get("biological_level")
                target_level = g.nodes[target].get("biological_level")
                
                # Skip if not a valid level pair
                if (source_level not in self.BIOLOGICAL_LEVELS or 
                    target_level not in self.BIOLOGICAL_LEVELS or
                    self.BIOLOGICAL_LEVELS.index(source_level) >= self.BIOLOGICAL_LEVELS.index(target_level)):
                    continue
                
                # Find all simple paths between source and target
                try:
                    paths = list(nx.all_simple_paths(g, source, target, cutoff=3))
                    for path in paths:
                        if len(path) >= 3:  # At least 3 nodes in the path
                            emergent_behaviors.append({
                                "type": "cascading",
                                "path": path,
                                "source_level": source_level,
                                "target_level": target_level,
                                "description": f"Cascading effect from {source_level} to {target_level} across multiple levels"
                            })
                except nx.NetworkXNoPath:
                    continue
                    
        return emergent_behaviors
