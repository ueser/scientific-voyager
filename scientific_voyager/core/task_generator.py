"""
Task Generator Module

This module implements the Next Task Chain functionality for dynamically generating
subsequent tasks based on the current knowledge state and defined criteria.
Uses OpenAI's GPT-4o model for reasoning and task generation.
"""

from typing import Dict, List, Optional, Tuple

from scientific_voyager.utils.llm_client import LLMClient


class TaskGenerator:
    """
    Generates and manages next tasks for scientific exploration.
    Uses OpenAI's GPT-4o model for reasoning and task generation.
    """

    def __init__(self, knowledge_graph=None, insights_generator=None, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the task generator.
        
        Args:
            knowledge_graph: Reference to the knowledge graph
            insights_generator: Reference to the insights generator
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: Model to use (defaults to gpt-4o)
        """
        self.knowledge_graph = knowledge_graph
        self.insights_generator = insights_generator
        self.tasks = []
        self.llm_client = LLMClient(api_key=api_key, model=model)
        
    def generate_tasks(
        self,
        overarching_goal: str,
        current_knowledge: Dict,
        focus_areas: Optional[List[str]] = None,
        max_tasks: int = 5
    ) -> List[Dict]:
        """
        Generate next tasks based on the current knowledge state and goals using GPT-4o.
        
        Args:
            overarching_goal: The main scientific goal guiding exploration
            current_knowledge: Summary of current knowledge state
            focus_areas: Optional list of focus areas to prioritize
            max_tasks: Maximum number of tasks to generate
            
        Returns:
            List of generated tasks with metadata
        """
        # Generate tasks using the LLM client
        tasks = self.llm_client.generate_tasks(
            current_knowledge=current_knowledge,
            overarching_goal=overarching_goal,
            focus_areas=focus_areas,
            max_tasks=max_tasks
        )
        
        # Add the generated tasks to our task list
        for task in tasks:
            self.add_task(
                task_description=task.get("description", ""),
                reasoning=task.get("reasoning", ""),
                focus_keywords=task.get("focus_keywords", []),
                priority=task.get("priority", 1),
                metadata=task.get("metadata", {})
            )
            
        return tasks
        
    def add_task(
        self,
        task_description: str,
        reasoning: str,
        focus_keywords: List[str],
        priority: int = 1,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a new task to the task list.
        
        Args:
            task_description: Description of the task
            reasoning: Reasoning behind generating this task
            focus_keywords: Key focus keywords for the task
            priority: Task priority (1-5, with 5 being highest)
            metadata: Additional metadata about the task
            
        Returns:
            Unique ID of the added task
        """
        if metadata is None:
            metadata = {}
            
        task_id = f"task_{len(self.tasks) + 1}"
        
        task = {
            "id": task_id,
            "description": task_description,
            "reasoning": reasoning,
            "focus_keywords": focus_keywords,
            "priority": priority,
            "status": "pending",
            "metadata": metadata,
            "timestamp": None  # Will be implemented in a future task
        }
        
        self.tasks.append(task)
        return task_id
        
    def get_pending_tasks(
        self,
        focus_area: Optional[str] = None,
        min_priority: int = 0
    ) -> List[Dict]:
        """
        Get pending tasks based on filtering criteria.
        
        Args:
            focus_area: Optional focus area to filter by
            min_priority: Minimum priority level
            
        Returns:
            List of pending tasks matching the criteria
        """
        # Simple implementation to be enhanced in future tasks
        return [task for task in self.tasks if task["status"] == "pending" 
                and task["priority"] >= min_priority]
