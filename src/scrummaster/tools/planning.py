"""
Planning Tool - Analysis of sprint planning quality
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import pandas as pd
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

class PlanningTool(BaseScrumMasterTool):
    """Tool for analyzing sprint planning quality"""
    
    def __init__(self):
        super().__init__("Analysis of sprint planning quality")

    def run(self):
        """Main method running the analysis"""
        # Get project and sprint
        project_key = self.get_project_key()
        sprint_data = self.get_sprint_selection(project_key)
        
        sprint_name = sprint_data.get('name', 'No name')
        sprint_start = self._parse_sprint_date(sprint_data.get('startDate'))
        sprint_end = self._parse_sprint_date(sprint_data.get('endDate'))
        
        print(f"\n📋 Analyzing sprint planning: {sprint_name}")
        if sprint_start and sprint_end:
            print(f"📅 Period: {sprint_start.strftime('%Y-%m-%d')} - {sprint_end.strftime('%Y-%m-%d')}")
        
        # Analyze planning
        planning_data = self._analyze_sprint_planning(project_key, sprint_name, sprint_start, sprint_end)
        
        # Generate reports
        self._generate_reports(project_key, sprint_name, planning_data)
        
        # Print summary
        self._print_detailed_summary(planning_data, project_key, sprint_name)

    def _parse_sprint_date(self, date_str):
        """Parse sprint date from Jira format"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    def _analyze_sprint_planning(self, project_key, sprint_name, sprint_start, sprint_end):
        """Analyze sprint planning quality"""
        
        # Build JQL for sprint issues
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        AND status in ("To Do", "In Progress", "On hold", "Backlog")
        ORDER BY key ASC
        """
        
        # Define fields to retrieve
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'created', 'updated',
            'timeoriginalestimate', 'timespent', 'timeestimate', CUSTOM_FIELDS['responsible'], 'labels', 'components'
        ]

        print(f"🚀 Fetching tasks from sprint...")
        print(f"JQL: {jql.strip()}")

        # Execute query to get all issues with changelog
        all_issues = self.jira_client.get_all_results(jql, fields, expand=['changelog'])

        if not all_issues:
            print(f"❌ No tasks found in sprint '{sprint_name}'")
            return []

        print(f"✅ Fetched {len(all_issues)} tasks from sprint")
        print("📋 Analyzing planning data...")

        planning_data = []
        
        for i, issue in enumerate(all_issues, 1):
            issue_key = issue.get('key', '')
            print(f"   Analyzing {i}/{len(all_issues)}: {issue_key}")
            
            # Extract planning data
            task_data = self._extract_planning_data(issue, sprint_start, sprint_end)
            planning_data.append(task_data)

        print(f"✅ Analyzed {len(planning_data)} tasks")
        return planning_data

    def _extract_planning_data(self, issue, sprint_start, sprint_end):
        """Extract planning-related data from task"""
        fields = issue.get('fields', {})
        
        # Basic info
        issue_key = issue.get('key', '')
        summary = fields.get('summary', '')
        status = fields.get('status', {}).get('name', '')
        issue_type = fields.get('issuetype', {}).get('name', '')
        
        # People
        assignee = fields.get('assignee')
        assignee_name = assignee.get('displayName', '') if assignee else ''
        
        responsible = fields.get(CUSTOM_FIELDS['responsible'])
        responsible_name = responsible.get('displayName', '') if responsible else ''
        
        # Time tracking
        original_estimate = fields.get('timeoriginalestimate', 0) or 0
        remaining_estimate = fields.get('timeestimate', 0) or 0
        time_spent = fields.get('timespent', 0) or 0
        
        # Convert seconds to hours
        original_estimate_hours = original_estimate / 3600 if original_estimate else 0
        remaining_estimate_hours = remaining_estimate / 3600 if remaining_estimate else 0
        time_spent_hours = time_spent / 3600 if time_spent else 0
        
        # Labels and category
        labels = fields.get('labels', [])
        components = fields.get('components', [])
        category = self._get_category_from_labels_and_components(labels, components)
        
        # Planning issues assessment (without quality scoring)
        planning_issues = self._assess_planning_issues(
            original_estimate_hours, remaining_estimate_hours, time_spent_hours,
            assignee_name, responsible_name, labels, components, status
        )

        # Determine owner (responsible or from changelog)
        changelog = issue.get('changelog', {})
        owner = self._determine_owner(responsible_name, assignee_name, status, changelog, sprint_start, sprint_end)

        return {
            'Issue Key': issue_key,
            'Summary': summary,
            'Status': status,
            'Issue Type': issue_type,
            'Assignee': assignee_name,
            'Responsible': responsible_name,
            'Owner': owner,
            'Original Estimate (hours)': round(original_estimate_hours, 2),
            'Remaining Estimate (hours)': round(remaining_estimate_hours, 2),
            'Time Spent (hours)': round(time_spent_hours, 2),
            'Category': category,
            'Labels': ', '.join(labels),
            'Planning Issues': ', '.join(planning_issues)
        }

    def _determine_owner(self, responsible_name, assignee_name, status, changelog, sprint_start, sprint_end):
        """Determine task owner based on responsible field or changelog analysis"""
        # If responsible field is filled, use it
        if responsible_name:
            return responsible_name

        # If no responsible, analyze changelog for status changes to "In Progress" during sprint
        if changelog and changelog.get('histories'):
            # Look for the first person who changed status to "In Progress" during sprint
            for history in changelog['histories']:
                # Parse history date
                history_date = self._parse_sprint_date(history.get('created'))
                if not history_date:
                    continue

                # Check if change happened during sprint
                if sprint_start and sprint_end:
                    if not (sprint_start <= history_date <= sprint_end):
                        continue

                # Check if this history entry contains status change to "In Progress"
                for item in history.get('items', []):
                    if (item.get('field') == 'status' and
                        item.get('toString', '').lower() == 'in progress'):
                        # Get the author of this change
                        author = history.get('author', {})
                        if author and author.get('displayName'):
                            return author.get('displayName')

        # If no status change to "In Progress" found, check current assignee for In Progress tasks
        if status.lower() == 'in progress' and assignee_name:
            return assignee_name

        # Otherwise, no clear owner
        return 'Unassigned'

    def _assess_planning_issues(self, original_est, remaining_est, time_spent, assignee, responsible, labels, components, status):
        """Assess planning issues"""
        issues = []

        # Missing estimates
        if original_est == 0:
            issues.append('No original estimate')

        # Missing responsible person
        if not responsible:
            issues.append('No responsible person')

        # Missing assignee for active tasks
        if status.lower() in ['in progress', 'in review', 'testing'] and not assignee:
            issues.append('Active task without assignee')

        # Missing technology labels or components
        has_tech_component = False
        has_tech_label = False

        # Check components first
        if components:
            component_names = [comp.get('name', '') for comp in components if isinstance(comp, dict)]
            has_tech_component = any(name in ['Backend', 'Frontend', 'Fullstack', 'DevOps', 'QA'] for name in component_names)

        # If no tech components, check labels
        if not has_tech_component and labels:
            has_tech_label = any(label in ['Backend', 'Frontend', 'Fullstack', 'DevOps', 'QA'] for label in labels)

        # Report issue if neither components nor labels indicate technology
        if not has_tech_component and not has_tech_label:
            issues.append('Missing technology labels or components')

        # Remaining estimate issues
        if status.lower() in ['done', 'closed', 'resolved'] and remaining_est > 0:
            issues.append('Completed task with remaining estimate')

        return issues





    def _generate_reports(self, project_key, sprint_name, planning_data):
        """Generate CSV report"""
        if not planning_data:
            print("⚠️  No planning data to export")
            return

        # Create DataFrame
        df = pd.DataFrame(planning_data)

        # Generate filename
        csv_filename = self.generate_output_filename("planning_analysis", project_key, sprint_name, "csv")

        # Get full path
        csv_path = self.get_output_path("reports", csv_filename)

        # Save CSV
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        print(f"\n📁 FILE EXPORT:")
        print(f"   📊 CSV Report: {csv_path}")

    def _print_detailed_summary(self, planning_data, project_key, sprint_name):
        """Print detailed summary of planning analysis"""
        if not planning_data:
            print(f"\n📊 No planning data found")
            return

        # Create DataFrame for analysis
        df = pd.DataFrame(planning_data)
        
        # Calculate totals
        total_tasks = len(planning_data)
        total_estimate = df['Original Estimate (hours)'].sum()
        total_remaining = df['Remaining Estimate (hours)'].sum()

        print(f"\n📊 DETAILED SUMMARY:")
        print(f"   • Project: {project_key}")
        print(f"   • Sprint: {sprint_name}")
        print(f"   • Total tasks: {total_tasks}")
        print(f"   • Total estimate: {total_estimate:.1f}h")
        print(f"   • Remaining time: {total_remaining:.1f}h")
        
        # Summary by category
        print(f"\n   📈 Summary by category:")
        category_stats = df.groupby('Category').agg({
            'Issue Key': 'count',
            'Original Estimate (hours)': 'sum',
            'Remaining Estimate (hours)': 'sum'
        }).round(1)
        
        for category, stats in category_stats.iterrows():
            print(f"     • {category}: {stats['Issue Key']} tasks, {stats['Original Estimate (hours)']}h estimate, {stats['Remaining Estimate (hours)']}h remaining")

        # Summary by owner (responsible or assignee for In Progress)
        print(f"\n   👤 Summary by owner:")
        owner_stats = df.groupby('Owner').agg({
            'Issue Key': 'count',
            'Original Estimate (hours)': 'sum',
            'Remaining Estimate (hours)': 'sum'
        }).round(1)

        # Sort by total estimate descending
        owner_stats = owner_stats.sort_values('Original Estimate (hours)', ascending=False)

        for owner, stats in owner_stats.iterrows():
            print(f"     • {owner}: {stats['Issue Key']} tasks, {stats['Original Estimate (hours)']}h estimate, {stats['Remaining Estimate (hours)']}h remaining")
        
        # Most common planning issues
        print(f"\n   ⚠️  Most common planning issues:")
        all_issues = []
        for issues_str in df['Planning Issues']:
            if issues_str:
                all_issues.extend(issues_str.split(', '))
        
        if all_issues:
            issue_counts = pd.Series(all_issues).value_counts().head(5)
            for issue, count in issue_counts.items():
                print(f"     • {issue}: {count} tasks")
        else:
            print("     • No planning issues found!")

def main():
    """Main function running the tool"""
    tool = PlanningTool()
    tool.safe_run()

if __name__ == "__main__":
    main()