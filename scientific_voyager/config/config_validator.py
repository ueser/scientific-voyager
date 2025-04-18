"""
Configuration Validator Module

This module provides validation functionality for the Scientific Voyager configuration.
It ensures that all required configuration settings are present and valid.
"""

import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, ValidationError, validator, Field

from scientific_voyager.interfaces.dto import ConfigDTO


class DatabaseConfig(BaseModel):
    """Validation model for database configuration."""
    type: str
    path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    
    @validator('type')
    def validate_db_type(cls, v):
        """Validate database type."""
        valid_types = ['sqlite', 'postgresql', 'mysql']
        if v not in valid_types:
            raise ValueError(f"Database type must be one of {valid_types}")
        return v
    
    @validator('path')
    def validate_sqlite_path(cls, v, values):
        """Validate SQLite path is provided when type is sqlite."""
        if values.get('type') == 'sqlite' and not v and v != ':memory:':
            raise ValueError("Path is required for SQLite database")
        return v
    
    @validator('host', 'name', 'user', 'password')
    def validate_postgres_mysql_fields(cls, v, values, field):
        """Validate required fields for PostgreSQL and MySQL."""
        if values.get('type') in ['postgresql', 'mysql'] and not v:
            # Allow environment variable placeholders
            if isinstance(v, str) and v.startswith('${') and v.endswith('}'):
                return v
            raise ValueError(f"{field.name} is required for {values.get('type')} database")
        return v


class LLMConfig(BaseModel):
    """Validation model for LLM configuration."""
    model: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: int = Field(gt=0)
    
    @validator('model')
    def validate_model(cls, v):
        """Validate LLM model."""
        valid_models = ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']
        if v not in valid_models:
            raise ValueError(f"Model must be one of {valid_models}")
        return v


class SearchConfig(BaseModel):
    """Validation model for search configuration."""
    max_results: int = Field(gt=0)
    min_relevance: float = Field(ge=0.0, le=1.0)
    cache_results: Optional[bool] = True
    cache_expiry_hours: Optional[int] = 24


class LoggingConfig(BaseModel):
    """Validation model for logging configuration."""
    level: str
    format: Optional[str] = None
    file: Optional[str] = None
    
    @validator('level')
    def validate_level(cls, v):
        """Validate logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in valid_levels:
            raise ValueError(f"Logging level must be one of {valid_levels}")
        return v


class ConfigValidator:
    """
    Configuration validator that ensures all required configuration
    settings are present and valid.
    """
    
    def __init__(self):
        """Initialize the configuration validator."""
        self._logger = logging.getLogger(__name__)
        self._validation_errors: List[str] = []
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        self._validation_errors = []
        
        # Validate required top-level keys
        required_keys = ['environment', 'database', 'logging']
        for key in required_keys:
            if key not in config:
                self._validation_errors.append(f"Missing required configuration key: {key}")
        
        # If missing required keys, return False
        if self._validation_errors:
            return False
        
        # Validate database configuration
        try:
            DatabaseConfig(**config.get('database', {}))
        except ValidationError as e:
            for error in e.errors():
                self._validation_errors.append(f"Database configuration error: {error['msg']}")
        
        # Validate LLM configuration if present
        if 'llm' in config:
            try:
                LLMConfig(**config.get('llm', {}))
            except ValidationError as e:
                for error in e.errors():
                    self._validation_errors.append(f"LLM configuration error: {error['msg']}")
        
        # Validate search configuration if present
        if 'search' in config:
            try:
                SearchConfig(**config.get('search', {}))
            except ValidationError as e:
                for error in e.errors():
                    self._validation_errors.append(f"Search configuration error: {error['msg']}")
        
        # Validate logging configuration
        try:
            LoggingConfig(**config.get('logging', {}))
        except ValidationError as e:
            for error in e.errors():
                self._validation_errors.append(f"Logging configuration error: {error['msg']}")
        
        # Return True if no validation errors
        return len(self._validation_errors) == 0
    
    def validate_config_dto(self, config_dto: ConfigDTO) -> bool:
        """
        Validate the ConfigDTO object.
        
        Args:
            config_dto: ConfigDTO object to validate
            
        Returns:
            True if ConfigDTO is valid, False otherwise
        """
        self._validation_errors = []
        
        # Validate environment
        valid_environments = ['development', 'testing', 'production']
        if config_dto.environment not in valid_environments:
            self._validation_errors.append(
                f"Invalid environment: {config_dto.environment}. "
                f"Must be one of {valid_environments}"
            )
        
        # Validate LLM settings
        if config_dto.llm_settings:
            try:
                LLMConfig(**config_dto.llm_settings)
            except ValidationError as e:
                for error in e.errors():
                    self._validation_errors.append(f"LLM configuration error: {error['msg']}")
        
        # Validate database settings
        if config_dto.database_settings:
            try:
                DatabaseConfig(**config_dto.database_settings)
            except ValidationError as e:
                for error in e.errors():
                    self._validation_errors.append(f"Database configuration error: {error['msg']}")
        
        # Validate search settings
        if config_dto.search_settings:
            try:
                SearchConfig(**config_dto.search_settings)
            except ValidationError as e:
                for error in e.errors():
                    self._validation_errors.append(f"Search configuration error: {error['msg']}")
        
        # Validate logging level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config_dto.logging_level not in valid_levels:
            self._validation_errors.append(
                f"Invalid logging level: {config_dto.logging_level}. "
                f"Must be one of {valid_levels}"
            )
        
        # Return True if no validation errors
        return len(self._validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """
        Get the list of validation errors.
        
        Returns:
            List of validation error messages
        """
        return self._validation_errors.copy()
