"""
Configuration Interface Module

This module defines the abstract interface for configuration management
in the Scientific Voyager platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class IConfig(ABC):
    """
    Interface for configuration management.
    Defines the contract for managing configuration settings.
    """

    @abstractmethod
    def load_config(self, config_path: str) -> Dict:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing configuration settings
            
        Raises:
            FileNotFoundError: If config file does not exist
            ValueError: If config file is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def save_config(self, config_path: str) -> bool:
        """
        Save current configuration to a file.
        
        Args:
            config_path: Path to save the configuration file
            
        Returns:
            True if save was successful, False otherwise
            
        Raises:
            ValueError: If config_path is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default if key is not found
        """
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            ValueError: If key is invalid
            Exception: For other unexpected errors
        """
        pass
        
    @abstractmethod
    def get_section(self, section: str) -> Dict:
        """
        Get a configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary containing section configuration
            
        Raises:
            KeyError: If section does not exist
            Exception: For other unexpected errors
        """
        pass
