"""
Sprint Completion Tool - Analysis of completed tasks in sprint
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import re
import pandas as pd
import logging
from datetime import datetime

# DEV: Add path to main project directory
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

class SprintCompletionTool(BaseScrumMasterTool):
    """Tool for analyzing completed tasks in sprint"""
    
    def __init__(self):
        super().__init__("Analysis of completed tasks in sprint")

    def run(self):
        """Main method running the analysis"""
        # Get project and sprint
        project_key = self.get_project_key()
        sprint_data = self.get_sprint_selection(project_key)
        
        sprint_name = sprint_data.get('name', 'No name')
        sprint_start = self._parse_sprint_date(sprint_data.get('startDate'))
        sprint_end = self._parse_sprint_date(sprint_data.get('endDate'))
        
        print(f"\n🎯 Analyzing completed tasks in sprint: {sprint_name}")
        if sprint_start and sprint_end:
            print(f"📅 Period: {sprint_start.strftime('%Y-%m-%d')} - {sprint_end.strftime('%Y-%m-%d')}")
        
        # Analyze completed tasks
        completed_tasks, incomplete_tasks = self._analyze_sprint_completion(project_key, sprint_name, sprint_start, sprint_end)

        # Generate reports
        self._generate_reports(project_key, sprint_name, completed_tasks, incomplete_tasks)

        # Print summary
        self._print_detailed_summary(completed_tasks, incomplete_tasks, project_key, sprint_name)

    def _parse_sprint_date(self, date_str):
        """Parse sprint date from Jira format with better cross-platform compatibility"""
        if not date_str:
            return None

        try:
            # Handle different Jira date formats
            # Format 1: '2025-07-11T12:18:02.309+0000' (most common)
            # Format 2: '2025-07-11T12:18:02.309Z'
            # Format 3: '2025-07-11T12:18:02+0000'

            # First, normalize the timezone format
            normalized_date = date_str

            # Replace 'Z' with '+00:00' for ISO format
            if normalized_date.endswith('Z'):
                normalized_date = normalized_date.replace('Z', '+00:00')

            # Replace '+0000' with '+00:00' for proper ISO format
            elif '+0000' in normalized_date:
                normalized_date = normalized_date.replace('+0000', '+00:00')

            # Replace '-0000' with '+00:00' for proper ISO format
            elif '-0000' in normalized_date:
                normalized_date = normalized_date.replace('-0000', '+00:00')

            # Try parsing with fromisoformat (Python 3.7+)
            return datetime.fromisoformat(normalized_date)

        except ValueError as e:
            # If fromisoformat fails, try manual parsing
            logger.warning(f"Failed to parse date '{date_str}' with fromisoformat: {e}")

            try:
                # Try parsing with strptime for common Jira formats
                # Remove timezone info and parse as UTC, then add timezone
                import re
                from datetime import timezone

                # Extract the datetime part without timezone
                # Pattern: YYYY-MM-DDTHH:MM:SS.sss
                match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{3}))?([+-]\d{4}|Z)?', date_str)

                if match:
                    datetime_part = match.group(1)
                    milliseconds = match.group(2) or '000'
                    timezone_part = match.group(3) or '+0000'

                    # Parse the datetime part
                    dt = datetime.strptime(datetime_part, '%Y-%m-%dT%H:%M:%S')

                    # Add milliseconds
                    dt = dt.replace(microsecond=int(milliseconds) * 1000)

                    # Add timezone (assume UTC for Jira dates)
                    dt = dt.replace(tzinfo=timezone.utc)

                    return dt

            except Exception as e2:
                logger.warning(f"Failed to parse date '{date_str}' with manual parsing: {e2}")

        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")

        return None

    def _analyze_sprint_completion(self, project_key, sprint_name, sprint_start, sprint_end):
        """Analyze completed tasks in sprint"""
        
        # Build JQL for sprint issues
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Bug, Task, Sub-bug, Sub-task)
        ORDER BY key ASC
        """
        
        # Define fields to retrieve
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'created', 'updated',
            'timeoriginalestimate', 'timespent', CUSTOM_FIELDS['responsible'], 'labels', 'components'
        ]

        print(f"🚀 Fetching tasks from sprint...")
        print(f"JQL: {jql.strip()}")

        # Execute query to get all issues with changelog
        all_issues = self.jira_client.get_all_results(jql, fields, expand=['changelog'])

        if not all_issues:
            print(f"❌ No tasks found in sprint '{sprint_name}'")
            return []

        print(f"✅ Fetched {len(all_issues)} tasks from sprint")
        print("🔍 Analyzing completed tasks...")

        completed_tasks = []
        incomplete_tasks = []

        for i, issue in enumerate(all_issues, 1):
            issue_key = issue.get('key', '')
            print(f"   Analyzing {i}/{len(all_issues)}: {issue_key}")

            # Check if task was completed during sprint
            completion_result = self._was_completed_during_sprint(issue, sprint_start, sprint_end)
            if completion_result['completed']:
                task_data = self._extract_task_data(issue, sprint_start, sprint_end)
                completed_tasks.append(task_data)
            else:
                # Add to incomplete tasks with reason
                incomplete_data = self._extract_task_data(issue, sprint_start, sprint_end)
                incomplete_data['Reason Not Completed'] = completion_result['reason']
                incomplete_tasks.append(incomplete_data)

        print(f"✅ Found {len(completed_tasks)} tasks completed during sprint")
        print(f"⚠️  Found {len(incomplete_tasks)} tasks not completed during sprint")
        return completed_tasks, incomplete_tasks

    def _was_completed_during_sprint(self, issue, sprint_start, sprint_end):
        """Check if task was completed during sprint period based on status transitions"""
        fields = issue.get('fields', {})
        changelog = issue.get('changelog', {})

        # If we don't have sprint dates, can't determine completion
        if not sprint_start or not sprint_end:
            return {'completed': False, 'reason': 'No sprint dates available'}

        # If no changelog, can't analyze transitions
        if not changelog or not changelog.get('histories'):
            return {'completed': False, 'reason': 'No changelog available for analysis'}

        # Track all transitions to "Code Review" during sprint from valid statuses
        valid_transitions_to_code_review = []

        # Analyze changelog for status transitions
        for history in changelog['histories']:
            # Parse history date
            history_date = self._parse_sprint_date(history.get('created'))
            if not history_date:
                continue

            # Check if change happened during sprint
            if not (sprint_start <= history_date <= sprint_end):
                continue

            # Look for status changes in this history entry
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    from_status = item.get('fromString', '').lower()
                    to_status = item.get('toString', '').lower()

                    # Check for transitions to "Code Review" from valid statuses
                    # Valid transitions: In Progress -> Code Review OR To Do -> Code Review OR Backlog -> Code Review
                    if (to_status == 'code review' and
                        from_status in ['in progress', 'to do', 'backlog']):
                        valid_transitions_to_code_review.append({
                            'date': history_date,
                            'from': from_status,
                            'to': to_status
                        })

        # If no valid transitions to Code Review during sprint, not completed
        if not valid_transitions_to_code_review:
            return {'completed': False, 'reason': 'No transition from In Progress/To Do/Backlog to Code Review during sprint'}

        # Check if the first valid transition to Code Review was during this sprint
        # This handles the case where task might have been moved back and forth
        first_transition = min(valid_transitions_to_code_review, key=lambda x: x['date'])

        # Additional validation for In Progress transitions only (original logic)
        # Check if task started in this sprint for In Progress -> Code Review transitions
        if first_transition['from'] == 'in progress':
            completed_statuses_lower = [
                'done', 'qa testing', 'ready for staging', 'qa staging',
                'ready for production', 'on production', 'code review'
            ]

            started_in_sprint = False
            for history in changelog['histories']:
                history_date = self._parse_sprint_date(history.get('created'))
                if not history_date or not (sprint_start <= history_date <= sprint_end):
                    continue

                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        from_status = item.get('fromString', '').lower()
                        to_status = item.get('toString', '').lower()

                        # Task started in sprint if it moved TO "In Progress" from non-completed status
                        if (to_status == 'in progress' and
                            from_status not in completed_statuses_lower and
                            from_status != 'in progress'):
                            started_in_sprint = True
                            break

            # For In Progress -> Code Review, task must have started in sprint
            if not started_in_sprint:
                return {'completed': False, 'reason': 'Task did not start in this sprint (no transition to In Progress from non-completed status)'}

        # For To Do -> Code Review or Backlog -> Code Review, no additional validation needed
        # Task is completed if it has any of the valid transitions during sprint
        return {'completed': True, 'reason': f'Completed during sprint (transition from {first_transition["from"]} to {first_transition["to"]})'}

    def _extract_task_data(self, issue, sprint_start, sprint_end):
        """Extract relevant data from issue"""
        fields = issue.get('fields', {})
        changelog = issue.get('changelog', {})

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

        # Determine owner (responsible or from changelog)
        owner = self._determine_owner(responsible_name, assignee_name, status, changelog, sprint_start, sprint_end)

        # Time tracking
        original_estimate = fields.get('timeoriginalestimate', 0) or 0
        time_spent = fields.get('timespent', 0) or 0

        # Convert seconds to hours
        original_estimate_hours = original_estimate / 3600 if original_estimate else 0
        time_spent_hours = time_spent / 3600 if time_spent else 0

        # Labels and category
        labels = fields.get('labels', [])
        components = fields.get('components', [])
        category = self._get_category_from_labels_and_components(labels, components)

        # Dates
        created = fields.get('created', '')
        updated = fields.get('updated', '')

        return {
            'Issue Key': issue_key,
            'Summary': summary,
            'Status': status,
            'Issue Type': issue_type,
            'Assignee': assignee_name,
            'Responsible': responsible_name,
            'Owner': owner,
            'Original Estimate (hours)': round(original_estimate_hours, 2),
            'Time Spent (hours)': round(time_spent_hours, 2),
            'Category': category,
            'Labels': ', '.join(labels),
            'Created': created,
            'Updated': updated
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



    def _generate_reports(self, project_key, sprint_name, completed_tasks, incomplete_tasks):
        """Generate CSV reports for completed and incomplete tasks"""
        if not completed_tasks and not incomplete_tasks:
            print("⚠️  No tasks to export")
            return

        print(f"\n📁 FILE EXPORT:")

        # Export completed tasks
        if completed_tasks:
            df_completed = pd.DataFrame(completed_tasks)
            csv_filename_completed = self.generate_output_filename("sprint_completion", project_key, sprint_name, "csv")
            csv_path_completed = self.get_output_path("reports", csv_filename_completed)
            df_completed.to_csv(csv_path_completed, index=False, encoding='utf-8-sig')
            print(f"   📊 Completed Tasks CSV: {csv_path_completed}")

        # Export incomplete tasks
        if incomplete_tasks:
            df_incomplete = pd.DataFrame(incomplete_tasks)
            csv_filename_incomplete = self.generate_output_filename("sprint_incomplete", project_key, sprint_name, "csv")
            csv_path_incomplete = self.get_output_path("reports", csv_filename_incomplete)
            df_incomplete.to_csv(csv_path_incomplete, index=False, encoding='utf-8-sig')
            print(f"   ⚠️  Incomplete Tasks CSV: {csv_path_incomplete}")

    def _print_detailed_summary(self, completed_tasks, incomplete_tasks, project_key, sprint_name):
        """Print detailed summary of completed tasks"""
        if not completed_tasks:
            print(f"\n📊 No completed tasks found in sprint")
            return

        # Create DataFrame for analysis
        df = pd.DataFrame(completed_tasks)
        
        # Calculate totals
        total_tasks = len(completed_tasks)
        total_estimate = df['Original Estimate (hours)'].sum()
        total_spent = df['Time Spent (hours)'].sum()
        
        print(f"\n📊 DETAILED SUMMARY:")
        print(f"   • Project: {project_key}")
        print(f"   • Sprint: {sprint_name}")
        print(f"   • Completed tasks: {total_tasks}")
        print(f"   • Total Original estimated (done tasks): {total_estimate:.1f}h")
        print(f"   • Total Work log time: {total_spent:.1f}h")
        
        # Efficiency ratio
        if total_spent > 0:
            efficiency = (total_estimate / total_spent) * 100
            print(f"   • Efficiency: {efficiency:.1f}% (estimated/spent)")

        # Print summaries for Tasks/Sub-tasks only
        self._print_task_summaries(df, "only tasks", task_types_filter=['Task', 'Sub-task'])

        # Print summaries for all issue types (Total)
        self._print_task_summaries(df, "Total", task_types_filter=None)

    def _print_task_summaries(self, df, section_name, task_types_filter=None):
        """Print summary sections with optional filtering by task types"""

        # Filter DataFrame if needed
        if task_types_filter:
            filtered_df = df[df['Issue Type'].isin(task_types_filter)]
            if filtered_df.empty:
                print(f"\n   📈 Summary by category ({section_name}): No {section_name.lower()} found")
                return
        else:
            filtered_df = df

        # Summary by category
        print(f"\n   📈 Summary by category ({section_name}):")
        category_stats = filtered_df.groupby('Category').agg({
            'Issue Key': 'count',
            'Original Estimate (hours)': 'sum',
            'Time Spent (hours)': 'sum'
        }).round(1)

        for category, stats in category_stats.iterrows():
            task_count = int(stats['Issue Key'])  # Convert to int to remove decimal places
            original_estimate = stats['Original Estimate (hours)']
            time_spent = stats['Time Spent (hours)']
            efficiency = (original_estimate / time_spent * 100) if time_spent > 0 else 0
            print(f"     • {category}: {task_count} tasks, {original_estimate}h Original Estimate, {time_spent}h Work log time, {efficiency:.1f}% efficiency")

        # Add Total row for Summary by category
        total_tasks = len(filtered_df)
        total_original_estimate = filtered_df['Original Estimate (hours)'].sum()
        total_time_spent = filtered_df['Time Spent (hours)'].sum()
        total_efficiency = (total_original_estimate / total_time_spent * 100) if total_time_spent > 0 else 0
        print(f"     • Total: {total_tasks} tasks, {total_original_estimate:.1f}h Original Estimate, {total_time_spent:.1f}h Work log time, {total_efficiency:.1f}% efficiency")

        # Summary by Responsible
        print(f"\n   👤 Summary by Responsible ({section_name}):")
        owner_stats = filtered_df.groupby('Owner').agg({
            'Issue Key': 'count',
            'Original Estimate (hours)': 'sum',
            'Time Spent (hours)': 'sum'
        }).round(1)

        # Sort by total estimate descending and filter out Unassigned
        owner_stats = owner_stats[owner_stats.index != 'Unassigned']
        owner_stats = owner_stats.sort_values('Original Estimate (hours)', ascending=False)

        for owner, stats in owner_stats.iterrows():
            task_count = int(stats['Issue Key'])  # Convert to int to remove decimal places
            original_estimate = stats['Original Estimate (hours)']
            time_spent = stats['Time Spent (hours)']
            efficiency = (original_estimate / time_spent * 100) if time_spent > 0 else 0
            print(f"     • {owner}: {task_count} tasks, {original_estimate}h Original estimated (done tasks), {time_spent}h Work log time, {efficiency:.1f}% efficiency")

def main():
    """Main function running the tool"""
    tool = SprintCompletionTool()
    tool.safe_run()

if __name__ == "__main__":
    main()