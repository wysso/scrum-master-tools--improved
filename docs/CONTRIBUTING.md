# Contributing to ScrumMaster Tools

Thank you for considering contributing to ScrumMaster Tools! This document provides guidelines for developers who want to contribute to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Code Standards](#code-standards)
- [Architecture Guide](#architecture-guide)
- [Adding New Analysis Tools](#adding-new-analysis-tools)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation Standards](#documentation-standards)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Access to a Jira instance for testing
- Git for version control
- Basic understanding of Jira API and Agile concepts

### Project Structure

```
ScrumMaster Tool/
├── src/scrummaster/           # Main package
│   ├── cli.py                 # CLI interface
│   ├── core/                  # Core components
│   │   ├── base_tool.py       # Abstract base class
│   │   ├── jira_client.py     # API client
│   │   └── exclusions_manager.py  # Filtering system
│   ├── tools/                 # Analysis tools
│   │   ├── sprint_completion.py
│   │   ├── worklog_summary.py
│   │   └── ...
│   └── helpers/               # Utility tools
│       ├── connection_test.py
│       ├── label_updater.py
│       └── ...
├── docs/                      # Documentation
├── config/                    # Configuration templates
├── output/                    # Generated reports
└── tests/                     # Test suite (future)
```

---

## Development Environment Setup

### Method 1: UV (Recommended)

UV provides fast Python package management and is the preferred development environment:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/mrozmk/scrummastertool.git
cd scrummastertool

# Create and activate environment
uv venv
uv sync

# Run in development mode
uv run python smt.py
```

### Method 2: Traditional pip/venv

```bash
# Clone repository
git clone https://github.com/mrozmk/scrummastertool.git
cd scrummastertool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Configuration for Development

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Jira credentials
# Use a test Jira instance if available
JIRA_BASE_URL=https://your-test-jira.com
JIRA_PERSONAL_TOKEN=your_development_token
```

**Important**: Use a dedicated test/development Jira instance when possible to avoid impacting production data.

---

## Code Standards

### Python Style Guide

SMT follows PEP8 with these specific guidelines:

#### Line Length and Formatting
```python
# Maximum 100 characters per line
max_line_length = 100

# Use double quotes for strings
message = "This is the preferred string format"

# Trailing commas in multi-line structures
dependencies = [
    "requests>=2.28.0",
    "pandas>=1.5.0",
    "jira>=3.4.0",  # ← trailing comma
]
```

#### Naming Conventions
```python
# Variables and functions: snake_case
def analyze_sprint_data(sprint_id: int) -> Dict[str, Any]:
    project_key = "EXAMPLE"
    total_issues = 42

# Classes: PascalCase
class SprintAnalysisTool(BaseScrumMasterTool):
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30
API_VERSION = "v2"

# Private methods: _leading_underscore
def _extract_issue_data(self, issue: Dict) -> Dict:
    pass
```

#### Type Hints (Required)
```python
from typing import Dict, List, Optional, Any, Union

def process_issues(
    issues: List[Dict[str, Any]],
    project_key: str,
    include_subtasks: bool = True
) -> Dict[str, Union[int, float]]:
    """Process issues and return analysis metrics."""
    pass

# For complex types, create type aliases
IssueData = Dict[str, Any]
AnalysisResult = Dict[str, Union[int, float, str]]

def analyze_data(issues: List[IssueData]) -> AnalysisResult:
    pass
```

### Docstring Standards (Google Style)

```python
def analyze_sprint_completion(
    self,
    sprint_id: int,
    project_key: str,
    include_subtasks: bool = True
) -> Dict[str, Any]:
    """
    Analyze sprint completion metrics for given sprint.

    Examines all issues in the specified sprint to determine completion
    status, timing, and categorization. Provides insights into sprint
    execution effectiveness.

    Args:
        sprint_id: Jira sprint ID to analyze
        project_key: Project key (e.g., 'PROJ')
        include_subtasks: Whether to include subtasks in analysis

    Returns:
        Dictionary containing completion metrics:
        - total_issues: Total number of issues analyzed
        - completed_during: Issues completed during sprint
        - completed_after: Issues completed after sprint end
        - not_completed: Issues remaining incomplete

    Raises:
        ValueError: If sprint_id or project_key are invalid
        ConnectionError: If unable to connect to Jira

    Example:
        >>> tool = SprintCompletionTool()
        >>> result = tool.analyze_sprint_completion(123, "PROJ")
        >>> print(f"Completion rate: {result['completion_rate']:.1%}")
        Completion rate: 78.3%
    """
```

### Error Handling Patterns

```python
# Use specific exception types
try:
    issues = self.jira_client.get_sprint_issues(sprint_id)
except ConnectionError as e:
    logger.error(f"Failed to connect to Jira: {e}")
    raise
except ValueError as e:
    logger.warning(f"Invalid sprint ID: {e}")
    return None

# Always log before raising
def validate_project_key(self, project_key: str) -> bool:
    if not project_key or not project_key.strip():
        logger.error("Project key cannot be empty")
        raise ValueError("Project key is required")

    return True
```

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

class MyAnalysisTool(BaseScrumMasterTool):
    def run(self):
        logger.info(f"Starting analysis for project {project_key}")
        logger.debug(f"Processing {len(issues)} issues")

        try:
            result = self.process_data(issues)
            logger.info(f"Analysis completed successfully: {len(result)} items")
        except Exception as e:
            logger.exception(f"Analysis failed: {e}")
            raise
```

---

## Architecture Guide

### Understanding the Template Method Pattern

SMT uses the Template Method pattern where `BaseScrumMasterTool` defines the workflow template:

```python
# Template defined in BaseScrumMasterTool
def safe_run(self):
    """Safe tool execution with error handling"""
    try:
        self.run()  # ← This is implemented by subclasses
    except KeyboardInterrupt:
        print("\n❌ Operation interrupted by user")
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error in {self.tool_name}")
        print(f"❌ Unexpected error occurred: {str(e)}")

# Subclasses implement the specific analysis logic
class MyAnalysisTool(BaseScrumMasterTool):
    def run(self):
        # 1. Use inherited methods for common operations
        project_key = self.get_project_key()
        sprint = self.get_sprint_selection(project_key)
        exclusions = self.get_project_exclusions(project_key)

        # 2. Implement specific analysis logic
        results = self.analyze_data(project_key, sprint, exclusions)

        # 3. Use inherited methods for output
        filename = self.generate_output_filename("my_analysis", project_key)
        self.save_results(results, filename)
```

### Core Components Overview

#### 1. BaseScrumMasterTool
**Purpose**: Abstract base class providing common functionality
**Key Methods**:
- `get_project_key()`: Interactive project selection
- `get_sprint_selection()`: Sprint selection with board discovery
- `get_project_exclusions()`: Exclusions management
- `generate_output_filename()`: Consistent file naming
- `safe_run()`: Error handling wrapper

#### 2. JiraClient
**Purpose**: Single point of Jira API integration
**Key Methods**:
- `execute_jql()`: JQL query execution with pagination
- `get_project_sprints()`: Sprint data retrieval
- `update_issue_labels()`: Bulk label updates
- `test_connection()`: Connection validation

#### 3. ExclusionsManager
**Purpose**: Project-specific data filtering
**Key Methods**:
- `get_exclusions_for_project()`: Load exclusions config
- `get_interactive_exclusions()`: Interactive exclusions UI
- `add_temp_exclusion()`: Runtime exclusions

---

## Adding New Analysis Tools

### Step-by-Step Guide

#### 1. Create Tool Class

```python
# src/scrummaster/tools/my_analysis.py
import logging
from typing import Dict, List, Any
from ..core.base_tool import BaseScrumMasterTool

logger = logging.getLogger(__name__)

class MyAnalysisTool(BaseScrumMasterTool):
    """
    Tool for analyzing [specific aspect] of Jira data.

    Provides insights into [what it analyzes] to help Scrum Masters
    [what problems it solves].
    """

    def __init__(self):
        super().__init__("My Analysis Tool")

    def run(self):
        """Main execution method - implements the analysis workflow."""
        # 1. Get project and sprint selection
        project_key = self.get_project_key()
        sprint = self.get_sprint_selection(project_key)
        exclusions = self.get_project_exclusions(project_key)

        logger.info(f"Starting my analysis for {project_key}, sprint {sprint['name']}")

        # 2. Fetch data from Jira
        issues = self._fetch_sprint_issues(project_key, sprint['id'], exclusions)

        if not issues:
            print("⚠️ No issues found for analysis")
            return

        # 3. Perform analysis
        results = self._analyze_issues(issues)

        # 4. Generate reports
        self._generate_reports(results, project_key, sprint['name'])

        # 5. Print summary
        self._print_summary(results, project_key, sprint['name'])

    def _fetch_sprint_issues(self, project_key: str, sprint_id: int, exclusions: Dict) -> List[Dict]:
        """Fetch issues for the sprint with exclusions applied."""
        # Build JQL query
        jql = f"project = {project_key} AND sprint = {sprint_id}"

        # Add exclusions to JQL if needed
        if exclusions.get('issue_types'):
            excluded_types = "','".join(exclusions['issue_types'])
            jql += f" AND issuetype NOT IN ('{excluded_types}')"

        logger.debug(f"Executing JQL: {jql}")

        # Fetch issues
        response = self.jira_client.execute_jql(jql)
        issues = response.get('issues', [])

        logger.info(f"Fetched {len(issues)} issues for analysis")
        return issues

    def _analyze_issues(self, issues: List[Dict]) -> Dict[str, Any]:
        """Perform the core analysis logic."""
        results = {
            'total_issues': len(issues),
            'analysis_metrics': {},
            'detailed_data': [],
        }

        for issue in issues:
            # Extract relevant data
            issue_data = self._extract_issue_data(issue)
            results['detailed_data'].append(issue_data)

            # Update metrics
            self._update_metrics(results['analysis_metrics'], issue_data)

        # Calculate derived metrics
        results['completion_rate'] = self._calculate_completion_rate(results)

        return results

    def _extract_issue_data(self, issue: Dict) -> Dict[str, Any]:
        """Extract relevant data from a Jira issue."""
        fields = issue.get('fields', {})

        return {
            'key': issue['key'],
            'summary': fields.get('summary', ''),
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'assignee': self._get_assignee_name(fields.get('assignee')),
            'story_points': self._get_story_points(fields),
            'category': self._get_category_from_labels_and_components(
                fields.get('labels', []),
                fields.get('components', [])
            ),
            # Add more fields as needed for your analysis
        }

    def _get_story_points(self, fields: Dict) -> Optional[float]:
        """Extract story points from issue fields."""
        # Use configuration to get the correct custom field
        from config.jira_config import JIRA_CONFIG

        story_points_field = JIRA_CONFIG.get('story_points_field', 'customfield_10016')
        story_points = fields.get(story_points_field)

        return float(story_points) if story_points is not None else None

    def _get_assignee_name(self, assignee: Optional[Dict]) -> str:
        """Get assignee display name."""
        if not assignee:
            return "Unassigned"
        return assignee.get('displayName', 'Unknown')

    def _update_metrics(self, metrics: Dict, issue_data: Dict):
        """Update running metrics with new issue data."""
        # Implement your specific metric calculations
        category = issue_data['category']

        if category not in metrics:
            metrics[category] = {
                'count': 0,
                'total_story_points': 0,
            }

        metrics[category]['count'] += 1
        if issue_data['story_points']:
            metrics[category]['total_story_points'] += issue_data['story_points']

    def _calculate_completion_rate(self, results: Dict) -> float:
        """Calculate overall completion rate."""
        # Implement your completion rate calculation
        # This is just an example
        completed = sum(1 for item in results['detailed_data']
                       if item['status'] in ['Done', 'Closed'])
        total = results['total_issues']

        return completed / total if total > 0 else 0.0

    def _generate_reports(self, results: Dict, project_key: str, sprint_name: str):
        """Generate CSV and other reports."""
        import pandas as pd
        from datetime import datetime

        # Create DataFrame from detailed data
        df = pd.DataFrame(results['detailed_data'])

        # Generate filename
        filename = self.generate_output_filename("my_analysis", project_key, sprint_name)
        filepath = self.get_output_path("reports", filename)

        # Save CSV
        df.to_csv(filepath, index=False)
        logger.info(f"Report saved to {filepath}")

        print(f"📁 Report saved: {filepath}")

    def _print_summary(self, results: Dict, project_key: str, sprint_name: str):
        """Print analysis summary to console."""
        print(f"\n📊 MY ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Project: {project_key}")
        print(f"Sprint: {sprint_name}")
        print()

        print("📈 KEY METRICS:")
        print(f"   • Total Issues: {results['total_issues']}")
        print(f"   • Completion Rate: {results['completion_rate']:.1%}")

        print("\n📊 BY CATEGORY:")
        for category, metrics in results['analysis_metrics'].items():
            print(f"   • {category}: {metrics['count']} issues "
                  f"({metrics['total_story_points']} story points)")

        print(f"\n✅ Analysis completed successfully!")


def main():
    """Entry point for standalone execution."""
    tool = MyAnalysisTool()
    tool.safe_run()


if __name__ == "__main__":
    main()
```

#### 2. Register Tool in CLI

Edit `src/scrummaster/cli.py`:

```python
# Add import
from .tools.my_analysis import MyAnalysisTool

class ScrumMasterCLI:
    def __init__(self):
        # Add to tools dictionary
        self.tools = {
            # ... existing tools ...
            "my_analysis": {
                "name": "My Analysis Tool",
                "class": MyAnalysisTool,
                "description": "Analyze [specific aspect] of sprint data"
            },
        }

    def display_menu(self):
        # Tool will appear automatically in menu
        pass
```

#### 3. Add Tool to setup.py (if needed)

```python
# setup.py
entry_points={
    'console_scripts': [
        # ... existing entries ...
        'smt-my-analysis=scrummaster.tools.my_analysis:main',
    ],
},
```

### Testing Your New Tool

```bash
# Test standalone
python src/scrummaster/tools/my_analysis.py

# Test via CLI
python smt.py
# Choose your new tool from the menu

# Test with different projects and sprints
# Verify CSV output format
# Check console output formatting
```

---

## Testing Guidelines

### Current Testing Approach

SMT currently uses manual testing with real Jira data. Future versions will include automated testing.

### Manual Testing Checklist

**For New Analysis Tools:**
- [ ] Test with multiple projects
- [ ] Test with different sprint sizes (small <10 issues, large >50 issues)
- [ ] Test with various exclusion configurations
- [ ] Verify CSV output format and data accuracy
- [ ] Test error conditions (no data, connection failures)
- [ ] Verify console output formatting and user experience

**For Helper Tools:**
- [ ] Test successful operations
- [ ] Test error conditions and edge cases
- [ ] Verify user input validation
- [ ] Check permission requirements

### Future Testing Framework

When implementing automated tests, follow this structure:

```python
# tests/test_my_analysis.py
import unittest
from unittest.mock import Mock, patch
from src.scrummaster.tools.my_analysis import MyAnalysisTool

class TestMyAnalysisTool(unittest.TestCase):
    def setUp(self):
        self.tool = MyAnalysisTool()

    @patch('src.scrummaster.core.jira_client.JiraClient')
    def test_analyze_issues_success(self, mock_jira_client):
        # Mock Jira response
        mock_issues = [
            {
                'key': 'TEST-1',
                'fields': {
                    'summary': 'Test issue',
                    'status': {'name': 'Done'},
                    'assignee': {'displayName': 'John Doe'},
                    'customfield_10016': 5.0,  # Story points
                }
            }
        ]

        # Test analysis logic
        results = self.tool._analyze_issues(mock_issues)

        self.assertEqual(results['total_issues'], 1)
        self.assertEqual(results['completion_rate'], 1.0)

    def test_extract_issue_data(self):
        # Test data extraction logic
        issue = {
            'key': 'TEST-1',
            'fields': {
                'summary': 'Test issue',
                'status': {'name': 'In Progress'},
            }
        }

        result = self.tool._extract_issue_data(issue)

        self.assertEqual(result['key'], 'TEST-1')
        self.assertEqual(result['status'], 'In Progress')
```

---

## Pull Request Process

### Before Submitting

1. **Code Quality Check**
   ```bash
   # Format code (if ruff is configured)
   ruff format .

   # Check linting
   ruff check .

   # Type checking (if mypy is configured)
   mypy src/
   ```

2. **Manual Testing**
   - Test your changes with real Jira data
   - Verify existing functionality still works
   - Test edge cases and error conditions

3. **Documentation Updates**
   - Update docstrings for new/modified functions
   - Add/update examples in documentation
   - Update CHANGELOG.md if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes and why they're needed.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Detailed list of changes
- New files created
- Modified functionality

## Testing
- [ ] Manual testing completed with real Jira data
- [ ] Tested with different project configurations
- [ ] Verified existing functionality still works
- [ ] Tested error conditions

## Documentation
- [ ] Updated docstrings
- [ ] Updated user documentation if needed
- [ ] Updated API documentation if needed

## Screenshots (if applicable)
Include console output or CSV examples for new features.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] My changes generate no new warnings
- [ ] I have added/updated documentation
- [ ] My changes have been tested manually
```

### Review Process

1. **Automated Checks**: Code style, basic syntax validation
2. **Manual Review**: Code quality, architecture adherence, documentation
3. **Testing**: Reviewer tests with their own Jira instance
4. **Approval**: Two approvals required for major changes

---

## Documentation Standards

### Code Documentation

**Required Documentation:**
- All public classes and methods must have Google-style docstrings
- Complex algorithms should have inline comments
- Type hints required for all function signatures

**Example:**
```python
def process_sprint_data(
    self,
    sprint_data: Dict[str, Any],
    exclusions: Dict[str, List[str]]
) -> Tuple[List[Dict], Dict[str, int]]:
    """
    Process raw sprint data applying exclusions and categorization.

    Takes raw sprint data from Jira API and processes it by applying
    configured exclusions, extracting relevant fields, and categorizing
    issues based on components and labels.

    Args:
        sprint_data: Raw sprint data from Jira API containing issues list
        exclusions: Dictionary of exclusion rules by type (issue_types, components, etc.)

    Returns:
        Tuple containing:
        - List of processed issue dictionaries
        - Dictionary of processing statistics

    Raises:
        ValueError: If sprint_data format is invalid
        KeyError: If required fields are missing from sprint_data

    Example:
        >>> exclusions = {'issue_types': ['Epic'], 'components': ['Archive']}
        >>> issues, stats = tool.process_sprint_data(raw_data, exclusions)
        >>> print(f"Processed {len(issues)} issues, excluded {stats['excluded_count']}")
    """
```

### User Documentation

When adding new features:
- Update [USER_GUIDE.md](USER_GUIDE.md) with usage examples
- Add troubleshooting entries to [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Update [TOOLS.md](TOOLS.md) with detailed tool information

### API Documentation

For API changes:
- Update [API.md](API.md) with new endpoints or methods
- Include code examples
- Document any breaking changes

---

## Development Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/my-new-analysis-tool

# Make changes, commit regularly
git add .
git commit -m "feat: add basic structure for new analysis tool"

# Push and create PR
git push origin feature/my-new-analysis-tool
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(tools): add epic analysis tool with burndown metrics

Add comprehensive epic analysis including:
- Epic completion tracking across sprints
- Story breakdown and progress metrics
- Burndown chart data generation

Closes #42

fix(jira-client): handle rate limiting in bulk operations

Added exponential backoff for rate limit responses.
Improved error messages for API failures.

docs(contributing): add testing guidelines for new tools

Updated testing checklist and added examples for
manual testing procedures.
```

### Release Process

SMT uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to API or user interface
- **MINOR**: New features, backward-compatible changes
- **PATCH**: Bug fixes, minor improvements

---

## Getting Help

### Community Resources

- **GitHub Issues**: Report bugs, request features
- **Documentation**: Comprehensive guides in `/docs`
- **Code Examples**: Study existing tools for patterns

### Development Support

For development questions:
- Review existing code in similar tools
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Look at [API.md](API.md) for Jira integration patterns

### Professional Support

For enterprise development or custom tools:
- Contact: marek@mroz.consulting
- Custom development services available
- Training and consultation for large deployments

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain high code quality standards
- Document your contributions thoroughly

### Reporting Issues

For sensitive issues or code of conduct violations:
- Contact maintainer directly: marek@mroz.consulting
- All reports will be handled confidentially

---

Thank you for contributing to ScrumMaster Tools! Your contributions help teams worldwide improve their agile processes through better data analysis.