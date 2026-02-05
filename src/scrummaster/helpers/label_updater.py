"""
Label Updater Tool - Updating labels in Jira issues
Helper tool for bulk updating labels in Jira issues
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

class LabelUpdaterTool(BaseScrumMasterTool):
    """Tool for updating labels in Jira issues"""
    
    def __init__(self):
        super().__init__("Updating labels in Jira issues")

    def run(self):
        """Main method running label update"""
        print("🏷️  Updating labels in Jira issues")
        print("=" * 50)
        
        # Get project
        project_key = self.get_project_key()
        
        # Get update mode
        mode = self._get_update_mode()
        
        if mode == "single":
            self._update_single_issue(project_key)
        elif mode == "bulk":
            self._update_bulk_issues(project_key)
        elif mode == "sprint":
            self._update_sprint_issues(project_key)
    
    def _get_update_mode(self):
        """Select update mode"""
        print("\n🔧 Select update mode:")
        print("1. Single issue")
        print("2. Bulk update (JQL query)")
        print("3. All issues in sprint")
        
        while True:
            choice = input("\nSelect mode (1-3): ").strip()
            
            if choice == "1":
                return "single"
            elif choice == "2":
                return "bulk"
            elif choice == "3":
                return "sprint"
            else:
                print("❌ Invalid option. Please select 1-3.")

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

            print(f"\n📋 Current labels for {issue_key}:")
            if current_labels:
                for label in current_labels:
                    print(f"  • {label}")
            else:
                print("  (no labels)")

            # Get new labels
            labels_to_add, labels_to_remove = self._get_labels_from_user()

            # Update labels
            self._update_issue_labels(issue_key, labels_to_add, labels_to_remove, current_labels)

        except Exception as e:
            logger.error(f"Error updating issue {issue_key}: {e}")
            print(f"❌ Error updating issue {issue_key}: {e}")

    def _update_bulk_issues(self, project_key):
        """Bulk update of issues by JQL"""
        # Ask user for update type
        print(f"\n📝 Select bulk update type:")
        print("1. Custom JQL query")
        print("2. Check Backend/Frontend labels in sprint")

        while True:
            choice = input("\nSelect option (1-2): ").strip()

            if choice == "1":
                # Original JQL flow
                print(f"\n📝 Enter JQL query for issues to update:")
                print(f"Example: project = \"{project_key}\" AND status = \"To Do\"")

                jql = input("JQL: ").strip()

                if not jql:
                    print("❌ JQL query cannot be empty")
                    return
                break
            elif choice == "2":
                # Check Backend/Frontend labels with auto-detection
                self._auto_update_tech_labels(project_key)
                return
            else:
                print("❌ Invalid option. Please select 1 or 2.")

        try:
            # Get issues
            print(f"\n🔍 Searching for issues...")
            issues = self.jira_client.get_all_results(jql, ['labels', 'summary', 'components'])

            if not issues:
                print("❌ No issues found for given criteria")
                return

            print(f"✅ Found {len(issues)} issues")

            # Show first few issues
            print(f"\nFirst 5 issues:")
            for i, issue in enumerate(issues[:5], 1):
                issue_key = issue.get('key', '')
                summary = issue.get('fields', {}).get('summary', '')
                current_labels = issue.get('fields', {}).get('labels', [])
                print(f"  {i}. {issue_key}: {summary[:50]}...")
                if current_labels:
                    print(f"     Current labels: {', '.join(current_labels)}")
                else:
                    print(f"     Current labels: (no labels)")

            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more")

            # Confirm update
            confirm = input(f"\nDo you want to update labels for all {len(issues)} issues? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Update cancelled")
                return

            # Get labels to update
            labels_to_add, labels_to_remove = self._get_labels_from_user()

            # Update all issues
            self._bulk_update_labels(issues, labels_to_add, labels_to_remove)

        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            print(f"❌ Error in bulk update: {e}")

    def _update_sprint_issues(self, project_key):
        """Update all issues in sprint"""
        # Get sprint
        sprint_data = self.get_sprint_selection(project_key)
        sprint_name = sprint_data.get('name', 'No name')
        
        print(f"\n🎯 Updating labels for all issues in sprint: {sprint_name}")
        
        # Build JQL
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        ORDER BY key ASC
        """
        
        try:
            # Get issues
            print(f"🔍 Searching for issues in sprint...")
            issues = self.jira_client.get_all_results(jql, ['labels', 'summary'])
            
            if not issues:
                print(f"❌ No issues found in sprint '{sprint_name}'")
                return
            
            print(f"✅ Found {len(issues)} issues in sprint")
            
            # Get labels to update
            labels_to_add, labels_to_remove = self._get_labels_from_user()
            
            # Update all issues
            self._bulk_update_labels(issues, labels_to_add, labels_to_remove)
            
        except Exception as e:
            logger.error(f"Error updating sprint issues: {e}")
            print(f"❌ Error updating sprint issues: {e}")

    def _get_jql_for_missing_tech_labels(self, project_key):
        """Get JQL for issues missing Backend/Frontend labels"""
        # Get sprint
        sprint_data = self.get_sprint_selection(project_key)
        sprint_name = sprint_data.get('name', 'No name')

        print(f"\n🎯 Checking for issues without Backend/Frontend labels in sprint: {sprint_name}")

        # Build JQL to get all issues from sprint
        all_jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        ORDER BY key ASC
        """

        print(f"🔍 Fetching all issues from sprint to check labels...")
        all_issues = self.jira_client.get_all_results(all_jql, ['labels', 'summary', 'components'])

        if not all_issues:
            print(f"❌ No issues found in sprint '{sprint_name}'")
            return None

        # Filter issues without tech labels
        issues_without_tech_labels = []
        tech_labels = ['backend', 'frontend', 'fullstack', 'devops', 'qa']

        for issue in all_issues:
            issue_key = issue.get('key', '')
            labels = issue.get('fields', {}).get('labels', [])
            components = issue.get('fields', {}).get('components', [])

            # Check if issue has tech label
            has_tech_label = False
            if labels:
                has_tech_label = any(label.lower() in tech_labels for label in labels)

            # Check if issue has tech component
            has_tech_component = False
            if components:
                component_names = [comp.get('name', '').lower() for comp in components if isinstance(comp, dict)]
                has_tech_component = any(name in tech_labels for name in component_names)

            # If no tech label or component, add to list
            if not has_tech_label and not has_tech_component:
                issues_without_tech_labels.append(issue_key)

        if not issues_without_tech_labels:
            print(f"✅ All issues in sprint already have technology labels!")
            return None

        print(f"⚠️  Found {len(issues_without_tech_labels)} issues without Backend/Frontend labels")

        # Build JQL for these specific issues
        issue_keys = ', '.join(issues_without_tech_labels)
        return f'key in ({issue_keys})'

    def _auto_update_tech_labels(self, project_key):
        """Automatically detect and update tech labels based on task titles"""
        # Get sprint
        sprint_data = self.get_sprint_selection(project_key)
        sprint_name = sprint_data.get('name', 'No name')

        print(f"\n🎯 Checking for issues without Backend/Frontend labels in sprint: {sprint_name}")

        # Build JQL to get all issues from sprint
        all_jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        ORDER BY key ASC
        """

        print(f"🔍 Fetching all issues from sprint to check labels...")
        all_issues = self.jira_client.get_all_results(all_jql, ['labels', 'summary', 'components'])

        if not all_issues:
            print(f"❌ No issues found in sprint '{sprint_name}'")
            return

        # Filter and analyze issues without tech labels
        issues_to_update = []
        tech_labels = ['backend', 'frontend', 'fullstack', 'devops', 'qa']

        for issue in all_issues:
            issue_key = issue.get('key', '')
            summary = issue.get('fields', {}).get('summary', '')
            labels = issue.get('fields', {}).get('labels', [])
            components = issue.get('fields', {}).get('components', [])

            # Check if issue has tech label
            has_tech_label = False
            if labels:
                has_tech_label = any(label.lower() in tech_labels for label in labels)

            # Check if issue has tech component
            has_tech_component = False
            if components:
                component_names = [comp.get('name', '').lower() for comp in components if isinstance(comp, dict)]
                has_tech_component = any(name in tech_labels for name in component_names)

            # If no tech label or component, analyze title
            if not has_tech_label and not has_tech_component:
                suggested_label = self._detect_label_from_title(summary)
                issues_to_update.append({
                    'key': issue_key,
                    'summary': summary,
                    'current_labels': labels,
                    'suggested_label': suggested_label
                })

        if not issues_to_update:
            print(f"✅ All issues in sprint already have technology labels!")
            return

        print(f"\n⚠️  Found {len(issues_to_update)} issues without Backend/Frontend labels")
        print("\n📋 Analysis results:")

        # Group by suggested labels
        backend_issues = [i for i in issues_to_update if i['suggested_label'] == 'Backend']
        frontend_issues = [i for i in issues_to_update if i['suggested_label'] == 'Frontend']
        no_suggestion_issues = [i for i in issues_to_update if i['suggested_label'] is None]

        # Show summary
        if backend_issues:
            print(f"\n🔵 Backend label suggested for {len(backend_issues)} issues:")
            for issue in backend_issues[:5]:
                print(f"  • {issue['key']}: {issue['summary'][:60]}...")
            if len(backend_issues) > 5:
                print(f"  ... and {len(backend_issues) - 5} more")

        if frontend_issues:
            print(f"\n🟢 Frontend label suggested for {len(frontend_issues)} issues:")
            for issue in frontend_issues[:5]:
                print(f"  • {issue['key']}: {issue['summary'][:60]}...")
            if len(frontend_issues) > 5:
                print(f"  ... and {len(frontend_issues) - 5} more")

        if no_suggestion_issues:
            print(f"\n⚪ No label detected for {len(no_suggestion_issues)} issues:")
            for issue in no_suggestion_issues[:5]:
                print(f"  • {issue['key']}: {issue['summary'][:60]}...")
            if len(no_suggestion_issues) > 5:
                print(f"  ... and {len(no_suggestion_issues) - 5} more")

        # Ask for confirmation
        print("\n🤔 What would you like to do?")
        print("1. Apply suggested labels automatically")
        print("2. Review and modify suggestions")
        print("3. Cancel")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            # Apply automatically
            self._apply_suggested_labels(issues_to_update)
        elif choice == "2":
            # Review mode
            self._review_and_apply_labels(issues_to_update)
        else:
            print("❌ Update cancelled")
            return

    def _detect_label_from_title(self, title):
        """Detect appropriate label from task title"""
        title_lower = title.lower()

        # Check for [BE] or backend indicators
        if '[be]' in title_lower or '[backend]' in title_lower:
            return 'Backend'

        # Check for [FE] or frontend indicators
        if '[fe]' in title_lower or '[frontend]' in title_lower:
            return 'Frontend'

        # Additional patterns can be added here
        # For example: API, database, UI, etc.

        return None

    def _apply_suggested_labels(self, issues_to_update):
        """Apply suggested labels to issues"""
        print(f"\n🔄 Applying labels to issues...")

        success_count = 0
        error_count = 0
        skipped_count = 0

        for issue in issues_to_update:
            if issue['suggested_label']:
                try:
                    self._update_issue_labels(
                        issue['key'],
                        [issue['suggested_label']],
                        [],
                        issue['current_labels']
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error updating {issue['key']}: {e}")
                    error_count += 1
            else:
                skipped_count += 1
                print(f"⏭️  Skipped {issue['key']} (no label detected)")

        print(f"\n📊 Update summary:")
        print(f"  ✅ Successfully updated: {success_count}")
        print(f"  ⏭️  Skipped (no detection): {skipped_count}")
        print(f"  ❌ Errors: {error_count}")

    def _review_and_apply_labels(self, issues_to_update):
        """Review and modify label suggestions before applying"""
        print(f"\n📝 Review mode - modify suggestions as needed")
        print("Options: b=Backend, f=Frontend, s=Skip, q=Quit\n")

        updated_issues = []

        for i, issue in enumerate(issues_to_update, 1):
            print(f"\n[{i}/{len(issues_to_update)}] {issue['key']}: {issue['summary']}")
            print(f"Current labels: {', '.join(issue['current_labels']) if issue['current_labels'] else '(none)'}")
            print(f"Suggested: {issue['suggested_label'] or '(no suggestion)'}")

            while True:
                choice = input("Action (b/f/s/q): ").strip().lower()

                if choice == 'b':
                    issue['suggested_label'] = 'Backend'
                    updated_issues.append(issue)
                    break
                elif choice == 'f':
                    issue['suggested_label'] = 'Frontend'
                    updated_issues.append(issue)
                    break
                elif choice == 's':
                    print("⏭️  Skipped")
                    break
                elif choice == 'q':
                    print("❌ Review cancelled")
                    return
                else:
                    print("Invalid option. Use: b=Backend, f=Frontend, s=Skip, q=Quit")

        if updated_issues:
            print(f"\n✅ Ready to update {len(updated_issues)} issues")
            confirm = input("Apply changes? (y/N): ").strip().lower()

            if confirm == 'y':
                self._apply_suggested_labels(updated_issues)
            else:
                print("❌ Update cancelled")

    def _get_labels_from_user(self):
        """Get labels from user"""
        print(f"\n🏷️  Label configuration:")
        
        # Labels to add
        print("Enter labels to ADD (comma-separated, or press Enter to skip):")
        add_input = input("Labels to add: ").strip()
        labels_to_add = [label.strip() for label in add_input.split(',') if label.strip()] if add_input else []
        
        # Labels to remove
        print("Enter labels to REMOVE (comma-separated, or press Enter to skip):")
        remove_input = input("Labels to remove: ").strip()
        labels_to_remove = [label.strip() for label in remove_input.split(',') if label.strip()] if remove_input else []
        
        # Summary
        print(f"\n📋 Summary of changes:")
        if labels_to_add:
            print(f"  ➕ Labels to add: {', '.join(labels_to_add)}")
        if labels_to_remove:
            print(f"  ➖ Labels to remove: {', '.join(labels_to_remove)}")
        
        if not labels_to_add and not labels_to_remove:
            print("  ⚠️  No changes specified")
            return [], []
        
        return labels_to_add, labels_to_remove

    def _update_issue_labels(self, issue_key, labels_to_add, labels_to_remove, current_labels):
        """Update labels for single issue"""
        try:
            # Calculate new labels
            new_labels = set(current_labels)

            # Add new labels
            for label in labels_to_add:
                new_labels.add(label)

            # Remove labels
            for label in labels_to_remove:
                new_labels.discard(label)

            # Convert to list
            new_labels_list = list(new_labels)

            # Update issue using JiraClient method
            success = self.jira_client.update_issue_labels(issue_key, new_labels_list)

            if success:
                print(f"✅ Updated labels for {issue_key}")
                print(f"   New labels: {', '.join(new_labels_list) if new_labels_list else '(no labels)'}")
            else:
                print(f"❌ Failed to update {issue_key}")

        except Exception as e:
            logger.error(f"Error updating labels for {issue_key}: {e}")
            print(f"❌ Error updating {issue_key}: {e}")

    def _bulk_update_labels(self, issues, labels_to_add, labels_to_remove):
        """Bulk update labels for multiple issues"""
        print(f"\n🔄 Updating labels for {len(issues)} issues...")
        
        success_count = 0
        error_count = 0
        
        for i, issue in enumerate(issues, 1):
            issue_key = issue.get('key', '')
            current_labels = issue.get('fields', {}).get('labels', [])
            
            print(f"  Updating {i}/{len(issues)}: {issue_key}")
            
            try:
                self._update_issue_labels(issue_key, labels_to_add, labels_to_remove, current_labels)
                success_count += 1
            except Exception as e:
                logger.error(f"Error updating {issue_key}: {e}")
                error_count += 1
        
        print(f"\n📊 Update summary:")
        print(f"  ✅ Successfully updated: {success_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  📋 Total processed: {len(issues)}")

def main():
    """Main function running the tool"""
    tool = LabelUpdaterTool()
    tool.safe_run()

if __name__ == "__main__":
    main()