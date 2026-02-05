# ScrumMaster Tools - API Documentation

## Table of Contents

- [Overview](#overview)
- [JiraClient Architecture](#jiraclient-architecture)
- [Authentication](#authentication)
- [API Endpoints Used](#api-endpoints-used)
- [Rate Limiting](#rate-limiting)
- [Custom Fields Integration](#custom-fields-integration)
- [Extending API Functionality](#extending-api-functionality)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)

---

## Overview

ScrumMaster Tools integrates with Jira via the official Jira REST API v2. This document covers the technical aspects of this integration, including endpoints used, authentication methods, and extension points for developers.

### API Integration Strategy

**Core Principles:**
- **Read-Only First**: SMT primarily reads data, with selective write operations for helpers
- **Efficient Batching**: Minimize API calls through intelligent caching and batching
- **Graceful Degradation**: Handle API failures gracefully without crashing
- **Rate Limit Respect**: Automatic handling of Jira's rate limiting

**Integration Architecture:**
```
SMT Analysis Tools
        ↓
 BaseScrumMasterTool
        ↓
    JiraClient
        ↓
   Jira REST API v2
        ↓
    Jira Instance
```

---

## JiraClient Architecture

### Class Overview

The `JiraClient` class (`src/scrummaster/core/jira_client.py`) serves as the single point of integration with Jira's REST API.

```python
class JiraClient:
    """
    Client for communication with Jira REST API.

    Handles authentication, HTTP requests, and data retrieval from Jira instance.
    Provides methods for project management, sprint operations, issue querying,
    and bulk data modifications.
    """

    def __init__(self):
        self.base_url = JIRA_CONFIG['base_url']
        self.headers = {
            'Authorization': f'Bearer {JIRA_CONFIG["personal_token"]}',
            'Content-Type': 'application/json'
        }
```

### Core Capabilities

#### 1. Connection Management
- **Connection Testing**: Validates API connectivity and authentication
- **SSL Verification**: Configurable SSL certificate validation
- **Timeout Handling**: Configurable request timeouts
- **Error Recovery**: Automatic retry for transient failures

#### 2. Data Retrieval
- **Project Discovery**: List accessible projects and their metadata
- **Board Management**: Access to Agile boards and their configuration
- **Sprint Operations**: Sprint data retrieval and analysis
- **Issue Querying**: JQL-based issue search with pagination
- **Worklog Access**: Time tracking data retrieval

#### 3. Data Modification
- **Label Updates**: Bulk label management for issues
- **Component Updates**: JQL-based component assignment
- **Field Updates**: Custom field value modifications
- **Issue Creation**: Create issues programmatically (helper tools)

---

## Authentication

### Personal Access Token (PAT) Authentication

SMT uses Jira Personal Access Tokens for authentication, providing several advantages:

**Benefits:**
- ✅ **Secure**: Token-based, no password storage
- ✅ **Revocable**: Can be revoked without changing passwords
- ✅ **Scoped**: Limited to specific permissions
- ✅ **Auditable**: API calls are logged under user context

**Implementation:**
```python
headers = {
    'Authorization': f'Bearer {personal_access_token}',
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers, timeout=30)
```

### Token Configuration

**In .env file:**
```bash
JIRA_PERSONAL_TOKEN=your_token_here_without_quotes
```

**Required Token Permissions:**
- Browse Projects
- View Issues
- View Development Tools (for worklogs)
- Access to specific projects you want to analyze

### Authentication Testing

```python
def test_connection(self) -> Dict[str, Any]:
    """Test connection to Jira API and validate authentication."""
    url = f"{self.base_url}/rest/api/2/myself"

    try:
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Jira: {str(e)}")
```

---

## API Endpoints Used

### Core Project APIs

#### 1. User Information
```http
GET /rest/api/2/myself
```
**Purpose**: Authentication validation, user context
**Used by**: Connection Test, initialization
**Response**: Current user details and permissions

#### 2. Project Discovery
```http
GET /rest/api/2/project
```
**Purpose**: List accessible projects
**Used by**: Project validation, Projects Lister
**Response**: Array of project objects with keys, names, metadata

#### 3. Project Validation
```http
GET /rest/api/2/project/{projectKey}
```
**Purpose**: Validate specific project access
**Used by**: Project key validation in all tools
**Response**: Detailed project information

### Board and Sprint APIs

#### 4. Board Discovery
```http
GET /rest/agile/1.0/board
```
**Query Parameters**:
- `projectKeyOrId`: Filter boards by project
- `type`: scrum, kanban, simple
**Used by**: Sprint selection, board management
**Response**: Paginated list of boards with metadata

#### 5. Sprint Retrieval
```http
GET /rest/agile/1.0/board/{boardId}/sprint
```
**Query Parameters**:
- `state`: active, closed, future
- `maxResults`: Pagination limit (default: 50)
**Used by**: Sprint selection in all analysis tools
**Response**: Paginated list of sprints with dates and status

### Issue and Search APIs

#### 6. JQL Issue Search
```http
POST /rest/api/2/search
```
**Body**:
```json
{
    "jql": "project = PROJ AND sprint = 123",
    "startAt": 0,
    "maxResults": 100,
    "fields": ["summary", "status", "assignee", "components", "labels"],
    "expand": ["changelog"]
}
```
**Used by**: All analysis tools for data retrieval
**Response**: Paginated search results with issue details

#### 7. Issue Details
```http
GET /rest/api/2/issue/{issueKey}
```
**Query Parameters**:
- `expand`: changelog, worklogs, transitions
- `fields`: Specific field selection
**Used by**: Detailed analysis, worklog retrieval
**Response**: Complete issue object with history

#### 8. Worklog Retrieval
```http
GET /rest/api/2/issue/{issueKey}/worklog
```
**Used by**: Worklog Summary tool, time analysis
**Response**: Array of worklog entries with time and author

### Bulk Operations APIs

#### 9. Bulk Issue Update
```http
PUT /rest/api/2/issue/bulk
```
**Body**:
```json
{
    "issueUpdates": [
        {
            "issueIdOrKey": "PROJ-123",
            "fields": {
                "labels": ["backend", "reviewed"],
                "components": [{"name": "Backend"}]
            }
        }
    ]
}
```
**Used by**: Label Updater, Components Updater
**Response**: Update results with success/failure status

#### 10. Custom Fields Discovery
```http
GET /rest/api/2/field
```
**Used by**: Custom Fields Identifier helper
**Response**: Array of all fields with IDs, names, and types

### Component Management APIs

#### 11. Project Components
```http
GET /rest/api/2/project/{projectKey}/components
```
**Used by**: Components validation, Components Updater
**Response**: Array of project components with metadata

---

## Rate Limiting

### Jira Cloud Rate Limits

**Standard Limits:**
- **10 requests per second** per user
- **60 requests per minute** per user
- **3000 requests per hour** per user

**SMT Rate Limit Handling:**

```python
import time
from requests.exceptions import HTTPError

def execute_jql(self, jql: str, max_results: int = 100) -> Dict[str, Any]:
    """Execute JQL query with automatic rate limit handling."""

    for attempt in range(3):  # Max 3 retries
        try:
            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except HTTPError as e:
            if attempt == 2:  # Last attempt
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Optimization Strategies

**1. Pagination Management**
```python
def get_all_results(self, jql: str) -> List[Dict]:
    """Retrieve all results using pagination."""
    all_issues = []
    start_at = 0
    max_results = 100  # Optimal batch size

    while True:
        response = self.execute_jql(jql, max_results, start_at)
        issues = response.get('issues', [])
        all_issues.extend(issues)

        if len(issues) < max_results:
            break

        start_at += max_results
        time.sleep(0.1)  # Small delay between requests

    return all_issues
```

**2. Field Selection**
```python
# Only request needed fields to reduce response size
fields = ["summary", "status", "assignee", "customfield_10016"]  # Specific fields only
# Instead of requesting all fields (slower, rate limit impact)
```

**3. Intelligent Caching**
```python
# Cache project metadata, user info, and other static data
# Avoid repeated requests for same information within session
```

---

## Custom Fields Integration

### Understanding Custom Fields

Jira custom fields have internal IDs like `customfield_10016` that vary between instances. SMT needs mapping between logical fields and physical field IDs.

### Configuration Mapping

**In .env file:**
```bash
# Story Points (varies by instance)
JIRA_STORY_POINTS_FIELD=customfield_10016

# Epic Link
JIRA_EPIC_LINK_FIELD=customfield_10014

# Sprint Field
JIRA_SPRINT_FIELD=customfield_10020

# Responsible Person (custom)
JIRA_RESPONSIBLE_FIELD=customfield_11000
```

### Custom Field Discovery

**Automated Discovery:**
```python
def get_fields(self) -> List[Dict[str, Any]]:
    """Retrieve all custom fields from Jira instance."""
    url = f"{self.base_url}/rest/api/2/field"
    response = requests.get(url, headers=self.headers)
    response.raise_for_status()

    fields = response.json()

    # Filter for custom fields
    custom_fields = [
        field for field in fields
        if field['id'].startswith('customfield_')
    ]

    return custom_fields
```

**Usage in Analysis:**
```python
def extract_story_points(self, issue: Dict) -> Optional[float]:
    """Extract story points from issue, handling custom field mapping."""
    story_points_field = JIRA_CONFIG.get('story_points_field', 'customfield_10016')

    fields = issue.get('fields', {})
    story_points = fields.get(story_points_field)

    return float(story_points) if story_points is not None else None
```

### Adding New Custom Field Support

**1. Identify Field ID**
```python
# Use Custom Fields Identifier helper tool
# Or manually inspect Jira issue JSON
```

**2. Add to Configuration**
```bash
# Add to .env file
JIRA_MY_CUSTOM_FIELD=customfield_12345
```

**3. Update Field Extraction**
```python
def extract_custom_field(self, issue: Dict, field_name: str) -> Any:
    """Generic custom field extraction."""
    field_id = JIRA_CONFIG.get(field_name.lower() + '_field')
    if not field_id:
        return None

    return issue.get('fields', {}).get(field_id)
```

---

## Extending API Functionality

### Adding New Endpoints

**1. Add Method to JiraClient**
```python
def get_project_versions(self, project_key: str) -> List[Dict]:
    """Retrieve project versions (for release tracking)."""
    url = f"{self.base_url}/rest/api/2/project/{project_key}/versions"

    try:
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get project versions: {e}")
        return []
```

**2. Use in Analysis Tools**
```python
class ReleaseAnalysisTool(BaseScrumMasterTool):
    def run(self):
        project_key = self.get_project_key()
        versions = self.jira_client.get_project_versions(project_key)
        # Analysis logic here
```

### Custom Analysis Examples

**1. Epic Analysis**
```python
def get_epic_issues(self, epic_key: str) -> List[Dict]:
    """Get all issues in an epic."""
    epic_link_field = JIRA_CONFIG.get('epic_link_field', 'customfield_10014')
    jql = f'"{epic_link_field}" = {epic_key}'

    return self.execute_jql(jql).get('issues', [])
```

**2. User Story Analysis**
```python
def get_user_stories_by_persona(self, project_key: str, persona: str) -> List[Dict]:
    """Find user stories mentioning specific persona."""
    jql = f'project = {project_key} AND text ~ "{persona}" AND issuetype = Story'

    return self.execute_jql(jql).get('issues', [])
```

**3. Cross-Project Dependencies**
```python
def find_cross_project_links(self, project_key: str) -> List[Dict]:
    """Find issues linked to other projects."""
    jql = f'project = {project_key} AND issueFunction in linkedIssuesOf("project != {project_key}")'

    return self.execute_jql(jql).get('issues', [])
```

---

## Error Handling

### HTTP Error Categories

**1. Authentication Errors (401)**
```python
def handle_auth_error(self, response):
    """Handle authentication failures."""
    if response.status_code == 401:
        raise AuthenticationError(
            "Jira authentication failed. Check your Personal Access Token."
        )
```

**2. Permission Errors (403)**
```python
def handle_permission_error(self, response, resource):
    """Handle permission denied errors."""
    if response.status_code == 403:
        raise PermissionError(
            f"Access denied to {resource}. Check your Jira permissions."
        )
```

**3. Not Found Errors (404)**
```python
def handle_not_found_error(self, response, resource):
    """Handle resource not found errors."""
    if response.status_code == 404:
        raise ValueError(f"{resource} not found. Check the ID/key and try again.")
```

**4. Rate Limit Errors (429)**
```python
def handle_rate_limit(self, response):
    """Handle rate limiting with automatic retry."""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return True  # Indicate retry should happen
    return False
```

### Comprehensive Error Handling Pattern

```python
def safe_api_call(self, method: str, url: str, **kwargs) -> Dict:
    """Make API call with comprehensive error handling."""

    for attempt in range(3):
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)

            # Handle rate limiting
            if self.handle_rate_limit(response):
                continue

            # Handle other HTTP errors
            if response.status_code == 401:
                self.handle_auth_error(response)
            elif response.status_code == 403:
                self.handle_permission_error(response, url)
            elif response.status_code == 404:
                self.handle_not_found_error(response, url)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}")
            if attempt == 2:
                raise TimeoutError("Jira API request timed out after 3 attempts")

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
            if attempt == 2:
                raise ConnectionError("Unable to connect to Jira API")

        time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Performance Optimization

### Batching Strategies

**1. Bulk Issue Retrieval**
```python
def get_issues_batch(self, issue_keys: List[str]) -> List[Dict]:
    """Retrieve multiple issues in single request."""
    if not issue_keys:
        return []

    # JQL with key list (more efficient than individual requests)
    keys_str = ','.join(issue_keys)
    jql = f"key in ({keys_str})"

    return self.execute_jql(jql).get('issues', [])
```

**2. Field Optimization**
```python
# Specify only needed fields
essential_fields = [
    "summary", "status", "assignee",
    "customfield_10016",  # Story points
    "components", "labels"
]

response = self.execute_jql(jql, fields=essential_fields)
```

**3. Expand Optimization**
```python
# Only expand what you need
expand_options = ["changelog"]  # Don't expand everything
response = self.execute_jql(jql, expand=expand_options)
```

### Caching Implementation

**1. Session-Level Caching**
```python
class JiraClient:
    def __init__(self):
        self._cache = {}
        # ... other initialization

    def get_project_cached(self, project_key: str) -> Dict:
        """Get project info with caching."""
        cache_key = f"project_{project_key}"

        if cache_key not in self._cache:
            self._cache[cache_key] = self.get_project(project_key)

        return self._cache[cache_key]
```

**2. File-Based Caching (for development)**
```python
import pickle
import os
from datetime import datetime, timedelta

def cached_api_call(self, cache_key: str, api_function, cache_hours: int = 1):
    """Cache API results to disk for development."""
    cache_dir = "cache"
    cache_file = os.path.join(cache_dir, f"{cache_key}.pkl")

    # Check if cache exists and is fresh
    if os.path.exists(cache_file):
        cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if cache_age < timedelta(hours=cache_hours):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

    # Make API call and cache result
    result = api_function()

    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)

    return result
```

### Monitoring and Metrics

**1. Request Timing**
```python
import time

def timed_request(self, method: str, url: str, **kwargs) -> Tuple[Dict, float]:
    """Make request and return result with timing."""
    start_time = time.time()

    response = requests.request(method, url, headers=self.headers, **kwargs)
    response.raise_for_status()

    duration = time.time() - start_time
    logger.debug(f"API call to {url} took {duration:.2f}s")

    return response.json(), duration
```

**2. Rate Limit Monitoring**
```python
def log_rate_limit_headers(self, response):
    """Log rate limit information from response headers."""
    headers = response.headers

    if 'X-RateLimit-Remaining' in headers:
        remaining = headers['X-RateLimit-Remaining']
        logger.debug(f"Rate limit remaining: {remaining}")

        if int(remaining) < 10:
            logger.warning("Approaching rate limit, slowing down requests")
```

---

This API documentation provides the technical foundation for understanding and extending ScrumMaster Tools' Jira integration. For implementation examples, see the source code in `src/scrummaster/core/jira_client.py`.