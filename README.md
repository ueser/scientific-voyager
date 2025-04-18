# Scientific Voyager

A modular platform for scientific knowledge exploration and insight generation across biological levels, powered by large language models.

## Overview

Scientific Voyager is a platform designed to help researchers navigate and connect scientific knowledge across different biological levels (genetic, molecular, cellular, systems, and organism). By leveraging advanced language models, it processes scientific literature, identifies relationships between findings, and generates novel insights that might otherwise remain hidden in the vast sea of scientific publications.

## Features

- **Cross-level Knowledge Integration**: Connect findings across different biological levels
- **Insight Generation**: Identify novel connections and research opportunities
- **Statement Triangulation**: Validate scientific statements through multiple sources
- **Research Task Prioritization**: Generate and prioritize research tasks based on insights
- **Modular Architecture**: Extensible design for adding new data sources and analysis methods

## Requirements

- Python 3.10+
- OpenAI API key (for GPT-4o integration)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scientific-voyager.git
cd scientific-voyager

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/.env.example config/.env
# Edit config/.env with your API keys and settings
```

## Configuration

Scientific Voyager uses a hierarchical configuration system that supports different deployment environments:

### Configuration Structure

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

### Required Configuration
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4o integration

### Optional Configuration
- `VOYAGER_ENV`: Deployment environment (development, testing, production)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEBUG`: Enable debug mode (true/false)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database connection settings for production

See [Configuration Documentation](docs/configuration.md) for detailed information.

## Usage

### Basic Usage

```python
# Import the necessary modules
from scientific_voyager.config.config_manager import get_config
from scientific_voyager.interfaces.llm_interface import ILLM
from scientific_voyager.interfaces.dto import StatementDTO, RelationshipDTO

# Get configuration
config = get_config()

# Initialize components
llm_service = get_llm_service()

# Process scientific statements
statement = StatementDTO(
    text="PTEN loss leads to increased PI3K signaling in cancer cells.",
    source="PMID:12345678"
)

# Generate insights
insights = llm_service.generate_insights([statement])

# Print results
for insight in insights:
    print(f"Insight: {insight.text}")
    print(f"Novelty Score: {insight.novelty_score}")
    print(f"Significance: {insight.significance_score}")
```

### Advanced Usage

See the [examples](examples/) directory for more advanced usage examples, including:

- Cross-level knowledge integration
- Statement triangulation
- Research task generation
- Custom data source integration

## Project Structure

The Scientific Voyager platform follows a modular architecture with clear separation of concerns:

```
scientific-voyager/
├── config/                  # Configuration files
├── docs/                    # Documentation
├── examples/                # Usage examples
├── scientific_voyager/      # Main package
│   ├── config/              # Configuration management
│   ├── interfaces/          # Interface definitions
│   ├── llm/                 # LLM integration
│   ├── data/                # Data handling
│   ├── processing/          # Processing logic
│   └── utils/               # Utility functions
├── tests/                   # Test suite
└── scripts/                 # Utility scripts
```

## Architecture

Scientific Voyager is built on a modular architecture with the following key components:

1. **Interfaces**: Define clear contracts between components
2. **Configuration**: Manage settings across different environments
3. **LLM Integration**: Connect with large language models for analysis
4. **Data Management**: Handle scientific statements and relationships
5. **Processing Pipeline**: Generate insights across biological levels

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4o API access
- The scientific community for their invaluable research
- All contributors to this project