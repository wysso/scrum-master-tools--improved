# ScrumMaster Tools - Architecture Documentation

## Overview

ScrumMaster Tools (SMT) is a Python application following a modular, layered architecture designed for analyzing Jira data to support Scrum Masters and development teams. The architecture emphasizes separation of concerns, extensibility, and maintainability.

## Core Principles

- **Single Responsibility**: Each component has a clear, focused purpose
- **Dependency Inversion**: High-level modules depend on abstractions, not concrete implementations
- **Open/Closed**: Open for extension through inheritance, closed for modification
- **Template Method Pattern**: Common workflows defined in base classes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                            │
│                    (src/cli.py)                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Analysis Tools                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   Sprint    │ │   Worklog   │ │   Anomaly   │ │    ...    │ │
│  │ Completion  │ │   Summary   │ │  Detector   │ │           │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                 BaseScrumMasterTool                            │
│              (Abstract Base Class)                             │
│  • Project key validation                                       │
│  • Sprint selection logic                                       │
│  • Output directory management                                  │
│  • Exclusions management integration                            │
│  • Common UI patterns                                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Core Components                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐ │
│  │ JiraClient  │ │ Exclusions  │ │      Helper Tools           │ │
│  │             │ │  Manager    │ │ • Connection Test           │ │
│  │ • API calls │ │             │ │ • Projects Lister          │ │
│  │ • Auth      │ │ • Filter    │ │ • Label Updater            │ │
│  │ • Queries   │ │   logic     │ │ • Components Updater       │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                   External Dependencies                         │
│              Jira REST API • Pandas • Matplotlib               │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. BaseScrumMasterTool (Abstract Base Class)

**Location**: `src/scrummaster/core/base_tool.py`

**Purpose**: Provides common functionality and workflow template for all analysis tools.

**Key Responsibilities**:
- **Project Management**: Project key validation and selection
- **Sprint Selection**: Interactive sprint selection with multi-sprint support
- **Exclusions Integration**: Seamless integration with ExclusionsManager
- **Output Management**: Standardized report generation and file handling
- **UI Patterns**: Common CLI interaction patterns
- **Error Handling**: Consistent error handling across tools

**Key Methods**:
```python
# Template method - implemented by subclasses
def run(self) -> None

# Common workflow methods
def get_project_key(self) -> str
def get_sprint_selection(self) -> list
def get_project_exclusions(self) -> dict
def generate_output_filename(self) -> str
```

**Design Pattern**: Template Method Pattern - defines the skeleton of the algorithm while letting subclasses override specific steps.

### 2. JiraClient

**Location**: `src/scrummaster/core/jira_client.py`

**Purpose**: Handles all interactions with Jira REST API.

**Key Responsibilities**:
- **Authentication**: Bearer token (PAT) authentication
- **API Communication**: HTTP requests to Jira endpoints
- **Data Retrieval**: Issues, sprints, projects, worklogs, custom fields
- **Data Modification**: Update labels, components, responsible fields
- **Query Execution**: JQL query execution with pagination
- **Connection Management**: Connection testing and validation

**Key Features**:
- **Pagination Support**: Automatic handling of large result sets
- **Error Handling**: Robust error handling for API failures
- **Flexible Querying**: Support for complex JQL queries
- **Component Management**: Bulk component updates (v2.5.0+)

### 3. ExclusionsManager

**Location**: `src/scrummaster/core/exclusions_manager.py`

**Purpose**: Manages project-specific exclusions for filtering analysis data.

**Key Responsibilities**:
- **Configuration Management**: Load/save exclusions from JSON files
- **Interactive Configuration**: CLI interface for managing exclusions
- **Filtering Logic**: Apply exclusions across different analysis tools
- **Temporary Exclusions**: Runtime exclusions that don't persist

**Architecture Features**:
- **Project-Specific Config**: Each project can have its own exclusion rules
- **Multi-Level Filtering**: Issue types, specific issues, components, labels
- **Template System**: Default exclusion templates for common scenarios

## Tool Architecture

### Analysis Tools Structure

All analysis tools inherit from `BaseScrumMasterTool` and follow this pattern:

```python
class AnalysisTool(BaseScrumMasterTool):
    def __init__(self):
        super().__init__()
        self.tool_name = "Analysis Tool Name"

    def run(self):
        # 1. Get project and sprint selection (inherited)
        # 2. Get and apply exclusions (inherited)
        # 3. Fetch data from Jira
        # 4. Process and analyze data
        # 5. Generate reports (inherited output management)
```

**Key Analysis Tools**:

1. **SprintCompletionTool** - Sprint completion analysis
2. **WorklogSummaryTool** - Work logging and focus rate analysis
3. **AnomalyDetectorTool** - Statistical anomaly detection
4. **PlanningTool** - Sprint planning quality analysis
5. **IssueTypeSummaryTool** - Issue type distribution analysis
6. **DevsPerformanceTool** - Developer performance metrics

