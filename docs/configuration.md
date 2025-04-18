# Configuration Management System

## Overview

The Scientific Voyager platform uses a flexible, hierarchical configuration management system that supports different deployment environments (development, testing, production) with appropriate security measures for sensitive data like API keys.

## Configuration Structure

The configuration system is organized as follows:

```
scientific-voyager/
├── config/
│   ├── config.yaml                 # Base configuration
│   ├── .env                        # Environment variables (not in version control)
│   ├── .env.example                # Template for environment variables
│   └── environments/
│       ├── development.yaml        # Development environment overrides
│       ├── testing.yaml            # Testing environment overrides
│       └── production.yaml         # Production environment overrides
```

## Configuration Hierarchy

The configuration is loaded in the following order, with later sources overriding earlier ones:

1. Base configuration (`config/config.yaml`)
2. Environment-specific configuration (`config/environments/<env>.yaml`)
3. Environment variables (prefixed with `VOYAGER_`)
4. Runtime overrides (via code)

## Usage

### Basic Usage

```python
from scientific_voyager.config.config_manager import get_config

# Get the global configuration instance
config = get_config()

# Access configuration values
db_type = config.get("database.type")
debug_mode = config.get("debug", False)  # With default value

# Get a configuration section
db_config = config.get_section("database")

# Get configuration as DTO
config_dto = config.get_config_dto()
```

### Environment Variables

Environment variables can override configuration values. The format is:

```
VOYAGER_SECTION_KEY=value
```

For example:
- `VOYAGER_ENV=production` sets the environment
- `VOYAGER_DATABASE_HOST=localhost` overrides `database.host`
- `VOYAGER_DEBUG=true` overrides `debug`

### Sensitive Data

Sensitive data such as API keys should be stored in environment variables or the `.env` file, which is not committed to version control. The `.env.example` file provides a template with placeholder values.

Example `.env` file:
```
VOYAGER_ENV=development
OPENAI_API_KEY=your_openai_api_key_here
PUBMED_API_KEY=your_pubmed_api_key_here
```

## Configuration Options

### Base Configuration

The base configuration includes the following sections:

#### General Settings
- `environment`: Deployment environment (`development`, `testing`, `production`)
- `debug`: Debug mode flag

#### Logging
- `logging.level`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `logging.format`: Log message format
- `logging.file`: Log file path

#### Database
- `database.type`: Database type (`sqlite`, `postgresql`, `mysql`)
- `database.path`: SQLite database path
- `database.host`: Database host (PostgreSQL/MySQL)
- `database.port`: Database port (PostgreSQL/MySQL)
- `database.name`: Database name (PostgreSQL/MySQL)
- `database.user`: Database user (PostgreSQL/MySQL)
- `database.password`: Database password (PostgreSQL/MySQL)

#### LLM Settings
- `llm.model`: LLM model name (`gpt-4o`, `gpt-4`, `gpt-3.5-turbo`)
- `llm.temperature`: Temperature parameter (0.0-1.0)
- `llm.max_tokens`: Maximum tokens per request

#### Search Settings
- `search.max_results`: Maximum search results
- `search.min_relevance`: Minimum relevance score (0.0-1.0)
- `search.cache_results`: Whether to cache search results
- `search.cache_expiry_hours`: Cache expiry time in hours

#### Execution Settings
- `execution.max_concurrent_tasks`: Maximum concurrent tasks
- `execution.task_timeout_seconds`: Task timeout in seconds
- `execution.retry_attempts`: Number of retry attempts

### Environment-Specific Overrides

Each environment can override any of the base configuration options. The environment-specific configuration files are located in `config/environments/<env>.yaml`.

## Configuration Validation

The configuration is validated using Pydantic models to ensure that all required configuration settings are present and valid. If validation fails, appropriate error messages are provided.

## Adding New Configuration Options

To add new configuration options:

1. Add the option to the appropriate configuration file(s)
2. Update the `ConfigDTO` class in `scientific_voyager/interfaces/dto.py` if needed
3. Update the validation models in `scientific_voyager/config/config_validator.py` if needed
4. Document the new option in this file

## Best Practices

1. **Environment Separation**: Use environment-specific configuration files for settings that vary between environments.
2. **Sensitive Data**: Never commit sensitive data like API keys to version control.
3. **Validation**: Always validate configuration at startup to catch issues early.
4. **Defaults**: Provide sensible defaults for optional configuration settings.
5. **Documentation**: Keep this documentation up-to-date when adding or changing configuration options.
