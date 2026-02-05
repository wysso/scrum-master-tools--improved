#!/usr/bin/env python3
"""
Responsible Field Updater Tool

This tool helps automatically set the 'responsible' field in Jira tasks
based on the owner determination logic from planning analysis.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.scrummaster.core.base_tool import BaseScrumMasterTool
from config.jira_config import CUSTOM_FIELDS

# Configure logging
logger = logging.getLogger(__name__)

class ResponsibleFieldUpdaterTool(BaseScrumMasterTool):
    """Tool for updating responsible field in Jira tasks"""
    
    def __init__(self):
        super().__init__("Responsible Field Updater")
    
    def run(self):
        """Main execution method"""
        print(f"🎯 {self.tool_name}")
        print("=" * 50)

        # Get project
        project_key = self.get_project_key()

        # Get sprint selection
        sprint_selection = self._get_sprint_selection(project_key)

        if not sprint_selection:
            print("❌ No sprints selected")
            return

        # Find tasks with empty responsible field in selected sprints
        print(f"\n🔍 Searching for tasks with empty responsible field in selected sprints...")
        empty_responsible_tasks = self._find_empty_responsible_tasks(project_key, sprint_selection)

        if not empty_responsible_tasks:
            print(f"✅ All tasks in selected sprints have responsible field set!")
            return

        print(f"📋 Found {len(empty_responsible_tasks)} tasks with empty responsible field")

        # Analyze and suggest responsible persons
        suggestions = self._analyze_and_suggest_responsible(empty_responsible_tasks)

        if not suggestions:
            print("❌ No suggestions could be generated")
            return

        # Display suggestions
        self._display_suggestions(suggestions)

        # Ask user what to do
        self._handle_user_choice(suggestions)
    
    def _find_empty_responsible_tasks(self, project_key, sprint_selection):
        """Find all tasks in selected sprints with empty responsible field"""

        # Build JQL to find tasks with empty responsible field in selected sprints
        # Use field name instead of field ID for JQL
        sprint_conditions = []
        for sprint_name in sprint_selection:
            sprint_conditions.append(f'Sprint = "{sprint_name}"')

        sprint_jql = " OR ".join(sprint_conditions)

        jql = f"""
        project = "{project_key}"
        AND "Responsible" is EMPTY
        AND ({sprint_jql})
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        ORDER BY key ASC
        """

        # Define fields to retrieve (use field ID for API)
        responsible_field = CUSTOM_FIELDS['responsible']
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'created', 'updated',
            'timeoriginalestimate', 'timespent', 'timeestimate', responsible_field, 'labels'
        ]

        print(f"JQL: {jql.strip()}")

        # Execute query to get all issues with changelog
        all_issues = self.jira_client.get_all_results(jql, fields, expand=['changelog'])

        return all_issues
    
    def _analyze_and_suggest_responsible(self, tasks):
        """Analyze tasks and suggest responsible persons based on owner logic"""
        suggestions = []
        
        print(f"\n📊 Analyzing tasks to suggest responsible persons...")

        for i, task in enumerate(tasks, 1):
            task_key = task.get('key', '')
            print(f"   Analyzing {i}/{len(tasks)}: {task_key}")

            # Extract task data
            fields = task.get('fields', {})
            status = fields.get('status', {}).get('name', '')
            assignee = fields.get('assignee')
            assignee_name = assignee.get('displayName', '') if assignee else ''

            # Determine suggested owner using the same logic as planning.py
            changelog = task.get('changelog', {})
            suggested_responsible, source = self._determine_owner('', assignee_name, status, changelog, None, None)

            if suggested_responsible and suggested_responsible != 'Unassigned':
                suggestions.append({
                    'task_key': task_key,
                    'summary': fields.get('summary', ''),
                    'status': status,
                    'current_assignee': assignee_name,
                    'suggested_responsible': suggested_responsible,
                    'recommendation_source': source,
                    'task_object': task
                })

        return suggestions
    
    def _determine_owner(self, responsible_name, assignee_name, status, changelog, sprint_start, sprint_end):
        """Determine task owner - same logic as in planning.py with additional fallback"""
        # If responsible field is filled, use it
        if responsible_name:
            return responsible_name, "existing_responsible"

        # Check changelog for first person who changed status to "In Progress"
        if changelog and changelog.get('histories'):
            for history in changelog['histories']:
                author_name = history.get('author', {}).get('displayName', '')

                # Check if this history entry contains status change to "In Progress"
                for item in history.get('items', []):
                    if (item.get('field') == 'status' and
                        item.get('toString') == 'In Progress' and
                        author_name):
                        return author_name, "changelog_in_progress"

        # If task is currently "In Progress" and has assignee, use assignee
        if status == 'In Progress' and assignee_name:
            return assignee_name, "current_in_progress"

        # Additional fallback: If task is in "To Do" or "Backlog" and has assignee, use assignee
        if status in ['To Do', 'Backlog', 'Open', 'New'] and assignee_name:
            return assignee_name, "assignee_fallback"

        # No owner found
        return 'Unassigned', "no_owner"
    
    def _display_suggestions(self, suggestions):
        """Display suggestions to user"""
        print(f"\n📋 SUGGESTIONS FOR RESPONSIBLE FIELD:")
        print("=" * 80)

        # Create source descriptions
        source_descriptions = {
            "existing_responsible": "Already has responsible",
            "changelog_in_progress": "First person to move to In Progress",
            "current_in_progress": "Current assignee (task In Progress)",
            "assignee_fallback": "Current assignee (task in To Do/Backlog)",
            "no_owner": "No owner found"
        }

        for i, suggestion in enumerate(suggestions, 1):
            source = suggestion.get('recommendation_source', 'unknown')
            source_desc = source_descriptions.get(source, 'Unknown source')

            print(f"{i:2d}. {suggestion['task_key']} - {suggestion['summary'][:50]}...")
            print(f"    Status: {suggestion['status']}")
            print(f"    Current Assignee: {suggestion['current_assignee'] or 'None'}")
            print(f"    Suggested Responsible: {suggestion['suggested_responsible']}")
            print(f"    Reason: {source_desc}")
            print()
    
    def _handle_user_choice(self, suggestions):
        """Handle user choice for updating tasks"""
        print("🤔 What would you like to do?")
        print("1. Update all suggested tasks")
        print("2. Select specific tasks to update")
        print("3. Exit without updating")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                if choice in ['1', '2', '3']:
                    break
                print("❌ Please enter 1, 2, or 3")
            except KeyboardInterrupt:
                print("\n👋 Operation cancelled")
                return
        
        if choice == '3':
            print("👋 Exiting without updates")
            return
        elif choice == '1':
            self._update_all_tasks(suggestions)
        elif choice == '2':
            self._update_selected_tasks(suggestions)
    
    def _update_all_tasks(self, suggestions):
        """Update all suggested tasks"""
        print(f"\n🚀 Updating {len(suggestions)} tasks...")

        # Final confirmation
        confirm = input(f"Are you sure you want to update {len(suggestions)} tasks? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Update cancelled")
            return

        success_count = 0
        error_count = 0

        for suggestion in suggestions:
            if self._update_single_task(suggestion, suggestions):
                success_count += 1
            else:
                error_count += 1

        print(f"\n📊 UPDATE SUMMARY:")
        print(f"   ✅ Successfully updated: {success_count} tasks")
        print(f"   ❌ Failed to update: {error_count} tasks")
    
    def _update_selected_tasks(self, suggestions):
        """Update selected tasks"""
        print(f"\n📝 Select tasks to update (comma-separated numbers, e.g., 1,3,5):")
        print("   Or type 'all' to select all tasks")
        print("   Or type 'none' to cancel")
        
        while True:
            try:
                selection = input("Enter selection: ").strip().lower()
                
                if selection == 'none':
                    print("❌ Update cancelled")
                    return
                elif selection == 'all':
                    selected_indices = list(range(len(suggestions)))
                    break
                else:
                    # Parse comma-separated numbers
                    selected_indices = []
                    for num_str in selection.split(','):
                        try:
                            num = int(num_str.strip()) - 1  # Convert to 0-based index
                            if 0 <= num < len(suggestions):
                                selected_indices.append(num)
                            else:
                                print(f"❌ Number {num + 1} is out of range")
                                raise ValueError()
                        except ValueError:
                            print(f"❌ Invalid number: {num_str.strip()}")
                            raise ValueError()
                    break
            except (ValueError, KeyboardInterrupt):
                if isinstance(sys.exc_info()[1], KeyboardInterrupt):
                    print("\n👋 Operation cancelled")
                    return
                print("❌ Please enter valid numbers or 'all' or 'none'")
        
        if not selected_indices:
            print("❌ No tasks selected")
            return
        
        selected_tasks = [suggestions[i] for i in selected_indices]
        
        print(f"\n📋 Selected {len(selected_tasks)} tasks for update:")
        for task in selected_tasks:
            print(f"   • {task['task_key']} → {task['suggested_responsible']}")
        
        # Final confirmation
        confirm = input(f"\nProceed with updating {len(selected_tasks)} tasks? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Update cancelled")
            return
        
        success_count = 0
        error_count = 0

        for task in selected_tasks:
            if self._update_single_task(task, suggestions):
                success_count += 1
            else:
                error_count += 1

        print(f"\n📊 UPDATE SUMMARY:")
        print(f"   ✅ Successfully updated: {success_count} tasks")
        print(f"   ❌ Failed to update: {error_count} tasks")

    def _update_single_task(self, suggestion, all_suggestions):
        """Update single task's responsible field"""
        task_key = suggestion['task_key']
        suggested_responsible = suggestion['suggested_responsible']

        try:
            print(f"   Updating {task_key} → {suggested_responsible}")

            # Find user by display name
            user_info = self._find_user_by_display_name(suggested_responsible, all_suggestions)
            if not user_info:
                print(f"   ❌ Could not find user: {suggested_responsible}")
                return False

            # Prepare update data
            responsible_field = CUSTOM_FIELDS['responsible']

            # Use accountId if available, otherwise fall back to name
            if user_info.get('accountId'):
                user_ref = {"accountId": user_info['accountId']}
            else:
                user_ref = {"name": user_info['name']}

            update_data = {
                "fields": {
                    responsible_field: user_ref
                }
            }

            # Update the task
            success = self.jira_client.update_issue(task_key, update_data)

            if success:
                print(f"   ✅ Updated {task_key}")
                return True
            else:
                print(f"   ❌ Failed to update {task_key}")
                return False

        except Exception as e:
            print(f"   ❌ Error updating {task_key}: {str(e)}")
            logger.error(f"Error updating {task_key}: {str(e)}")
            return False
    
    def _find_user_by_display_name(self, display_name, suggestions):
        """Find user information by display name from existing task data"""
        try:
            # First, try to find the user in assignee data from the suggestions
            for suggestion in suggestions:
                task = suggestion['task_object']
                fields = task.get('fields', {})

                # Check assignee
                assignee = fields.get('assignee')
                if assignee and assignee.get('displayName') == display_name:
                    return {
                        'name': assignee.get('name', ''),
                        'displayName': assignee.get('displayName', ''),
                        'accountId': assignee.get('accountId', '')
                    }

                # Check responsible field
                responsible_field = CUSTOM_FIELDS['responsible']
                responsible = fields.get(responsible_field)
                if responsible and responsible.get('displayName') == display_name:
                    return {
                        'name': responsible.get('name', ''),
                        'displayName': responsible.get('displayName', ''),
                        'accountId': responsible.get('accountId', '')
                    }

            # If not found in suggestions, we need to search more broadly
            # This is a simplified fallback - in production you might want to
            # implement proper user search via Jira API
            logger.warning(f"User {display_name} not found in current task data")
            return None

        except Exception as e:
            logger.error(f"Error finding user {display_name}: {str(e)}")
            return None

    def _get_sprint_selection(self, project_key):
        """Get sprint selection from user"""
        print(f"\n📅 Sprint Selection:")
        print("1. Select single sprint")
        print("2. Select multiple sprints")
        print("3. All active/recent sprints")

        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                if choice in ['1', '2', '3']:
                    break
                print("❌ Please enter 1, 2, or 3")
            except KeyboardInterrupt:
                print("\n👋 Operation cancelled")
                return None

        if choice == '1':
            return self._select_single_sprint(project_key)
        elif choice == '2':
            return self._select_multiple_sprints(project_key)
        elif choice == '3':
            return self._select_all_recent_sprints(project_key)

    def _select_single_sprint(self, project_key):
        """Select single sprint"""
        sprint_data = self.get_sprint_selection(project_key)
        if sprint_data:
            return [sprint_data.get('name', '')]
        return None

    def _select_multiple_sprints(self, project_key):
        """Select multiple sprints"""
        print(f"\n🚀 Fetching sprints for project {project_key}...")

        try:
            sprints = self.jira_client.get_project_sprints(project_key)
            if not sprints:
                print(f"❌ No sprints found for project {project_key}")
                return None

            # Display sprints
            print(f"\n📋 Available sprints:")
            for i, sprint in enumerate(sprints, 1):
                sprint_name = sprint.get('name', 'No name')
                sprint_state = sprint.get('state', 'Unknown')
                print(f"  {i:2d}. {sprint_name} ({sprint_state})")

            print(f"\n📝 Select sprints (comma-separated numbers, e.g., 1,3,5):")
            print("   Or type 'all' to select all sprints")

            while True:
                try:
                    selection = input("Enter selection: ").strip().lower()

                    if selection == 'all':
                        return [sprint.get('name', '') for sprint in sprints]
                    else:
                        # Parse comma-separated numbers
                        selected_indices = []
                        for num_str in selection.split(','):
                            try:
                                num = int(num_str.strip()) - 1  # Convert to 0-based index
                                if 0 <= num < len(sprints):
                                    selected_indices.append(num)
                                else:
                                    print(f"❌ Number {num + 1} is out of range")
                                    raise ValueError()
                            except ValueError:
                                print(f"❌ Invalid number: {num_str.strip()}")
                                raise ValueError()

                        if not selected_indices:
                            print("❌ No sprints selected")
                            continue

                        selected_sprints = [sprints[i].get('name', '') for i in selected_indices]
                        print(f"\n📋 Selected {len(selected_sprints)} sprints:")
                        for sprint_name in selected_sprints:
                            print(f"   • {sprint_name}")

                        return selected_sprints

                except (ValueError, KeyboardInterrupt):
                    if isinstance(sys.exc_info()[1], KeyboardInterrupt):
                        print("\n👋 Operation cancelled")
                        return None
                    print("❌ Please enter valid numbers or 'all'")

        except Exception as e:
            print(f"❌ Error fetching sprints: {e}")
            logger.error(f"Error fetching sprints for {project_key}: {e}")
            return None

    def _select_all_recent_sprints(self, project_key):
        """Select all active and recently closed sprints"""
        print(f"\n🚀 Fetching recent sprints for project {project_key}...")

        try:
            sprints = self.jira_client.get_project_sprints(project_key)
            if not sprints:
                print(f"❌ No sprints found for project {project_key}")
                return None

            # Filter for active and closed sprints (exclude future)
            recent_sprints = [
                sprint for sprint in sprints
                if sprint.get('state', '').lower() in ['active', 'closed']
            ]

            if not recent_sprints:
                print("❌ No active or closed sprints found")
                return None

            print(f"📋 Selected {len(recent_sprints)} active/closed sprints:")
            sprint_names = []
            for sprint in recent_sprints:
                sprint_name = sprint.get('name', '')
                sprint_state = sprint.get('state', 'Unknown')
                print(f"   • {sprint_name} ({sprint_state})")
                sprint_names.append(sprint_name)

            return sprint_names

        except Exception as e:
            print(f"❌ Error fetching sprints: {e}")
            logger.error(f"Error fetching sprints for {project_key}: {e}")
            return None

def main():
    """Main function running the tool"""
    tool = ResponsibleFieldUpdaterTool()
    tool.safe_run()

if __name__ == "__main__":
    main()