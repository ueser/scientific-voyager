"""
Configuration Manager Module

This module implements the configuration management system for Scientific Voyager.
It provides functionality to load, validate, and access configuration settings from
various sources including YAML files, environment variables, and .env files.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from scientific_voyager.interfaces.config_interface import IConfig
from scientific_voyager.interfaces.dto import ConfigDTO


class ConfigManager(IConfig):
    """
    Configuration manager implementation that handles loading and accessing
    configuration settings from multiple sources with environment-specific overrides.
    """
    
    def __init__(self, config_dir: str = None, env_file: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files (default: project_root/config)
            env_file: Path to .env file (default: project_root/config/.env)
        """
        self._config: Dict[str, Any] = {}
        self._config_dto: Optional[ConfigDTO] = None
        
        # Set default config directory if not provided
        if config_dir is None:
            # Determine project root (assuming this file is in project_root/scientific_voyager/config)
            project_root = Path(__file__).parent.parent.parent
            config_dir = os.path.join(project_root, "config")
        
        self._config_dir = config_dir
        
        # Set default .env file path if not provided
        if env_file is None:
            env_file = os.path.join(config_dir, ".env")
        
        # Load environment variables from .env file if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Determine environment from environment variable or default to development
        self._environment = os.environ.get("VOYAGER_ENV", "development")
        
        # Initialize logger
        self._logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: str = None) -> Dict:
        """
        Load configuration from files and environment variables.
        
        Args:
            config_path: Optional path to a specific config file to load
                         If not provided, loads from default locations
            
        Returns:
            Dictionary containing merged configuration settings
            
        Raises:
            FileNotFoundError: If config file does not exist
            ValueError: If config file is invalid
            Exception: For other unexpected errors
        """
        try:
            # If specific config path is provided, load only that file
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self._config = yaml.safe_load(file) or {}
                self._logger.info(f"Loaded configuration from {config_path}")
                return self._config
            
            # Otherwise, load configuration in layers
            
            # 1. Load base configuration
            base_config_path = os.path.join(self._config_dir, "config.yaml")
            if os.path.exists(base_config_path):
                with open(base_config_path, 'r') as file:
                    self._config = yaml.safe_load(file) or {}
                self._logger.info(f"Loaded base configuration from {base_config_path}")
            else:
                self._logger.warning(f"Base configuration file not found at {base_config_path}")
                self._config = {}
            
            # 2. Load environment-specific configuration
            env_config_path = os.path.join(self._config_dir, "environments", f"{self._environment}.yaml")
            if os.path.exists(env_config_path):
                with open(env_config_path, 'r') as file:
                    env_config = yaml.safe_load(file) or {}
                
                # Merge environment config with base config (environment overrides base)
                self._deep_merge(self._config, env_config)
                self._logger.info(f"Loaded environment configuration from {env_config_path}")
            else:
                self._logger.warning(f"Environment configuration file not found at {env_config_path}")
            
            # 3. Override with environment variables
            self._override_from_env_vars()
            
            # 4. Create ConfigDTO from loaded configuration
            self._create_config_dto()
            
            return self._config
            
        except FileNotFoundError as e:
            self._logger.error(f"Configuration file not found: {e}")
            raise
        except yaml.YAMLError as e:
            self._logger.error(f"Invalid YAML in configuration file: {e}")
            raise ValueError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            self._logger.error(f"Error loading configuration: {e}")
            raise
    
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
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write configuration to file
            with open(config_path, 'w') as file:
                yaml.dump(self._config, file, default_flow_style=False)
            
            self._logger.info(f"Saved configuration to {config_path}")
            return True
        
        except Exception as e:
            self._logger.error(f"Error saving configuration to {config_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key (dot notation supported for nested keys)
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default if key is not found
        """
        # Handle nested keys with dot notation (e.g., "database.host")
        if "." in key:
            parts = key.split(".")
            current = self._config
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            
            return current
        
        # Handle top-level keys
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation supported for nested keys)
            value: Configuration value
            
        Raises:
            ValueError: If key is invalid
            Exception: For other unexpected errors
        """
        # Handle nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            current = self._config
            
            # Navigate to the nested dictionary
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    raise ValueError(f"Cannot set nested key '{key}' because '{part}' is not a dictionary")
                
                current = current[part]
            
            # Set the value in the nested dictionary
            current[parts[-1]] = value
        else:
            # Set top-level key
            self._config[key] = value
        
        # Update ConfigDTO
        self._create_config_dto()
    
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
        if section in self._config and isinstance(self._config[section], dict):
            return self._config[section].copy()
        
        raise KeyError(f"Configuration section '{section}' not found")
    
    def get_config_dto(self) -> ConfigDTO:
        """
        Get the configuration as a ConfigDTO object.
        
        Returns:
            ConfigDTO object representing the current configuration
        """
        if self._config_dto is None:
            self._create_config_dto()
        
        return self._config_dto
    
    def _create_config_dto(self) -> None:
        """
        Create a ConfigDTO object from the current configuration.
        """
        # Extract relevant configuration sections for the DTO
        environment = self.get("environment", "development")
        debug = self.get("debug", False)
        
        # Extract API keys
        api_keys = {}
        if "OPENAI_API_KEY" in os.environ:
            api_keys["openai"] = os.environ["OPENAI_API_KEY"]
        if "PUBMED_API_KEY" in os.environ:
            api_keys["pubmed"] = os.environ["PUBMED_API_KEY"]
        if "SEMANTIC_SCHOLAR_API_KEY" in os.environ:
            api_keys["semantic_scholar"] = os.environ["SEMANTIC_SCHOLAR_API_KEY"]
        
        # Extract LLM settings
        llm_settings = self.get("llm", {})
        
        # Extract database settings
        database_settings = self.get("database", {})
        
        # Extract search settings
        search_settings = self.get("search", {})
        
        # Extract logging level
        logging_level = self.get("logging", {}).get("level", "INFO")
        
        # Extract max concurrent tasks
        max_concurrent_tasks = self.get("execution", {}).get("max_concurrent_tasks", 5)
        
        # Create ConfigDTO
        self._config_dto = ConfigDTO(
            environment=environment,
            debug=debug,
            api_keys=api_keys,
            llm_settings=llm_settings,
            database_settings=database_settings,
            search_settings=search_settings,
            logging_level=logging_level,
            max_concurrent_tasks=max_concurrent_tasks
        )
    
    def _override_from_env_vars(self) -> None:
        """
        Override configuration values with environment variables.
        
        Environment variables are expected to be in the format:
        VOYAGER_SECTION_KEY=value
        
        For example, VOYAGER_DATABASE_HOST=localhost would override config["database"]["host"]
        """
        prefix = "VOYAGER_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split into parts
                config_key = key[len(prefix):].lower()
                parts = config_key.split("_")
                
                if len(parts) >= 2:
                    # Convert to nested dictionary keys
                    section = parts[0]
                    subkey = "_".join(parts[1:])
                    
                    # Ensure section exists
                    if section not in self._config:
                        self._config[section] = {}
                    
                    # Set value in configuration
                    self._config[section][subkey] = self._convert_env_value(value)
                else:
                    # Set top-level key
                    self._config[config_key] = self._convert_env_value(value)
    
    def _convert_env_value(self, value: str) -> Any:
        """
        Convert environment variable string value to appropriate type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value (bool, int, float, or string)
        """
        # Convert boolean values
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
        
        # Convert numeric values
        try:
            # Try converting to int
            return int(value)
        except ValueError:
            try:
                # Try converting to float
                return float(value)
            except ValueError:
                # Keep as string
                return value
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """
        Deep merge two dictionaries, modifying base in-place.
        
        Args:
            base: Base dictionary to merge into
            override: Dictionary with values to override base
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._deep_merge(base[key], value)
            else:
                # Override or add value
                base[key] = value


# Create a singleton instance for global access
_config_instance = None

def get_config() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigManager()
        # Load configuration immediately
        _config_instance.load_config()
    
    return _config_instance
