"""
Jira Client - Client for communication with Jira API
Author: Marek Mróz <marek@mroz.consulting>
"""
import json
import base64
import requests
import logging
from typing import Dict, List, Optional, Any
from config.jira_config import JIRA_CONFIG, SETTINGS

logger = logging.getLogger(__name__)

class JiraClient:
    """
    Client for communication with Jira REST API.

    Handles authentication, HTTP requests, and data retrieval from Jira instance.
    Provides methods for project management, sprint operations, issue querying,
    and bulk data modifications. Uses Personal Access Token (PAT) authentication.

    Attributes:
        base_url (str): Base URL of the Jira instance
        headers (dict): HTTP headers including Bearer authentication token

    Example:
        >>> client = JiraClient()
        >>> projects = client.get_projects()
        >>> issues = client.execute_jql("project = PROJ AND sprint = 123")
    """
    
    def __init__(self):
        """
        Initialize Jira client with configuration from jira_config.

        Loads base URL and Personal Access Token from configuration,
        sets up authentication headers for API requests.
        """
        self.base_url = JIRA_CONFIG['base_url']

        email = JIRA_CONFIG.get('email', '')
        token = JIRA_CONFIG.get('personal_token', '')

        basic = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("utf-8")

        self.headers = {
            'Authorization': f'Basic {basic}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }

    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Jira API and validate authentication.

        Makes a request to /myself endpoint to verify connectivity,
        authentication, and API accessibility.

        Returns:
            Dict[str, Any]: Current user information from Jira API

        Raises:
            requests.exceptions.RequestException: If connection fails
            ValueError: If authentication is invalid

        Example:
            >>> user_info = client.test_connection()
            >>> print(f"Connected as: {user_info['displayName']}")
        """
        url = f"{self.base_url}/rest/api/2/myself"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            raise

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of all accessible projects"""
        url = f"{self.base_url}/rest/api/2/project"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get projects: {e}")
            raise

    def execute_jql(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        next_page_token: Optional[str] = None,
        max_results: int = 100,
        expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute JQL query and return results (Jira Cloud enhanced search)"""
        url = f"{self.base_url}/rest/api/3/search/jql"

        payload: Dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
        }
        if next_page_token:
            payload["nextPageToken"] = next_page_token
        if fields:
            payload["fields"] = fields
        if expand:
            payload["expand"] = expand

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=SETTINGS["timeout"],
                verify=SETTINGS["verify_ssl"],
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_messages = error_data.get("errorMessages", [])
                    if error_messages:
                        raise ValueError(f"JQL query error: {error_messages[0]}")
                    raise ValueError("Invalid JQL query")
                except (json.JSONDecodeError, KeyError):
                    raise ValueError("JQL query error")
            else:
                logger.error(f"HTTP Error: {e}")
                logger.error(f"Response status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                raise


    def search_issues(self, jql: str, fields: Optional[List[str]] = None,
                     start_at: int = 0, max_results: int = 100) -> Dict[str, Any]:
        """Search issues using JQL - alias for execute_jql for backward compatibility"""
        return self.execute_jql(jql, fields, start_at, max_results)
    
    def get_all_results(self, jql: str, fields: Optional[List[str]] = None,
                        expand: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get all results by handling pagination for /rest/api/3/search/jql.
        NOTE: /search/jql does NOT support expand=changelog, so we fetch changelog
        via per-issue calls when requested.
        """
        # If changelog is requested, do a 2-step fetch:
        # 1) search keys via /search/jql (no expand)
        # 2) fetch each issue with expand=changelog via /issue/{key}
        if expand and "changelog" in expand:
            # Step 1: fetch stubs (keys) via search/jql without expand
            stubs: List[Dict[str, Any]] = []
            next_token: Optional[str] = None
            max_results = 100
            seen_tokens = set()

            while True:
                response = self.execute_jql(
                    jql,
                    fields=["summary"],          # minimal payload; key will still be present
                    next_page_token=next_token,
                    max_results=max_results,
                    expand=None
                )

                issues = response.get("issues", [])
                stubs.extend(issues)

                next_token = response.get("nextPageToken")
                is_last = response.get("isLast", False)

                if is_last or not next_token:
                    break
                if next_token in seen_tokens:
                    break
                seen_tokens.add(next_token)

            keys = [i.get("key") for i in stubs if i.get("key")]

            # Step 2: fetch full issue details + changelog per key
            full_issues: List[Dict[str, Any]] = []
            for k in keys:
                issue = self.get_issue(k, fields=fields, expand=["changelog"])
                if issue:
                    full_issues.append(issue)

            return full_issues

        # Normal case (no changelog): use token pagination on /search/jql
        all_issues: List[Dict[str, Any]] = []
        next_token: Optional[str] = None
        max_results = 100
        seen_tokens = set()

        while True:
            response = self.execute_jql(
                jql,
                fields=fields,
                next_page_token=next_token,
                max_results=max_results,
                expand=None
            )

            issues = response.get("issues", [])
            all_issues.extend(issues)

            next_token = response.get("nextPageToken")
            is_last = response.get("isLast", False)

            if is_last or not next_token:
                break
            if next_token in seen_tokens:
                break
            seen_tokens.add(next_token)

        return all_issues

    
    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None,
                expand: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get a single issue (v3) with optional fields and expand (e.g., changelog)."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=SETTINGS["timeout"],
                verify=SETTINGS["verify_ssl"]
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get issue {issue_key}: {e}")
            return None

    
    def get_issue_details(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific issue"""
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get issue details {issue_key}: {e}")
            return None

    def get_issue_with_worklogs(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get issue with worklogs expanded"""
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params={'expand': 'worklog'},
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get issue with worklogs {issue_key}: {e}")
            return None

    def update_issue_labels(self, issue_key: str, new_labels: List[str], notify_users: bool = False) -> bool:
        """Update labels for a specific issue
        
        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            new_labels: List of label names to set
            notify_users: Whether to send email notifications to watchers (default: False)
                         Note: Requires admin/project admin permissions when False
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        
        # Add notifyUsers parameter to suppress notifications
        if not notify_users:
            url += "?notifyUsers=false"
        
        payload = {
            "fields": {
                "labels": new_labels
            }
        }
        
        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=payload,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update labels for {issue_key}: {e}")
            return False

    def get_project_boards(self, project_key: str) -> List[Dict[str, Any]]:
        """Get all boards for a project"""
        boards_url = f"{self.base_url}/rest/agile/1.0/board"

        try:
            boards_response = requests.get(
                boards_url,
                headers=self.headers,
                params={'projectKeyOrId': project_key},
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            boards_response.raise_for_status()
            boards_data = boards_response.json()

            return boards_data.get('values', [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get boards for project {project_key}: {e}")
            return []
    def get_project_sprints(self, project_key: str, board_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all sprints for a project or specific board"""
        # If board_id is provided, get sprints only from that board
        if board_id:
            sprints_url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"

            try:
                all_sprints = []
                start_at = 0
                max_results = 50  # Jira API limit

                while True:
                    sprints_response = requests.get(
                        sprints_url,
                        headers=self.headers,
                        params={
                            'startAt': start_at,
                            'maxResults': max_results
                        },
                        timeout=SETTINGS['timeout'],
                        verify=SETTINGS['verify_ssl']
                    )

                    if sprints_response.status_code == 200:
                        sprints_data = sprints_response.json()
                        values = sprints_data.get('values', [])
                        all_sprints.extend(values)

                        # Check if there are more results
                        is_last = sprints_data.get('isLast', True)
                        if is_last or len(values) < max_results:
                            break

                        start_at += max_results
                    else:
                        logger.warning(f"Failed to get sprints from board {board_id}")
                        break

                return all_sprints

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get sprints for board {board_id}: {e}")
                return []

        # Original logic - get sprints from first board that has them
        # First, get the project to find the board
        project_url = f"{self.base_url}/rest/api/2/project/{project_key}"

        try:
            project_response = requests.get(
                project_url,
                headers=self.headers,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            project_response.raise_for_status()

            # Get boards for the project
            boards_url = f"{self.base_url}/rest/agile/1.0/board"
            boards_response = requests.get(
                boards_url,
                headers=self.headers,
                params={'projectKeyOrId': project_key},
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            boards_response.raise_for_status()
            boards_data = boards_response.json()

            if not boards_data.get('values'):
                logger.warning(f"No boards found for project {project_key}")
                return []

            # Try to get sprints from available boards
            for board in boards_data.get('values', []):
                board_id = board['id']
                board_name = board.get('name', 'Unknown')
                board_type = board.get('type', 'Unknown')

                sprints_url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"

                try:
                    all_sprints = []
                    start_at = 0
                    max_results = 50  # Jira API limit

                    while True:
                        sprints_response = requests.get(
                            sprints_url,
                            headers=self.headers,
                            params={
                                'startAt': start_at,
                                'maxResults': max_results
                            },
                            timeout=SETTINGS['timeout'],
                            verify=SETTINGS['verify_ssl']
                        )

                        if sprints_response.status_code == 200:
                            sprints_data = sprints_response.json()
                            values = sprints_data.get('values', [])
                            all_sprints.extend(values)

                            # Check if there are more results
                            is_last = sprints_data.get('isLast', True)
                            if is_last or len(values) < max_results:
                                break

                            start_at += max_results
                        else:
                            logger.debug(f"Board {board_name} (Type: {board_type}) doesn't support sprints or access denied")
                            break

                    if all_sprints:
                        logger.info(f"Found {len(all_sprints)} sprints on board: {board_name}")
                        return all_sprints
                    else:
                        logger.debug(f"Board {board_name} has no sprints")

                except requests.exceptions.RequestException as e:
                    logger.debug(f"Failed to get sprints from board {board_name}: {e}")
                    continue

            # If no board had sprints
            logger.warning(f"No sprints found on any board for project {project_key}")
            return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get sprints for project {project_key}: {e}")
            return []
    
    def validate_project_key(self, project_input: str) -> Optional[str]:
        """
        Validate project by trying both name and key fields
        Returns the actual project key if found, None otherwise
        """
        # First try with the input as project name
        test_jql_name = f'project = "{project_input}" ORDER BY created DESC'

        try:
            # Test query with project name
            response = self.execute_jql(test_jql_name, ['key'], max_results=1)
            if response.get('issues'):
                # Extract the actual project key from the issue
                issue_key = response['issues'][0]['key']
                project_key = issue_key.split('-')[0]  # Extract project key from issue key (e.g., APIM-123 -> APIM)
                print(f"✅ Found project by name: {project_input} (key: {project_key})")
                return project_key
        except ValueError:
            # If name fails, try with project key
            print(f"⚠️  Project not found by name '{project_input}', checking key...")

            test_jql_key = f'project = "{project_input.upper()}" ORDER BY created DESC'
            try:
                response = self.execute_jql(test_jql_key, ['key'], max_results=1)
                if response.get('issues'):
                    # Extract the actual project key from the issue
                    issue_key = response['issues'][0]['key']
                    project_key = issue_key.split('-')[0]  # Extract project key from issue key
                    print(f"✅ Found project by key: {project_input.upper()} (confirmed key: {project_key})")
                    return project_key
            except ValueError:
                pass

        return None

    def get_fields(self) -> List[Dict[str, Any]]:
        """Get all available fields in Jira"""
        url = f"{self.base_url}/rest/api/2/field"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get fields: {e}")
            raise

    def get_project_components(self, project_key: str) -> List[Dict[str, Any]]:
        """Get all components for a specific project"""
        url = f"{self.base_url}/rest/api/2/project/{project_key}/components"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get components for project {project_key}: {e}")
            raise

    def update_issue_components(self, issue_key: str, components: List[str], notify_users: bool = False) -> bool:
        """Update components for an issue

        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            components: List of component names to set
            notify_users: Whether to send email notifications to watchers (default: False)
                         Note: Requires admin/project admin permissions when False

        Returns:
            bool: True if successful, False otherwise
        """
        # Convert component names to the format expected by Jira API
        component_objects = [{"name": comp} for comp in components]

        update_data = {
            "fields": {
                "components": component_objects
            }
        }

        return self.update_issue(issue_key, update_data, notify_users)

    def update_issue(self, issue_key: str, update_data: Dict[str, Any], notify_users: bool = False) -> bool:
        """Update an issue with the provided data
        
        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            update_data: Dictionary containing the update data
            notify_users: Whether to send email notifications to watchers (default: False)
                         Note: Requires admin/project admin permissions when False
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        
        # Add notifyUsers parameter to suppress notifications
        if not notify_users:
            url += "?notifyUsers=false"

        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=update_data,
                timeout=SETTINGS['timeout'],
                verify=SETTINGS['verify_ssl']
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update issue {issue_key}: {e}")
            return False