# Scientific Voyager Interface Definitions

This document provides an overview of the interface definitions for the Scientific Voyager platform. These interfaces establish the contracts between different components of the system, ensuring maintainability, testability, and scalability.

## Interface Hierarchy

The Scientific Voyager platform is organized into the following interface categories:

1. **Execution Interface**: Coordinates the overall execution of the platform
2. **LLM Interface**: Defines interactions with large language models
3. **Data Interfaces**: Define data management and storage operations
4. **Knowledge Interfaces**: Define knowledge graph and hierarchical model operations
5. **Processing Interfaces**: Define data processing and statement extraction operations
6. **Analysis Interfaces**: Define insight generation and triangulation operations
7. **Task Interface**: Defines task generation and management operations
8. **Visualization Interface**: Defines graph visualization operations
9. **Configuration Interface**: Defines configuration management operations

## Component Relationships

The following diagram illustrates the relationships between the main components:

```
                         +----------------+
                         | IExecutionEngine |
                         +----------------+
                                 |
                +----------------+----------------+
                |                |                |
    +-----------v------+  +------v-------+  +----v-----------+
    |    ILLMClient    |  | IDataManager |  | IKnowledgeGraph |
    +-----------------+  +--------------+  +----------------+
                |                |                |
    +-----------v------+  +------v-------+  +----v-----------+
    | IStatementExtractor |  | IDataSource |  | IHierarchicalModel |
    +-----------------+  +--------------+  +----------------+
                |                |                |
    +-----------v------+  +------v-------+  +----v-----------+
    | IProcessingPipeline |  | IDatabaseManager |  | ITriangulationEngine |
    +-----------------+  +--------------+  +----------------+
                |                                |
    +-----------v------+                  +----v-----------+
    | IInsightsGenerator |                  | IEmergentInsightsManager |
    +-----------------+                  +----------------+
                |                                |
    +-----------v------+                  +----v-----------+
    |   ITaskGenerator  |                  | IGraphVisualizer |
    +-----------------+                  +----------------+
```

## Data Transfer Objects (DTOs)

The platform uses the following DTOs for communication between components:

- **StatementDTO**: Represents a scientific statement
- **RelationshipDTO**: Represents a relationship between statements
- **InsightDTO**: Represents a scientific insight
- **EmergentInsightDTO**: Represents an emergent insight across biological levels
- **TaskDTO**: Represents a research task
- **TriangulationResultDTO**: Represents a triangulation result
- **ExplorationStateDTO**: Represents the state of an exploration
- **SearchResultDTO**: Represents a search result

## Implementation Guidelines

When implementing these interfaces, follow these guidelines:

1. **Error Handling**: Implement robust error handling as specified in the interface contracts
2. **Type Safety**: Ensure all implementations respect the type hints provided in the interfaces
3. **Documentation**: Maintain comprehensive docstrings for all implemented methods
4. **Testing**: Create unit tests for each interface implementation
5. **Dependency Injection**: Use dependency injection to provide dependencies to implementations

## Example Usage

Here's an example of how to implement and use these interfaces:

```python
from scientific_voyager.interfaces.llm_interface import ILLMClient
from scientific_voyager.interfaces.dto import StatementDTO, StatementType, BiologicalLevel

class OpenAIClient(ILLMClient):
    """Implementation of ILLMClient using OpenAI's API."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        # Initialize OpenAI client
        
    def complete(self, prompt: str, system_message: Optional[str] = None, 
                 temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        # Implementation using OpenAI's API
        pass
        
    def extract_statements(self, text: str) -> List[Dict]:
        # Implementation using OpenAI's API
        pass
        
    def categorize_statement(self, statement: str) -> Dict:
        # Implementation using OpenAI's API
        pass
        
    def generate_insights(self, statements: List[Dict], overarching_goal: str,
                          focus_area: Optional[str] = None) -> List[Dict]:
        # Implementation using OpenAI's API
        pass
```

## Sequence Diagrams

### Statement Extraction and Analysis Flow

```
User -> ExecutionEngine: start_exploration(query)
ExecutionEngine -> DataSource: search(query)
DataSource -> ExecutionEngine: search_results
ExecutionEngine -> StatementExtractor: extract_statements(text)
StatementExtractor -> LLMClient: complete(prompt)
LLMClient -> StatementExtractor: extracted_statements
StatementExtractor -> ExecutionEngine: statements
ExecutionEngine -> HierarchicalModel: classify_statement(statement)
HierarchicalModel -> LLMClient: categorize_statement(statement)
LLMClient -> HierarchicalModel: categorization
HierarchicalModel -> ExecutionEngine: classified_statements
ExecutionEngine -> KnowledgeGraph: add_statement(statement)
KnowledgeGraph -> ExecutionEngine: success
```

### Insight Generation Flow

```
ExecutionEngine -> InsightsGenerator: generate_insights(statements)
InsightsGenerator -> LLMClient: generate_insights(statements)
LLMClient -> InsightsGenerator: insights
InsightsGenerator -> ExecutionEngine: insights
ExecutionEngine -> TriangulationEngine: triangulate(statements)
TriangulationEngine -> ExecutionEngine: triangulation_results
ExecutionEngine -> EmergentInsightsManager: identify_emergent_insights(insights)
EmergentInsightsManager -> ExecutionEngine: emergent_insights
ExecutionEngine -> TaskGenerator: generate_tasks(insights)
TaskGenerator -> ExecutionEngine: tasks
```
