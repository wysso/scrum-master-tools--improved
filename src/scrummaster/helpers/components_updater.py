"""
Components Updater Tool - Updating components in Jira issues based on labels
Helper tool for bulk updating components in Jira issues based on Backend/Frontend labels
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import json
import logging
from datetime import datetime

# Add path to main project directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Handle imports for different execution methods
try:
    # Try relative imports (when run as module)
    from ..core.base_tool import BaseScrumMasterTool
except ImportError:
    # Fallback to absolute imports (when run directly)
    from src.scrummaster.core.base_tool import BaseScrumMasterTool

from config.jira_config import CUSTOM_FIELDS

logger = logging.getLogger(__name__)

class ComponentsUpdaterTool(BaseScrumMasterTool):
    """Tool for updating components in Jira issues based on labels"""

    def __init__(self):
        super().__init__("Updating components based on Backend/Frontend labels")

    def run(self):
        """Main method running component update"""
        print("🔧 Updating components based on Backend/Frontend labels")
        print("=" * 60)

        # Get project
        project_key = self.get_project_key()

        # Validate components exist in project
        if not self._validate_components_exist(project_key):
            return

        # Get update mode
        mode = self._get_update_mode()

        if mode == "single":
            self._update_single_issue(project_key)
        elif mode == "sprint":
            self._update_sprint_issues(project_key)
        elif mode == "custom_jql":
            self._update_custom_jql_issues(project_key)
        elif mode == "bulk":
            self._update_bulk_issues(project_key)

    def _validate_components_exist(self, project_key):
        """Validate that Backend and Frontend components exist in project"""
        print(f"\n🔍 Checking if Backend and Frontend components exist in project {project_key}...")

        try:
            components = self.jira_client.get_project_components(project_key)
            component_names = [comp.get('name', '') for comp in components]

            backend_exists = "Backend" in component_names
            frontend_exists = "Frontend" in component_names

            print(f"📋 Available components in project:")
            for comp in components:
                name = comp.get('name', 'Unknown')
                desc = comp.get('description', '')
                print(f"  • {name}" + (f" - {desc}" if desc else ""))

            if not backend_exists and not frontend_exists:
                print(f"\n❌ ERROR: Neither 'Backend' nor 'Frontend' components exist in project {project_key}")
                print("💡 You need to create these components in Jira before running this tool.")
                return False

            if not backend_exists:
                print(f"\n⚠️  WARNING: 'Backend' component does not exist in project {project_key}")
                print("💡 Issues with 'Backend' label will be skipped.")

            if not frontend_exists:
                print(f"\n⚠️  WARNING: 'Frontend' component does not exist in project {project_key}")
                print("💡 Issues with 'Frontend' label will be skipped.")

            if backend_exists and frontend_exists:
                print(f"\n✅ Both 'Backend' and 'Frontend' components found in project.")

            return True

        except Exception as e:
            logger.error(f"Error checking components for project {project_key}: {e}")
            print(f"❌ Error checking components for project {project_key}: {e}")
            return False

    def _get_update_mode(self):
        """Select update mode"""
        print("\n🔧 Select update mode:")
        print("1. Single issue")
        print("2. All issues in sprint")
        print("3. Custom JQL Query (manual component selection)")
        print("4. Bulk update based on Backend/Frontend labels")

        while True:
            choice = input("\nSelect mode (1-4): ").strip()

            if choice == "1":
                return "single"
            elif choice == "2":
                return "sprint"
            elif choice == "3":
                return "custom_jql"
            elif choice == "4":
                return "bulk"
            else:
                print("❌ Invalid option. Please select 1-4.")

    def _update_single_issue(self, project_key):
        """Update single issue"""
        issue_key = input(f"\nEnter issue key (e.g., {project_key}-123): ").strip().upper()

        if not issue_key:
            print("❌ Issue key cannot be empty")
            return

        try:
            # Get current issue
            issue_data = self.jira_client.get_issue_details(issue_key)
            if not issue_data:
                print(f"❌ Issue {issue_key} not found")
                return

            current_labels = issue_data.get('fields', {}).get('labels', [])
            current_components = issue_data.get('fields', {}).get('components', [])
            current_component_names = [comp.get('name', '') for comp in current_components if isinstance(comp, dict)]

            print(f"\n📋 Current state for {issue_key}:")
            print(f"   Labels: {', '.join(current_labels) if current_labels else '(no labels)'}")
            print(f"   Components: {', '.join(current_component_names) if current_component_names else '(no components)'}")

            # Determine which components to add based on labels
            components_to_add = self._determine_components_from_labels(current_labels)

            if not components_to_add:
                print(f"\n⚠️  No Backend or Frontend labels found in issue {issue_key}")
                print("💡 This tool only works with issues that have 'Backend' or 'Frontend' labels.")
                return

            # Show planned changes
            self._show_planned_changes([{
                'key': issue_key,
                'current_components': current_component_names,
                'components_to_add': components_to_add,
                'labels': current_labels
            }])

            # Confirm update
            confirm = input(f"\nDo you want to update components for {issue_key}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Update cancelled")
                return

            # Update components
            self._update_issue_components(issue_key, current_component_names, components_to_add)

        except Exception as e:
            logger.error(f"Error updating issue {issue_key}: {e}")
            print(f"❌ Error updating issue {issue_key}: {e}")

    def _update_custom_jql_issues(self, project_key):
        """Update issues using custom JQL with manual component selection"""
        print(f"\n📝 Custom JQL Query - Manual Component Selection")
        print("=" * 60)

        # Step 1: Get JQL from user
        print(f"Enter JQL query for issues to update:")
        print(f"Example: project = \"{project_key}\" AND status = \"To Do\"")
        jql = input("JQL: ").strip()

        if not jql:
            print("❌ JQL query cannot be empty")
            return

        try:
            # Step 2: Count results first (quick check)
            print(f"\n🔍 Counting issues matching your query...")
            count_result = self.jira_client.execute_jql(jql, fields=['key'], max_results=0)
            total_count = count_result.get('total', 0)

            if total_count == 0:
                print("❌ No issues found for given JQL query")
                return

            print(f"✅ Found {total_count} issues matching your query")

            # Step 3: Get component name from user and validate
            print(f"\n🏷️  Enter component name to add to these issues:")
            print(f"Available components will be checked...")
            component_name = input("Component name (e.g., Backend, Frontend, DevOps): ").strip()

            if not component_name:
                print("❌ Component name cannot be empty")
                return

            # Validate component exists in project
            print(f"\n🔍 Validating component '{component_name}' exists in project...")
            components = self.jira_client.get_project_components(project_key)
            component_names = [comp.get('name', '') for comp in components]

            if component_name not in component_names:
                print(f"❌ Component '{component_name}' does not exist in project {project_key}")
                print(f"💡 Available components: {', '.join(component_names) if component_names else 'None'}")
                return

            print(f"✅ Component '{component_name}' found in project")

            # Step 4: Get full issue data and filter
            print(f"\n🔍 Fetching full issue data and filtering...")
            issues = self.jira_client.get_all_results(jql, ['key', 'summary', 'components'])

            # Filter out issues that already have this component
            issues_to_update = []
            issues_skipped = 0

            for issue in issues:
                issue_key = issue.get('key', '')
                components = issue.get('fields', {}).get('components', [])
                current_component_names = [comp.get('name', '') for comp in components if isinstance(comp, dict)]

                if component_name not in current_component_names:
                    issues_to_update.append({
                        'key': issue_key,
                        'summary': issue.get('fields', {}).get('summary', ''),
                        'current_components': current_component_names
                    })
                else:
                    issues_skipped += 1

            if not issues_to_update:
                print(f"⚠️  All {total_count} issues already have component '{component_name}'")
                print("💡 No updates needed")
                return

            # Step 5: Show filtered list of IDs
            print(f"\n📋 Issues to update with component '{component_name}':")
            print(f"Total: {len(issues_to_update)} issues (skipped {issues_skipped} that already have this component)")
            print("=" * 60)

            # Show issue keys in groups of 10
            issue_keys = [issue['key'] for issue in issues_to_update]
            for i in range(0, len(issue_keys), 10):
                keys_group = issue_keys[i:i+10]
                print(f"  {', '.join(keys_group)}")

            if len(issues_to_update) > 20:
                print(f"... and {len(issues_to_update) - 20} more")

            print("=" * 60)

            # Step 6: Confirmation
            confirm = input(f"\nDo you want to add component '{component_name}' to {len(issues_to_update)} issues? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Update cancelled")
                return

            # Step 7: Execute updates
            self._execute_custom_component_updates(issues_to_update, component_name)

        except Exception as e:
            logger.error(f"Error in custom JQL update: {e}")
            print(f"❌ Error in custom JQL update: {e}")

    def _execute_custom_component_updates(self, issues_to_update, component_name):
        """Execute component updates for custom JQL results"""
        print(f"\n🔄 Adding component '{component_name}' to {len(issues_to_update)} issues...")

        success_count = 0
        error_count = 0

        for i, issue in enumerate(issues_to_update, 1):
            issue_key = issue['key']
            current_components = issue['current_components']

            print(f"  Updating {i}/{len(issues_to_update)}: {issue_key}")

            try:
                # Add component to existing components
                final_components = list(set(current_components + [component_name]))
                success = self.jira_client.update_issue_components(issue_key, final_components)

                if success:
                    success_count += 1
                    print(f"    ✅ Added '{component_name}' to {issue_key}")
                else:
                    error_count += 1
                    print(f"    ❌ Failed to update {issue_key}")

            except Exception as e:
                logger.error(f"Error updating {issue_key}: {e}")
                error_count += 1
                print(f"    ❌ Error updating {issue_key}: {e}")

        print(f"\n📊 Update summary:")
        print(f"  ✅ Successfully updated: {success_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  📋 Total processed: {len(issues_to_update)}")
        print(f"  🏷️  Component added: '{component_name}'")

    def _update_bulk_issues(self, project_key):
        """Bulk update of issues by JQL"""
        print(f"\n📝 Enter JQL query for issues to update:")
        print(f"Example: project = \"{project_key}\" AND status = \"To Do\" AND (labels = \"Backend\" OR labels = \"Frontend\")")

        jql = input("JQL: ").strip()

        if not jql:
            print("❌ JQL query cannot be empty")
            return

        try:
            # Get issues
            print(f"\n🔍 Searching for issues...")
            issues = self.jira_client.get_all_results(jql, ['labels', 'summary', 'components'])

            if not issues:
                print("❌ No issues found for given criteria")
                return

            print(f"✅ Found {len(issues)} issues")

            # Analyze issues
            issues_to_update = self._analyze_issues_for_components(issues)

            if not issues_to_update:
                print("⚠️  No issues found with Backend or Frontend labels that need component updates")
                return

            # Show planned changes
            self._show_planned_changes(issues_to_update)

            # Confirm update
            confirm = input(f"\nDo you want to update components for {len(issues_to_update)} issues? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Update cancelled")
                return

            # Update all issues
            self._bulk_update_components(issues_to_update)

        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            print(f"❌ Error in bulk update: {e}")

    def _update_sprint_issues(self, project_key):
        """Update all issues in sprint"""
        # Get sprint
        sprint_data = self.get_sprint_selection(project_key)
        sprint_name = sprint_data.get('name', 'No name')

        print(f"\n🎯 Updating components for issues with Backend/Frontend labels in sprint: {sprint_name}")

        # Build JQL to find issues with Backend/Frontend labels
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND (labels = "Backend" OR labels = "Frontend")
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        ORDER BY key ASC
        """

        try:
            # Get issues
            print(f"🔍 Searching for issues with Backend/Frontend labels in sprint...")
            issues = self.jira_client.get_all_results(jql, ['labels', 'summary', 'components'])

            if not issues:
                print(f"❌ No issues with Backend/Frontend labels found in sprint '{sprint_name}'")
                return

            print(f"✅ Found {len(issues)} issues with Backend/Frontend labels")

            # Analyze issues
            issues_to_update = self._analyze_issues_for_components(issues)

            if not issues_to_update:
                print("⚠️  All issues already have appropriate components set")
                return

            # Show planned changes
            self._show_planned_changes(issues_to_update)

            # Confirm update
            confirm = input(f"\nDo you want to update components for {len(issues_to_update)} issues? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Update cancelled")
                return

            # Update all issues
            self._bulk_update_components(issues_to_update)

        except Exception as e:
            logger.error(f"Error updating sprint issues: {e}")
            print(f"❌ Error updating sprint issues: {e}")

    def _determine_components_from_labels(self, labels):
        """Determine which components to add based on labels"""
        components_to_add = []

        if "Backend" in labels:
            components_to_add.append("Backend")

        if "Frontend" in labels:
            components_to_add.append("Frontend")

        return components_to_add

    def _analyze_issues_for_components(self, issues):
        """Analyze issues and determine which need component updates"""
        issues_to_update = []

        for issue in issues:
            issue_key = issue.get('key', '')
            summary = issue.get('fields', {}).get('summary', '')
            labels = issue.get('fields', {}).get('labels', [])
            components = issue.get('fields', {}).get('components', [])
            current_component_names = [comp.get('name', '') for comp in components if isinstance(comp, dict)]

            # Determine which components should be added based on labels
            components_to_add = self._determine_components_from_labels(labels)

            if not components_to_add:
                continue  # Skip issues without Backend/Frontend labels

            # Check if components need to be added
            components_needed = [comp for comp in components_to_add if comp not in current_component_names]

            if components_needed:
                issues_to_update.append({
                    'key': issue_key,
                    'summary': summary,
                    'current_components': current_component_names,
                    'components_to_add': components_needed,
                    'labels': labels
                })

        return issues_to_update

    def _show_planned_changes(self, issues_to_update):
        """Show planned changes before execution"""
        print(f"\n📋 Planned changes for {len(issues_to_update)} issues:")
        print("=" * 80)

        for i, issue in enumerate(issues_to_update, 1):
            issue_key = issue['key']
            summary = issue.get('summary', '')
            current_components = issue['current_components']
            components_to_add = issue['components_to_add']
            labels = issue['labels']

            print(f"\n{i}. {issue_key}: {summary[:50]}...")
            print(f"   Labels: {', '.join(labels)}")
            print(f"   Current components: {', '.join(current_components) if current_components else '(none)'}")
            print(f"   Components to add: {', '.join(components_to_add)}")

            # Calculate final components
            final_components = list(set(current_components + components_to_add))
            print(f"   Final components: {', '.join(final_components)}")

        print("\n" + "=" * 80)

    def _update_issue_components(self, issue_key, current_components, components_to_add):
        """Update components for single issue"""
        try:
            # Calculate final components (add to existing, don't replace)
            final_components = list(set(current_components + components_to_add))

            # Update issue using JiraClient method
            success = self.jira_client.update_issue_components(issue_key, final_components)

            if success:
                print(f"✅ Updated components for {issue_key}")
                print(f"   Added components: {', '.join(components_to_add)}")
                print(f"   Final components: {', '.join(final_components)}")
            else:
                print(f"❌ Failed to update {issue_key}")

        except Exception as e:
            logger.error(f"Error updating components for {issue_key}: {e}")
            print(f"❌ Error updating {issue_key}: {e}")

    def _bulk_update_components(self, issues_to_update):
        """Bulk update components for multiple issues"""
        print(f"\n🔄 Updating components for {len(issues_to_update)} issues...")

        success_count = 0
        error_count = 0

        for i, issue in enumerate(issues_to_update, 1):
            issue_key = issue['key']
            current_components = issue['current_components']
            components_to_add = issue['components_to_add']

            print(f"  Updating {i}/{len(issues_to_update)}: {issue_key}")

            try:
                self._update_issue_components(issue_key, current_components, components_to_add)
                success_count += 1
            except Exception as e:
                logger.error(f"Error updating {issue_key}: {e}")
                error_count += 1

        print(f"\n📊 Update summary:")
        print(f"  ✅ Successfully updated: {success_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  📋 Total processed: {len(issues_to_update)}")

def main():
    """Main function running the tool"""
    tool = ComponentsUpdaterTool()
    tool.safe_run()

if __name__ == "__main__":
    main()