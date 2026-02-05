"""
Anomaly Detector Tool - Detection of anomalies in Jira data
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

class AnomalyDetectorTool(BaseScrumMasterTool):
    """Tool for detecting anomalies in sprint data"""
    
    def __init__(self):
        super().__init__("Detection of anomalies in sprint data")

    def run(self):
        """Main method running the analysis"""
        # Get project and sprint
        project_key = self.get_project_key()
        sprint_data = self.get_sprint_selection(project_key)
        
        sprint_name = sprint_data.get('name', 'No name')
        sprint_start = self._parse_sprint_date(sprint_data.get('startDate'))
        sprint_end = self._parse_sprint_date(sprint_data.get('endDate'))
        
        print(f"\n🔍 Detecting anomalies in sprint: {sprint_name}")
        if sprint_start and sprint_end:
            print(f"📅 Period: {sprint_start.strftime('%Y-%m-%d')} - {sprint_end.strftime('%Y-%m-%d')}")
        
        # Analyze anomalies
        anomalies = self._analyze_sprint_anomalies(project_key, sprint_name, sprint_start, sprint_end)
        
        # Generate reports
        self._generate_reports(project_key, sprint_name, anomalies)
        
        # Print summary
        self._print_detailed_summary(anomalies, project_key, sprint_name)

    def _parse_sprint_date(self, date_str):
        """Parse sprint date from Jira format"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    def _analyze_sprint_anomalies(self, project_key, sprint_name, sprint_start, sprint_end):
        """Analyze sprint for various anomalies"""
        
        # Build JQL for sprint issues
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Task, Sub-task, Bug, Sub-Bug)
        AND status != "Cancelled"
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

        print(f"✅ Fetched {len(all_issues)} tasks from sprint")
        print("🔍 Detecting anomalies...")

        anomalies = []
        
        for i, issue in enumerate(all_issues, 1):
            issue_key = issue.get('key', '')
            print(f"   Analyzing {i}/{len(all_issues)}: {issue_key}")
            
            # Check for various anomalies
            issue_anomalies = self._check_issue_anomalies(issue)
            anomalies.extend(issue_anomalies)

        print(f"✅ Found {len(anomalies)} anomalies")
        return anomalies

    def _check_issue_anomalies(self, issue):
        """Check single issue for anomalies"""
        anomalies = []
        issue_key = issue.get('key', '')
        fields = issue.get('fields', {})
        
        # Basic issue info
        summary = fields.get('summary', '')
        status = fields.get('status', {}).get('name', '')
        issue_type = fields.get('issuetype', {}).get('name', '')
        assignee = fields.get('assignee')
        responsible = fields.get(CUSTOM_FIELDS['responsible'])
        labels = fields.get('labels', [])
        components = fields.get('components', [])
        original_estimate = fields.get('timeoriginalestimate')
        time_spent = fields.get('timespent')

        # 1. Missing responsible person
        if not responsible and status.lower() not in ['todo', 'backlog', 'done', 'canceled']:
            anomalies.append({
                'Issue Key': issue_key,
                'Summary': summary,
                'Status': status,
                'Issue Type': issue_type,
                'Anomaly Type': 'Missing Responsible',
                'Description': 'Task has no responsible person assigned',
                'Category': self._get_category_from_labels_and_components(labels, components)
            })
        
        # 2. Missing time estimate
        if not original_estimate and status.lower() not in ['done', 'canceled']:
            anomalies.append({
                'Issue Key': issue_key,
                'Summary': summary,
                'Status': status,
                'Issue Type': issue_type,
                'Anomaly Type': 'Missing Estimate',
                'Description': 'Task has no time estimate',
                'Category': self._get_category_from_labels_and_components(labels, components)
            })
        
        # 3. Missing assignee for in-progress tasks
        if status.lower() in ['in progress', 'in review', 'testing'] and not assignee:
            anomalies.append({
                'Issue Key': issue_key,
                'Summary': summary,
                'Status': status,
                'Issue Type': issue_type,
                'Anomaly Type': 'Missing Assignee',
                'Description': f'Task in status "{status}" has no assignee',
                'Category': self._get_category_from_labels_and_components(labels, components)
            })
        
        # 4. Missing technology labels
        # Check components first, then labels
        components = fields.get('components', [])
        has_tech_component = False

        # Check if any component indicates technology
        if components:
            component_names = [comp.get('name', '') for comp in components if isinstance(comp, dict)]
            has_tech_component = any(name in ['Backend', 'Frontend', 'Fullstack', 'DevOps', 'QA'] for name in component_names)

        # If no tech components, check labels
        has_tech_label = False
        if not has_tech_component and labels:
            has_tech_label = any(label in ['Backend', 'Frontend', 'Fullstack', 'DevOps', 'QA'] for label in labels)

        # Report anomaly if neither components nor labels indicate technology
        if not has_tech_component and not has_tech_label:
            anomalies.append({
                'Issue Key': issue_key,
                'Summary': summary,
                'Status': status,
                'Issue Type': issue_type,
                'Anomaly Type': 'Missing technology labels or components',
                'Description': 'Task has no technology labels or components (Backend/Frontend/etc.)',
                'Category': self._get_category_from_labels_and_components(labels, components)
            })
        
        # 5. Missing work logs for completed tasks
        if status.lower() in ['code review', 'qa testing', 'ready for staging', 'qa staging'] and not time_spent:
            anomalies.append({
                'Issue Key': issue_key,
                'Summary': summary,
                'Status': status,
                'Issue Type': issue_type,
                'Anomaly Type': 'Missing Work Logs',
                'Description': f'Task in status "{status}" has no logged work time',
                'Category': self._get_category_from_labels_and_components(labels, components)
            })

        return anomalies





    def _generate_reports(self, project_key, sprint_name, anomalies):
        """Generate CSV and JSON reports"""
        if not anomalies:
            print("⚠️  No anomalies to export")
            return

        # Create DataFrame
        df = pd.DataFrame(anomalies)

        # Generate filename
        csv_filename = self.generate_output_filename("anomalies", project_key, sprint_name, "csv")

        # Get full path
        csv_path = self.get_output_path("reports", csv_filename)

        # Save CSV
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        print(f"\n📁 FILE EXPORT:")
        print(f"   📊 CSV Report: {csv_path}")

    def _print_detailed_summary(self, anomalies, project_key, sprint_name):
        """Print detailed summary of anomalies"""
        if not anomalies:
            print(f"\n🎉 No anomalies found in sprint!")
            return

        # Create DataFrame for analysis
        df = pd.DataFrame(anomalies)
        
        print(f"\n📊 DETAILED SUMMARY:")
        print(f"   • Project: {project_key}")
        print(f"   • Sprint: {sprint_name}")
        print(f"   • Total anomalies: {len(anomalies)}")
        
        # Summary by anomaly type
        print(f"\n   🔍 Summary by anomaly type:")
        anomaly_counts = df['Anomaly Type'].value_counts()
        for anomaly_type, count in anomaly_counts.items():
            print(f"     • {anomaly_type}: {count}")

        # Summary by category
        print(f"\n   📈 Summary by category:")
        category_counts = df['Category'].value_counts()
        for category, count in category_counts.items():
            print(f"     • {category}: {count}")

        # Most problematic issues
        print(f"\n   🚨 Most problematic issues:")
        issue_counts = df['Issue Key'].value_counts().head(5)
        for issue_key, count in issue_counts.items():
            if count > 1:
                print(f"     • {issue_key}: {count} anomalies")

        # Print summary stats
        self.print_summary(
            project_key,
            sprint_name,
            **{
                "Total anomalies": len(anomalies)
            }
        )

def main():
    """Main function running the tool"""
    tool = AnomalyDetectorTool()
    tool.safe_run()

if __name__ == "__main__":
    main()