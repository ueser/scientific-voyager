# Contributing to Scientific Voyager

Thank you for your interest in contributing to the Scientific Voyager project! This document outlines the coding standards, documentation guidelines, and development workflow for the project.

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd scientific-voyager
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Code Style and Standards

Scientific Voyager follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide with some modifications. We use the following tools to enforce code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **Flake8**: For code linting
- **mypy**: For static type checking

The configuration for these tools is defined in `pyproject.toml` and `setup.cfg`.

### General Guidelines

1. All code should be formatted with Black and isort
2. All functions and classes should have type annotations
3. Maximum line length is 88 characters
4. Use double quotes for strings, except when single quotes avoid backslashes
5. Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings

## Documentation Guidelines

### Docstrings

All modules, classes, and functions should have docstrings following the Google style:

```python
def function_with_types_in_docstring(param1: int, param2: str) -> bool:
    """Example function with types documented in the docstring.
    
    Args:
        param1: The first parameter.
        param2: The second parameter.
        
    Returns:
        True if successful, False otherwise.
        
    Raises:
        ValueError: If param1 is negative.
    """
    if param1 < 0:
        raise ValueError("param1 must be positive")
    return param1 < len(param2)
```

### Comments

- Use comments sparingly and only when necessary to explain complex logic
- Keep comments up-to-date with code changes
- Write comments as complete sentences with proper capitalization and punctuation

## Testing

- All code should have corresponding unit tests
- Tests should be placed in the `tests` directory
- Use pytest for writing and running tests
- Aim for high test coverage, especially for core functionality

## Pull Request Process

1. Create a new branch for your feature or bugfix
2. Write tests for your changes
3. Ensure all tests pass and code quality checks succeed
4. Update documentation if necessary
5. Submit a pull request with a clear description of the changes

## Using OpenAI GPT Models

When implementing NLP tasks, reasoning, classification, or decision-making features:

1. Use the `LLMClient` utility class from `scientific_voyager.utils.llm_client`
2. Prefer `gpt-4o` for high-quality results or `gpt-4o-mini` for faster, more cost-effective processing
3. Always handle API errors gracefully and provide fallback mechanisms
4. Cache results when appropriate to minimize API calls
5. Use clear, specific prompts with proper system messages for best results

## Project Structure

The project follows this structure:

```
scientific_voyager/
├── scientific_voyager/        # Main package
│   ├── core/                  # Core functionality
│   ├── data/                  # Data handling
│   ├── models/                # ML models
│   ├── utils/                 # Utilities
│   └── visualization/         # Visualization tools
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                      # Documentation
├── pyproject.toml             # Project configuration
├── setup.cfg                  # Additional configuration
└── .pre-commit-config.yaml    # Pre-commit hooks
```

## License

By contributing to Scientific Voyager, you agree that your contributions will be licensed under the project's license.
