"""
Worklog Summary Tool - Summary of work logs in sprint
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

class WorklogSummaryTool(BaseScrumMasterTool):
    """Tool for summarizing work logs in sprint"""
    
    def __init__(self):
        super().__init__("Summary of work logs in sprint")

    def run(self):
        """Main method running the analysis"""
        # Get project and sprint
        project_key = self.get_project_key()
        sprint_data = self.get_sprint_selection(project_key)

        # Get issues to exclude using new exclusions system
        excluded_issues = self.get_project_exclusions(project_key)
        
        sprint_name = sprint_data.get('name', 'No name')
        sprint_start = self._parse_sprint_date(sprint_data.get('startDate'))
        sprint_end = self._parse_sprint_date(sprint_data.get('endDate'))
        
        print(f"\n⏰ Analyzing work logs in sprint: {sprint_name}")
        if sprint_start and sprint_end:
            print(f"📅 Period: {sprint_start.strftime('%Y-%m-%d')} - {sprint_end.strftime('%Y-%m-%d')}")
        
        # Analyze worklogs
        worklog_data = self._analyze_sprint_worklogs(project_key, sprint_name, sprint_start, sprint_end, excluded_issues)

        # Get developer selection
        selection_type, selected_developer = self._get_developer_selection(worklog_data)

        # Filter data if specific developer selected
        if selection_type == 'single':
            worklog_data = self._filter_worklog_by_developer(worklog_data, selected_developer)

        # Generate reports
        self._generate_reports(project_key, sprint_name, worklog_data, selected_developer)

        # Print summary
        self._print_detailed_summary(worklog_data, project_key, sprint_name, selected_developer)

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

    def _analyze_sprint_worklogs(self, project_key, sprint_name, sprint_start, sprint_end, excluded_issues=None):
        """Analyze work logs in sprint"""
        
        # Build JQL for sprint issues
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        ORDER BY key ASC
        """
        
        # Define fields to retrieve
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'created', 'updated',
            'timeoriginalestimate', 'timespent', CUSTOM_FIELDS['responsible'], 'labels', 'components'
        ]

        print(f"🚀 Fetching tasks from sprint...")
        print(f"JQL: {jql.strip()}")

        # Execute query to get all issues
        all_issues = self.jira_client.get_all_results(jql, fields)

        if not all_issues:
            print(f"❌ No tasks found in sprint '{sprint_name}'")
            return []

        # Filter out excluded issues
        if excluded_issues:
            original_count = len(all_issues)
            all_issues = [issue for issue in all_issues if issue.get('key') not in excluded_issues]
            excluded_count = original_count - len(all_issues)
            if excluded_count > 0:
                print(f"❌ Excluded {excluded_count} issues from analysis")

        print(f"✅ Processing {len(all_issues)} tasks from sprint")
        print("⏰ Analyzing work logs...")

        worklog_data = []
        
        for i, issue in enumerate(all_issues, 1):
            issue_key = issue.get('key', '')
            print(f"   Analyzing {i}/{len(all_issues)}: {issue_key}")
            
            # Get worklogs for this issue
            issue_worklogs = self._get_issue_worklogs(issue_key, sprint_start, sprint_end)
            
            # Process each worklog
            for worklog in issue_worklogs:
                worklog_entry = self._extract_worklog_data(issue, worklog)
                worklog_data.append(worklog_entry)

        print(f"✅ Found {len(worklog_data)} work log entries")
        return worklog_data

    def _get_issue_worklogs(self, issue_key, sprint_start, sprint_end):
        """Get worklogs for specific issue within sprint period"""
        try:
            # Get issue with worklogs using the new method
            issue_data = self.jira_client.get_issue_with_worklogs(issue_key)

            if not issue_data:
                logger.warning(f"Could not fetch issue {issue_key}")
                return []

            # Extract worklogs from the response
            worklogs = issue_data.get('fields', {}).get('worklog', {}).get('worklogs', [])

            filtered_worklogs = []
            for worklog in worklogs:
                # Parse worklog date
                started = worklog.get('started', '')
                if started:
                    # Handle Jira date format: 2025-07-09T00:00:00.000+0000
                    try:
                        # Replace +0000 with +00:00 for proper timezone format
                        if started.endswith('+0000'):
                            started = started[:-5] + '+00:00'
                        elif started.endswith('-0000'):
                            started = started[:-5] + '+00:00'

                        worklog_date = datetime.fromisoformat(started)
                    except ValueError:
                        # Fallback: try parsing without timezone
                        try:
                            # Remove timezone info completely
                            date_part = started.split('+')[0].split('Z')[0]
                            # Remove milliseconds if present
                            if '.' in date_part:
                                date_part = date_part.split('.')[0]
                            worklog_date = datetime.fromisoformat(date_part)
                        except ValueError as e:
                            logger.warning(f"Could not parse date {started}: {e}")
                            continue

                    # Filter by sprint period if dates are available
                    if sprint_start and sprint_end:
                        if sprint_start <= worklog_date <= sprint_end:
                            filtered_worklogs.append(worklog)
                    else:
                        # If no sprint dates, include all worklogs
                        filtered_worklogs.append(worklog)

            return filtered_worklogs

        except Exception as e:
            logger.error(f"Error getting worklogs for {issue_key}: {e}")
            return []

    def _extract_worklog_data(self, issue, worklog):
        """Extract relevant data from worklog entry"""
        fields = issue.get('fields', {})

        # Basic issue info
        issue_key = issue.get('key', '')
        summary = fields.get('summary', '')
        status = fields.get('status', {}).get('name', '')
        issue_type = fields.get('issuetype', {}).get('name', '')

        # Responsible person
        responsible = fields.get(CUSTOM_FIELDS['responsible'])
        responsible_name = responsible.get('displayName', '') if responsible else ''

        # Labels and category
        labels = fields.get('labels', [])
        components = fields.get('components', [])
        category = self._get_category_from_labels_and_components(labels, components)

        # Worklog details - now worklog is a dictionary
        author = worklog.get('author', {}).get('displayName', '')
        time_spent_seconds = worklog.get('timeSpentSeconds', 0)
        time_spent_hours = time_spent_seconds / 3600 if time_spent_seconds else 0

        started = worklog.get('started', '')
        comment = worklog.get('comment', '')

        # Parse date for grouping
        worklog_date = ''
        if started:
            try:
                # Handle Jira date format: 2025-07-09T00:00:00.000+0000
                if started.endswith('+0000'):
                    started = started[:-5] + '+00:00'
                elif started.endswith('-0000'):
                    started = started[:-5] + '+00:00'

                date_obj = datetime.fromisoformat(started)
                worklog_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                # Fallback: try parsing without timezone
                try:
                    # Remove timezone info completely
                    date_part = started.split('+')[0].split('Z')[0]
                    # Remove milliseconds if present
                    if '.' in date_part:
                        date_part = date_part.split('.')[0]
                    date_obj = datetime.fromisoformat(date_part)
                    worklog_date = date_obj.strftime('%Y-%m-%d')
                except:
                    logger.warning(f"Could not parse worklog date: {started}")
                    pass

        return {
            'Issue Key': issue_key,
            'Summary': summary,
            'Status': status,
            'Issue Type': issue_type,
            'Responsible': responsible_name,
            'Author': author,
            'Time Spent (hours)': round(time_spent_hours, 2),
            'Date': worklog_date,
            'Category': category,
            'Labels': ', '.join(labels)
        }


    def _generate_reports(self, project_key, sprint_name, worklog_data, selected_developer=None):
        """Generate CSV and JSON reports"""
        if not worklog_data:
            print("⚠️  No work logs to export")
            return

        # Create DataFrame
        df = pd.DataFrame(worklog_data)
        
        # Generate filenames
        if selected_developer:
            # Sanitize developer name for filename
            dev_name_safe = selected_developer.replace(' ', '_').replace('.', '').replace(',', '')
            csv_filename = self.generate_output_filename(f"worklog_summary_{dev_name_safe}", project_key, sprint_name, "csv")
            json_filename = self.generate_output_filename(f"worklog_summary_raw_{dev_name_safe}", project_key, sprint_name, "json")
        else:
            csv_filename = self.generate_output_filename("worklog_summary", project_key, sprint_name, "csv")
            json_filename = self.generate_output_filename("worklog_summary_raw", project_key, sprint_name, "json")
        
        # Get full paths
        csv_path = self.get_output_path("reports", csv_filename)
        json_path = self.get_output_path("reports", json_filename)
        
        # Save CSV
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(worklog_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 FILE EXPORT:")
        print(f"   📊 CSV Report: {csv_path}")
        print(f"   📄 Raw JSON: {json_path}")

    def _print_detailed_summary(self, worklog_data, project_key, sprint_name, selected_developer=None):
        """Print detailed summary of work logs"""
        if not worklog_data:
            print(f"\n📊 No work logs found in sprint")
            return

        # Create DataFrame for analysis
        df = pd.DataFrame(worklog_data)

        # Calculate totals
        total_entries = len(worklog_data)
        total_hours = df['Time Spent (hours)'].sum()
        unique_issues = df['Issue Key'].nunique()
        unique_authors = df['Author'].nunique()

        print(f"\n📊 DETAILED SUMMARY:")
        print(f"   • Project: {project_key}")
        print(f"   • Sprint: {sprint_name}")
        if selected_developer:
            print(f"   • Developer: {selected_developer}")
        print(f"   • Log entries: {total_entries}")
        print(f"   • Total time: {total_hours:.1f}h")
        print(f"   • Unique issues: {unique_issues}")
        if not selected_developer:
            print(f"   • Log authors: {unique_authors}")

        # Summary by authors - skip if single developer selected
        if not selected_developer:
            print(f"\n   👥 Summary by authors:")
            author_stats = df.groupby('Author').agg({
                'Time Spent (hours)': 'sum',
                'Issue Key': 'nunique'
            }).round(1)

            for author, stats in author_stats.iterrows():
                if author:  # Skip empty authors
                    print(f"     • {author}: {stats['Time Spent (hours)']}h on {stats['Issue Key']} issues")

        # Summary by category
        print(f"\n   📈 Summary by category:")
        category_stats = df.groupby('Category').agg({
            'Time Spent (hours)': 'sum',
            'Issue Key': 'nunique'
        }).round(1)

        for category, stats in category_stats.iterrows():
            print(f"     • {category}: {stats['Time Spent (hours)']}h on {stats['Issue Key']} issues")

        # Summary by days
        print(f"\n   📅 Summary by days:")
        daily_stats = df.groupby('Date')['Time Spent (hours)'].sum().round(1)

        for date, hours in daily_stats.items():
            if date:  # Skip empty dates
                print(f"     • {date}: {hours}h")

        # Print summary stats
        self.print_summary(
            project_key,
            sprint_name,
            **{
                "Total entries": total_entries,
                "Total hours": f"{total_hours:.1f}",
                "Unique issues": unique_issues,
                "Authors": unique_authors
            }
        )

    def _get_developer_selection(self, worklog_data):
        """Ask user to choose between all developers or a specific one."""
        # Get unique authors from worklog_data
        unique_authors = sorted({entry['Author'] for entry in worklog_data if entry.get('Author')})

        # Display selection menu (Polish for user)
        print("\n📊 WYBÓR ZAKRESU ANALIZY:")
        print(f"   1. Wszyscy programiści w sprincie ({len(unique_authors)} osób)")
        print("   2. Jeden konkretny programista")

        # Get user choice
        while True:
            choice = input("\n👉 Wybierz opcję (1-2): ").strip()
            if choice == '' or choice == '1':
                return ('all', None)
            elif choice == '2':
                return self._select_specific_developer(unique_authors)
            else:
                print("⚠️  Nieprawidłowy wybór. Wprowadź 1 lub 2.")

    def _select_specific_developer(self, developers):
        """Let user select a specific developer from the list."""
        print("\n👥 PROGRAMIŚCI W SPRINCIE:")
        for i, dev in enumerate(developers, 1):
            print(f"   {i}. {dev}")

        while True:
            choice = input(f"\n👉 Wybierz programistę (1-{len(developers)}): ").strip()
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(developers):
                    selected_dev = developers[choice_num - 1]
                    print(f"✅ Wybrano: {selected_dev}")
                    return ('single', selected_dev)
                else:
                    print(f"⚠️  Nieprawidłowy numer. Wprowadź liczbę od 1 do {len(developers)}.")
            except ValueError:
                print("⚠️  Wprowadź prawidłową liczbę.")

    def _filter_worklog_by_developer(self, worklog_data, developer_name):
        """Filter worklog entries for a specific developer."""
        filtered_data = [entry for entry in worklog_data if entry.get('Author') == developer_name]
        print(f"🔍 Przefiltrowano dane: {len(filtered_data)} wpisów dla {developer_name}")
        return filtered_data

def main():
    """Main function running the tool"""
    tool = WorklogSummaryTool()
    tool.safe_run()

if __name__ == "__main__":
    main()