### Helper Tools

**Location**: `src/scrummaster/helpers/`

**Purpose**: Utility tools for setup, maintenance, and data management.

**Key Tools**:
- **ConnectionTest** - Validate Jira connectivity
- **ProjectsLister** - Browse available projects
- **LabelUpdater** - Bulk label management
- **ComponentsUpdater** - JQL-based component updates (v2.6.0)
- **CustomFieldsIdentifier** - Discover custom field mappings

## Data Flow Architecture

### Analysis Workflow

```
User Input → Project Selection → Exclusions → Sprint Selection
     ↓
Data Fetching (JiraClient) → Data Processing → Exclusions Filter
     ↓
Analysis Logic → Report Generation → Output Files
     ↓
CSV Export → Console Summary → File Storage
```

### Configuration Flow

```
Environment Variables (.env) → JiraClient Configuration
     ↓
Project Selection → ExclusionsManager → Tool Configuration
     ↓
Runtime Parameters → Analysis Execution
```

## Design Patterns

### 1. Template Method Pattern
- **Implementation**: BaseScrumMasterTool defines workflow template
- **Customization**: Subclasses implement specific analysis logic
- **Benefits**: Consistent workflow, code reuse, maintainability

### 2. Strategy Pattern
- **Implementation**: ExclusionsManager uses different filtering strategies
- **Flexibility**: Runtime selection of exclusion criteria
- **Extensibility**: Easy to add new exclusion types

### 3. Factory Pattern
- **Implementation**: Tool selection and instantiation in CLI
- **Benefits**: Dynamic tool creation, loose coupling

### 4. Singleton Pattern
- **Implementation**: Configuration management (implicit)
- **Usage**: Shared configuration across components

## Extension Points

### Adding New Analysis Tools

1. **Inherit from BaseScrumMasterTool**
2. **Implement the `run()` method**
3. **Use inherited methods for common operations**
4. **Register in CLI tool selection**

```python
class NewAnalysisTool(BaseScrumMasterTool):
    def __init__(self):
        super().__init__()
        self.tool_name = "New Analysis"

    def run(self):
        project_key = self.get_project_key()
        sprints = self.get_sprint_selection()
        exclusions = self.get_project_exclusions()

        # Custom analysis logic here
        results = self.analyze_data(project_key, sprints, exclusions)

        # Use inherited output methods
        filename = self.generate_output_filename("new_analysis")
        self.save_results(results, filename)
```

### Adding New Helper Tools

1. **Create standalone class or functions**
2. **Follow CLI interaction patterns**
3. **Use JiraClient for API operations**
4. **Register in CLI helper tools menu**

## Security Architecture

### Authentication
- **Personal Access Token (PAT)** based authentication
- **Environment variables** for secure token storage
- **No credential persistence** in code or logs

### Data Security
- **Input validation** for all user inputs
- **Output sanitization** for file names and paths
- **Secure API communication** (HTTPS only)

### Configuration Security
- **Sensitive data in .env files** (gitignored)
- **Template-based configuration** for safe distribution
- **No secrets in repository**

## Performance Considerations

### API Optimization
- **Pagination** for large result sets
- **Batch operations** for bulk updates
- **Connection pooling** (implicit via requests library)
- **Query optimization** for complex JQL

### Memory Management
- **Streaming data processing** for large datasets
- **Pandas optimization** for data analysis
- **Garbage collection** considerations for long-running operations

### Caching Strategy
- **Session-based caching** for repeated queries
- **Project metadata caching** to avoid redundant API calls
- **Configuration caching** for performance

## Error Handling Architecture

### Layered Error Handling

1. **API Level**: HTTP errors, authentication failures
2. **Data Level**: Invalid data formats, missing fields
3. **Business Level**: Invalid project keys, sprint not found
4. **UI Level**: User input validation, friendly error messages

### Error Recovery

- **Graceful degradation** when optional data is missing
- **Retry mechanisms** for transient API failures
- **User guidance** for configuration issues
- **Detailed logging** for debugging

## Future Architecture Considerations

### Scalability
- **Async/await patterns** for concurrent API calls
- **Database backend** for large-scale data caching
- **Microservices architecture** for enterprise deployment

### Extensibility
- **Plugin architecture** for third-party tools
- **API abstraction** for supporting other issue trackers
- **Configuration API** for external configuration management

### Monitoring
- **Metrics collection** for tool usage analytics
- **Performance monitoring** for API response times
- **Error tracking** for proactive issue resolution

---

This architecture provides a solid foundation for maintainable, extensible Jira analysis tools while ensuring consistency across all components and enabling easy addition of new functionality.