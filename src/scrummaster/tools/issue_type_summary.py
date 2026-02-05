"""
Issue Type Summary Tool - Summary of time spent by issue type
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import pandas as pd
import json
import logging
from datetime import datetime
from collections import defaultdict

# Add path to main project directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Handle imports for different execution methods
try:
    # Try relative imports (when run as module)
    from ..core.base_tool import BaseScrumMasterTool
except ImportError:
    # Fallback to absolute imports (when run directly)
    from src.scrummaster.core.base_tool import BaseScrumMasterTool

from config.jira_config import CUSTOM_FIELDS, OUTPUT_PATHS

logger = logging.getLogger(__name__)

class IssueTypeSummaryTool(BaseScrumMasterTool):
    """Tool for summarizing time spent by issue type"""
    
    def __init__(self):
        super().__init__("Summary of time spent by issue type")

    def get_sprint_selection_with_all(self, project_key):
        """Get sprint selection from user with ALL option"""
        print(f"\n📅 Fetching sprints for project {project_key}...")
        
        try:
            sprints = self.jira_client.get_project_sprints(project_key)
        except Exception as e:
            raise ValueError(f"Cannot fetch sprints: {str(e)}")

        if not sprints:
            raise ValueError(f"No sprints found for project {project_key}")

        # Sort sprints by end date (oldest first, newest at bottom for better readability)
        sprints.sort(key=lambda x: x.get('endDate', ''), reverse=False)

        print(f"✅ Found {len(sprints)} sprints:")
        print()

        # Display ALL option first
        print(f"   {'ALL':>3}. 🌐 ALL SPRINTS (analyze all sprints)")
        print()

        # Display sprints with status indicators
        for i, sprint in enumerate(sprints, 1):
            sprint_name = sprint.get('name', 'No name')
            sprint_state = sprint.get('state', 'UNKNOWN')
            
            # Status indicators
            status_icon = {
                'ACTIVE': '🟢',
                'CLOSED': '🔵', 
                'FUTURE': '⚪'
            }.get(sprint_state, '❓')
            
            print(f"   {i:2d}. {status_icon} {sprint_name} ({sprint_state})")

        print()
        
        while True:
            try:
                choice = input("📝 Choose sprint number or 'ALL': ").strip().upper()
                
                if choice == 'ALL':
                    print(f"✅ Selected: ALL SPRINTS")
                    return 'ALL', sprints
                
                sprint_index = int(choice) - 1
                
                if 0 <= sprint_index < len(sprints):
                    selected_sprint = sprints[sprint_index]
                    sprint_name = selected_sprint.get('name', 'No name')
                    print(f"✅ Selected sprint: {sprint_name}")
                    return selected_sprint, None
                else:
                    print(f"❌ Error: Choose number from 1 to {len(sprints)} or 'ALL'")
            except ValueError:
                print("❌ Error: Enter valid number or 'ALL'")

    def run(self):
        """Main method running the analysis"""
        # Get project
        project_key = self.get_project_key()

        # Get sprint selection with ALL option
        sprint_selection, all_sprints = self.get_sprint_selection_with_all(project_key)

        # Get issues to exclude using new exclusions system
        excluded_issues = self.get_project_exclusions(project_key)

        if sprint_selection == 'ALL':
            # Analyze all sprints - get unique issues across all sprints
            print(f"\n📊 Analyzing time spent by issue type across ALL sprints")
            print(f"ℹ️ Found {len(all_sprints)} sprints to analyze")

            # Get all unique issues from ALL sprints
            issue_type_data = self._analyze_issue_types_all_sprints(project_key, all_sprints, excluded_issues)

            # Generate reports for all sprints
            self._generate_reports(project_key, "ALL_SPRINTS", issue_type_data)

            # Print summary for all sprints
            self._print_summary(issue_type_data, project_key, "ALL SPRINTS")

        else:
            # Single sprint analysis (existing logic)
            sprint_data = sprint_selection
            sprint_name = sprint_data.get('name', 'No name')
            sprint_start = self._parse_sprint_date(sprint_data.get('startDate'))
            sprint_end = self._parse_sprint_date(sprint_data.get('endDate'))

            print(f"\n📊 Analyzing time spent by issue type in sprint: {sprint_name}")
            if sprint_start and sprint_end:
                print(f"📅 Period: {sprint_start.strftime('%Y-%m-%d')} - {sprint_end.strftime('%Y-%m-%d')}")

            # Analyze time by issue type
            issue_type_data = self._analyze_issue_types(project_key, sprint_name, sprint_start, sprint_end, excluded_issues)

            # Generate reports
            self._generate_reports(project_key, sprint_name, issue_type_data)

            # Generate detailed issues report for verification
            self._generate_detailed_issues_report(project_key, sprint_name, issue_type_data)

            # Print summary
            self._print_summary(issue_type_data, project_key, sprint_name)

    def _parse_sprint_date(self, date_str):
        """Parse sprint date from Jira format"""
        if not date_str:
            return None
        try:
            # Handle Jira date format: 2025-07-09T00:00:00.000+0000
            if date_str.endswith('+0000'):
                date_str = date_str[:-5] + '+00:00'
            elif date_str.endswith('-0000'):
                date_str = date_str[:-5] + '+00:00'
            elif 'Z' in date_str:
                date_str = date_str.replace('Z', '+00:00')

            return datetime.fromisoformat(date_str)
        except ValueError:
            # Fallback: try parsing without timezone
            try:
                # Remove timezone info completely
                date_part = date_str.split('+')[0].split('Z')[0]
                # Remove milliseconds if present
                if '.' in date_part:
                    date_part = date_part.split('.')[0]
                return datetime.fromisoformat(date_part)
            except:
                logger.warning(f"Could not parse sprint date: {date_str}")
                return None

    def _was_worked_during_sprint(self, issue, sprint_start, sprint_end):
        """Check if task was worked on during sprint period based on status transitions"""
        fields = issue.get('fields', {})
        changelog = issue.get('changelog', {})

        # If we don't have sprint dates, can't determine completion
        if not sprint_start or not sprint_end:
            return {'worked': False, 'reason': 'No sprint dates available'}

        # If no changelog, can't analyze transitions
        if not changelog or not changelog.get('histories'):
            return {'worked': False, 'reason': 'No changelog available for analysis'}

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

        # If no valid transitions to Code Review during sprint, not worked
        if not valid_transitions_to_code_review:
            return {'worked': False, 'reason': 'No transition from In Progress/To Do/Backlog to Code Review during sprint'}

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
                return {'worked': False, 'reason': 'Task did not start in this sprint (no transition to In Progress from non-completed status)'}

        # For To Do -> Code Review or Backlog -> Code Review, no additional validation needed
        # Task is worked if it has any of the valid transitions during sprint
        return {'worked': True, 'reason': f'Worked during sprint (transition from {first_transition["from"]} to {first_transition["to"]})'}

    def _analyze_issue_types_all_sprints(self, project_key, all_sprints, excluded_issues=None):
        """Analyze time spent by issue type across all sprints"""

        # Build JQL to get issues from all sprints
        sprint_names = [sprint.get('name', '') for sprint in all_sprints if sprint.get('name')]
        sprint_filter = " OR ".join([f'sprint = "{name}"' for name in sprint_names])

        jql = f"""
        project = "{project_key}"
        AND ({sprint_filter})
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        AND status NOT IN ("CANCELLED", "CANCELED")
        ORDER BY key ASC
        """

        # Define fields to retrieve
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'created', 'updated',
            'timeoriginalestimate', 'timespent', 'timeestimate', CUSTOM_FIELDS['responsible'],
            'labels', 'parent'
        ]

        print(f"🚀 Fetching all tasks from project...")

        # Execute query to get all issues
        all_issues = self.jira_client.get_all_results(jql, fields)

        if not all_issues:
            print(f"❌ No tasks found")
            return []

        # Filter out excluded issues
        if excluded_issues:
            original_count = len(all_issues)
            all_issues = [issue for issue in all_issues if issue.get('key') not in excluded_issues]
            excluded_count = original_count - len(all_issues)
            if excluded_count > 0:
                print(f"❌ Excluded {excluded_count} issues from analysis")

        print(f"✅ Fetched {len(all_issues)} unique tasks from project")

        # Dictionary to store aggregated data by issue type
        issue_type_summary = defaultdict(lambda: {
            'count': 0,
            'total_time_spent': 0,
            'total_original_estimate': 0,
            'total_remaining_estimate': 0,
            'issues': []
        })

        # Process each issue
        for issue in all_issues:
            issue_data = self._extract_issue_data(issue)
            issue_type = issue_data['issue_type']

            # Aggregate data
            issue_type_summary[issue_type]['count'] += 1
            issue_type_summary[issue_type]['total_time_spent'] += issue_data['time_spent_seconds']
            issue_type_summary[issue_type]['total_original_estimate'] += issue_data['original_estimate_seconds']
            issue_type_summary[issue_type]['total_remaining_estimate'] += issue_data['remaining_estimate_seconds']
            issue_type_summary[issue_type]['issues'].append(issue_data)

        # Convert to list format for easier processing
        summary_data = []
        for issue_type, data in issue_type_summary.items():
            summary_data.append({
                'issue_type': issue_type,
                'count': data['count'],
                'total_time_spent_hours': round(data['total_time_spent'] / 3600, 2),
                'total_original_estimate_hours': round(data['total_original_estimate'] / 3600, 2),
                'total_remaining_estimate_hours': round(data['total_remaining_estimate'] / 3600, 2),
                'average_time_spent_hours': round((data['total_time_spent'] / 3600) / data['count'], 2) if data['count'] > 0 else 0,
                'issues': data['issues']
            })

        return summary_data

    def _analyze_issue_types(self, project_key, sprint_name, sprint_start=None, sprint_end=None, excluded_issues=None):
        """Analyze time spent by issue type in a specific sprint

        Args:
            project_key: Jira project key
            sprint_name: Sprint name for filtering
            sprint_start: Sprint start date (unused but kept for API consistency)
            sprint_end: Sprint end date (unused but kept for API consistency)
        """
        # Note: sprint_start and sprint_end parameters are unused in this implementation
        # They are kept for consistency with other analysis tools
        _ = sprint_start, sprint_end  # Explicitly mark as unused
        
        # Build JQL for sprint issues
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        AND status NOT IN ("CANCELLED", "CANCELED")
        ORDER BY key ASC
        """
        
        # Define fields to retrieve
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'created', 'updated',
            'timeoriginalestimate', 'timespent', 'timeestimate', CUSTOM_FIELDS['responsible'], 
            'labels', 'parent'
        ]

        print(f"🚀 Fetching tasks from sprint...")

        # Execute query to get all issues
        all_issues = self.jira_client.get_all_results(jql, fields)

        if not all_issues:
            print(f"❌ No tasks found")
            return []

        # Filter out excluded issues
        if excluded_issues:
            original_count = len(all_issues)
            all_issues = [issue for issue in all_issues if issue.get('key') not in excluded_issues]
            excluded_count = original_count - len(all_issues)
            if excluded_count > 0:
                print(f"❌ Excluded {excluded_count} issues from analysis")

        print(f"✅ Processing {len(all_issues)} tasks from sprint")

        # Dictionary to store aggregated data by issue type
        issue_type_summary = defaultdict(lambda: {
            'count': 0,
            'total_time_spent': 0,
            'total_original_estimate': 0,
            'total_remaining_estimate': 0,
            'issues': []
        })
        
        # Process each issue
        for issue in all_issues:
            issue_data = self._extract_issue_data(issue)
            issue_type = issue_data['issue_type']
            
            # Aggregate data by issue type
            issue_type_summary[issue_type]['count'] += 1
            issue_type_summary[issue_type]['total_time_spent'] += issue_data['time_spent_seconds']
            issue_type_summary[issue_type]['total_original_estimate'] += issue_data['original_estimate_seconds']
            issue_type_summary[issue_type]['total_remaining_estimate'] += issue_data['remaining_estimate_seconds']
            issue_type_summary[issue_type]['issues'].append(issue_data)

        # Convert to list format for easier processing
        summary_data = []
        for issue_type, data in issue_type_summary.items():
            summary_data.append({
                'issue_type': issue_type,
                'count': data['count'],
                'total_time_spent_hours': round(data['total_time_spent'] / 3600, 2),
                'total_original_estimate_hours': round(data['total_original_estimate'] / 3600, 2),
                'total_remaining_estimate_hours': round(data['total_remaining_estimate'] / 3600, 2),
                'average_time_spent_hours': round((data['total_time_spent'] / 3600) / data['count'], 2) if data['count'] > 0 else 0,
                'issues': data['issues']
            })

        return summary_data

    def _extract_issue_data(self, issue):
        """Extract relevant data from issue"""
        fields = issue.get('fields', {})

        # Basic issue info
        issue_key = issue.get('key', '')
        summary = fields.get('summary', '')
        status = fields.get('status', {}).get('name', '')
        issue_type = fields.get('issuetype', {}).get('name', '')

        # Time tracking
        time_spent = fields.get('timespent', 0) or 0  # Time spent in seconds
        original_estimate = fields.get('timeoriginalestimate', 0) or 0  # Original estimate in seconds
        remaining_estimate = fields.get('timeestimate', 0) or 0  # Remaining estimate in seconds

        # Assignee and responsible
        assignee = fields.get('assignee')
        assignee_name = assignee.get('displayName', '') if assignee else ''
        
        responsible = fields.get(CUSTOM_FIELDS['responsible'])
        responsible_name = responsible.get('displayName', '') if responsible else ''

        # Parent issue (for subtasks)
        parent = fields.get('parent')
        parent_key = parent.get('key', '') if parent else ''

        # Labels
        labels = fields.get('labels', [])

        return {
            'issue_key': issue_key,
            'summary': summary,
            'status': status,
            'issue_type': issue_type,
            'time_spent_seconds': time_spent,
            'time_spent_hours': round(time_spent / 3600, 2) if time_spent else 0,
            'original_estimate_seconds': original_estimate,
            'original_estimate_hours': round(original_estimate / 3600, 2) if original_estimate else 0,
            'remaining_estimate_seconds': remaining_estimate,
            'remaining_estimate_hours': round(remaining_estimate / 3600, 2) if remaining_estimate else 0,
            'assignee': assignee_name,
            'responsible': responsible_name,
            'parent_key': parent_key,
            'labels': ', '.join(labels) if labels else ''
        }

    def _generate_reports(self, project_key, sprint_name, summary_data):
        """Generate CSV report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        base_filename = f"issue_type_summary_{project_key}_{sprint_name.replace(' ', '_')}_{timestamp}"

        # Prepare data for CSV - summary only
        csv_data = []
        for item in summary_data:
            # Extract issue keys from the issues list
            issue_keys = [issue['issue_key'] for issue in item.get('issues', [])]
            issue_keys_str = ', '.join(sorted(issue_keys))  # Sort for consistency

            csv_data.append({
                'Issue Type': item['issue_type'],
                'Count': item['count'],
                'Total Time Spent (hours)': item['total_time_spent_hours'],
                'Average Time Spent (hours)': item['average_time_spent_hours'],
                'Total Original Estimate (hours)': item['total_original_estimate_hours'],
                'Total Remaining Estimate (hours)': item['total_remaining_estimate_hours'],
                'Issue IDs': issue_keys_str
            })

        # Save CSV report
        csv_path = os.path.join(OUTPUT_PATHS['reports'], f"{base_filename}.csv")
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n📄 CSV report saved: {csv_path}")

    def _generate_detailed_issues_report(self, project_key, sprint_name, summary_data):
        """Generate detailed CSV report with all individual issues for verification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        base_filename = f"detailed_issues_{project_key}_{sprint_name.replace(' ', '_')}_{timestamp}"

        # Prepare detailed data for CSV - all individual issues
        detailed_csv_data = []

        for item in summary_data:
            issue_type = item['issue_type']
            for issue in item.get('issues', []):
                detailed_csv_data.append({
                    'Issue ID': issue['issue_key'],
                    'Summary': issue['summary'],
                    'Issue Type': issue_type,
                    'Status': issue['status'],
                    'Time Spent (hours)': issue['time_spent_hours'],
                    'Original Estimate (hours)': issue['original_estimate_hours'],
                    'Remaining Estimate (hours)': issue['remaining_estimate_hours'],
                    'Assignee': issue['assignee'],
                    'Responsible': issue['responsible'],
                    'Parent Key': issue['parent_key'],
                    'Labels': issue['labels']
                })

        # Sort by Issue ID for easier verification
        detailed_csv_data.sort(key=lambda x: x['Issue ID'])

        # Save detailed CSV report
        detailed_csv_path = os.path.join(OUTPUT_PATHS['reports'], f"{base_filename}.csv")
        detailed_df = pd.DataFrame(detailed_csv_data)
        detailed_df.to_csv(detailed_csv_path, index=False, encoding='utf-8-sig')

        # Calculate and display verification totals
        total_issues = len(detailed_csv_data)
        # Use the CSV column names as keys in detailed_csv_data entries
        total_time_spent = sum(issue['Time Spent (hours)'] for issue in detailed_csv_data)
        total_original_estimate = sum(issue['Original Estimate (hours)'] for issue in detailed_csv_data)

        print(f"\n📋 Detailed issues report saved: {detailed_csv_path}")
        print(f"📊 Verification totals from detailed report:")
        print(f"   - Total issues: {total_issues}")
        print(f"   - Total time spent: {total_time_spent:.2f} hours")
        print(f"   - Total original estimate: {total_original_estimate:.2f} hours")

    def _print_summary(self, summary_data, project_key, sprint_name):
        """Print detailed summary to console"""
        print(f"\n{'='*80}")
        print(f"📊 TIME SPENT BY ISSUE TYPE SUMMARY")
        print(f"🎯 Project: {project_key}")
        print(f"📅 Sprint: {sprint_name}")
        print(f"{'='*80}")

        # Calculate totals
        total_issues = sum(item['count'] for item in summary_data)
        total_time_spent = sum(item['total_time_spent_hours'] for item in summary_data)
        total_original_estimate = sum(item['total_original_estimate_hours'] for item in summary_data)

        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total unique issues: {total_issues}")
        print(f"   Total time spent: {total_time_spent:.2f} hours")
        print(f"   Total original estimate: {total_original_estimate:.2f} hours")
        if total_original_estimate > 0:
            # Calculate Estimation Accuracy as time_spent / original_estimate
            estimation_accuracy = total_time_spent / total_original_estimate
            print(f"   Estimation Accuracy: {estimation_accuracy:.2f} (spent/estimated ratio)")

            # Additional context
            if estimation_accuracy > 1.0:
                exceed_percent = (estimation_accuracy - 1.0) * 100
                print(f"   → Exceeded estimate by {exceed_percent:.1f}%")
            elif estimation_accuracy < 1.0:
                under_percent = (1.0 - estimation_accuracy) * 100
                print(f"   → Completed under estimate by {under_percent:.1f}%")
            else:
                print(f"   → Perfect estimation match!")

        # Sort by total time spent
        sorted_data = sorted(summary_data, key=lambda x: x['total_time_spent_hours'], reverse=True)

        print(f"\n📊 TIME SPENT BY ISSUE TYPE:")
        print(f"{'Issue Type':<15} {'Count':>8} {'Total Hours':>12} {'Avg Hours':>10} {'% of Total':>10}")
        print(f"{'-'*65}")

        for item in sorted_data:
            percentage = (item['total_time_spent_hours'] / total_time_spent * 100) if total_time_spent > 0 else 0
            print(f"{item['issue_type']:<15} {item['count']:>8} {item['total_time_spent_hours']:>12.2f} "
                  f"{item['average_time_spent_hours']:>10.2f} {percentage:>9.1f}%")

        # Calculate aggregated totals (Task + Sub-task, Bug + Sub-bug)
        print(f"\n📊 AGGREGATED TOTALS:")
        print(f"{'Category':<15} {'Count':>8} {'Total Hours':>12} {'Avg Hours':>10} {'% of Total':>10}")
        print(f"{'-'*65}")

        # Aggregate Task and Sub-task
        task_total = {'count': 0, 'hours': 0}
        bug_total = {'count': 0, 'hours': 0}

        for item in summary_data:
            if item['issue_type'] in ['Task', 'Sub-task']:
                task_total['count'] += item['count']
                task_total['hours'] += item['total_time_spent_hours']
            elif item['issue_type'] in ['Bug', 'Sub-bug']:
                bug_total['count'] += item['count']
                bug_total['hours'] += item['total_time_spent_hours']

        # Print aggregated results
        if task_total['count'] > 0:
            task_avg = task_total['hours'] / task_total['count']
            task_percentage = (task_total['hours'] / total_time_spent * 100) if total_time_spent > 0 else 0
            print(f"{'Tasks (all)':<15} {task_total['count']:>8} {task_total['hours']:>12.2f} "
                  f"{task_avg:>10.2f} {task_percentage:>9.1f}%")

        if bug_total['count'] > 0:
            bug_avg = bug_total['hours'] / bug_total['count']
            bug_percentage = (bug_total['hours'] / total_time_spent * 100) if total_time_spent > 0 else 0
            print(f"{'Bugs (all)':<15} {bug_total['count']:>8} {bug_total['hours']:>12.2f} "
                  f"{bug_avg:>10.2f} {bug_percentage:>9.1f}%")

        # Calculate aggregated totals by developer
        developer_totals = defaultdict(lambda: {
            'count': 0,
            'time_spent': 0,
            'original_estimate': 0
        })

        # Aggregate data by developer
        for item in summary_data:
            for issue in item.get('issues', []):
                developer = issue['responsible'] if issue['responsible'] else 'Unknown/Unassigned'
                developer_totals[developer]['count'] += 1
                developer_totals[developer]['time_spent'] += issue['time_spent_hours']
                developer_totals[developer]['original_estimate'] += issue['original_estimate_hours']

        # Print developer aggregation
        print(f"\n📊 TIME SPENT BY DEVELOPER:")
        print(f"{'Developer':<30} {'Count':>8} {'Total Hours':>12} {'Avg Hours':>10} {'Avg Estimate':>12} {'Est. Accuracy':>13}")
        print(f"{'-'*95}")

        # Sort by total time spent (descending)
        sorted_developers = sorted(developer_totals.items(), key=lambda x: x[1]['time_spent'], reverse=True)

        for developer, data in sorted_developers:
            avg_hours = data['time_spent'] / data['count'] if data['count'] > 0 else 0
            avg_estimate = data['original_estimate'] / data['count'] if data['count'] > 0 else 0
            estimation_accuracy = data['time_spent'] / data['original_estimate'] if data['original_estimate'] > 0 else 0.00

            print(f"{developer:<30} {data['count']:>8} {data['time_spent']:>12.2f} "
                  f"{avg_hours:>10.2f} {avg_estimate:>12.2f} {estimation_accuracy:>13.2f}")

        print(f"\n{'='*80}")
        print(f"✅ Analysis complete!")

def main():
    """Main function to run the tool"""
    tool = IssueTypeSummaryTool()
    tool.run()

if __name__ == "__main__":
    main()