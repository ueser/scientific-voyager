"""
Configuration System Usage Example

This example demonstrates how to use the Scientific Voyager configuration system.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scientific_voyager.config.config_manager import get_config
from scientific_voyager.config.config_validator import ConfigValidator


def main():
    """Demonstrate configuration system usage."""
    print("Scientific Voyager Configuration Example")
    print("=" * 50)
    
    # Get the global configuration instance
    config = get_config()
    print(f"Current environment: {config.get('environment')}")
    print(f"Debug mode: {config.get('debug')}")
    
    # Access nested configuration with dot notation
    print("\nDatabase Configuration:")
    print(f"  Type: {config.get('database.type')}")
    if config.get('database.type') == 'sqlite':
        print(f"  Path: {config.get('database.path')}")
    else:
        print(f"  Host: {config.get('database.host')}")
        print(f"  Port: {config.get('database.port')}")
        print(f"  Name: {config.get('database.name')}")
    
    # Get a configuration section
    print("\nLLM Configuration:")
    llm_config = config.get_section('llm') if 'llm' in config._config else {}
    for key, value in llm_config.items():
        print(f"  {key}: {value}")
    
    # Get configuration as DTO
    print("\nConfiguration DTO:")
    config_dto = config.get_config_dto()
    print(f"  Environment: {config_dto.environment}")
    print(f"  Debug: {config_dto.debug}")
    print(f"  Logging Level: {config_dto.logging_level}")
    print(f"  Max Concurrent Tasks: {config_dto.max_concurrent_tasks}")
    
    # Print API keys (in a real application, never print API keys)
    print("\nAPI Keys (masked):")
    for key, value in config_dto.api_keys.items():
        # Mask API keys for security
        masked_value = value[:4] + "..." + value[-4:] if value and len(value) > 8 else "Not set"
        print(f"  {key}: {masked_value}")
    
    # Validate configuration
    print("\nValidating Configuration:")
    validator = ConfigValidator()
    is_valid = validator.validate_config(config._config)
    if is_valid:
        print("  Configuration is valid.")
    else:
        print("  Configuration validation failed:")
        for error in validator.get_validation_errors():
            print(f"  - {error}")
    
    # Demonstrate setting a configuration value
    print("\nSetting a configuration value:")
    original_value = config.get("search.max_results", 50)
    print(f"  Original value: search.max_results = {original_value}")
    
    config.set("search.max_results", 75)
    new_value = config.get("search.max_results")
    print(f"  New value: search.max_results = {new_value}")
    
    # Demonstrate environment variable override
    print("\nEnvironment Variable Override Example:")
    print("  Setting VOYAGER_DEBUG=true as an environment variable")
    os.environ["VOYAGER_DEBUG"] = "true"
    
    # Reload configuration to apply environment variable
    config.load_config()
    print(f"  Debug mode after override: {config.get('debug')}")
    
    # Clean up environment variable
    del os.environ["VOYAGER_DEBUG"]


if __name__ == "__main__":
    main()
