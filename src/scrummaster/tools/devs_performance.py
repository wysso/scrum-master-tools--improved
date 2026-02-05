"""
Devs Performance Tool - Analysis of developers performance in sprint
Shows Completed Tasks hours and Scope Tasks hours per developer
Author: Based on sprint_completion.py
"""
import sys
import os
import pandas as pd
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np

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

class DevsPerformanceTool(BaseScrumMasterTool):
    """Tool for analyzing developers performance in sprint"""
    
    def __init__(self):
        super().__init__("Developers Performance Analysis")

    def run(self):
        """Main method running the analysis"""
        # Get project
        project_key = self.get_project_key()

        # Ask user for analysis mode
        analysis_mode = self._get_analysis_mode()

        if analysis_mode == 'single':
            # Single sprint analysis (current behavior)
            self._run_single_sprint_analysis(project_key)
        else:
            # Multi-sprint analysis for single developer
            self._run_multi_sprint_analysis(project_key)

    def _get_analysis_mode(self):
        """Ask user to choose between single sprint or multi-sprint analysis"""
        print("\n📊 ANALYSIS MODE:")
        print("   1. Single Sprint - Multiple Developers")
        print("   2. Multiple Sprints - Single Developer")

        while True:
            choice = input("\n👉 Choose analysis mode (1-2): ").strip()
            if choice == '1':
                return 'single'
            elif choice == '2':
                return 'multi'
            else:
                print("⚠️  Invalid choice. Please enter 1 or 2.")

    def _run_single_sprint_analysis(self, project_key):
        """Run analysis for single sprint with multiple developers"""
        # Get sprint
        sprint_data = self.get_sprint_selection(project_key)

        sprint_name = sprint_data.get('name', 'No name')
        sprint_start = self._parse_sprint_date(sprint_data.get('startDate'))
        sprint_end = self._parse_sprint_date(sprint_data.get('endDate'))

        print(f"\n🎯 Analyzing developers performance in sprint: {sprint_name}")
        if sprint_start and sprint_end:
            print(f"📅 Period: {sprint_start.strftime('%Y-%m-%d')} - {sprint_end.strftime('%Y-%m-%d')}")

        # Get all developers from sprint
        all_developers = self._get_all_developers_from_sprint(project_key, sprint_name)

        # Let user select developers to include
        selected_developers = self._select_developers(all_developers)

        if not selected_developers:
            print("\n❌ No developers selected for analysis")
            return

        # Analyze completed tasks (using logic from sprint_completion)
        completed_data, completed_details = self._analyze_completed_tasks(project_key, sprint_name, sprint_start, sprint_end, selected_developers)

        # Analyze scope tasks (new logic)
        scope_data, scope_details = self._analyze_scope_tasks(project_key, sprint_name, sprint_start, selected_developers)

        # Combine data and calculate performance
        performance_data = self._calculate_performance(completed_data, scope_data)

        # Generate reports
        self._generate_reports(project_key, sprint_name, performance_data, completed_details, scope_details)

        # Print summary
        self._print_summary(performance_data, project_key, sprint_name)

    def _run_multi_sprint_analysis(self, project_key):
        """Run analysis for multiple sprints with single developer"""
        # Get all developers from project
        print("\n🔍 Fetching all developers from project...")
        all_developers = self._get_all_developers_from_project(project_key)

        if not all_developers:
            print("\n❌ No developers found in project")
            return

        # Let user select single developer
        selected_developer = self._select_single_developer(all_developers)

        if not selected_developer:
            print("\n❌ No developer selected for analysis")
            return

        # Get sprints for analysis
        selected_sprints = self._select_multiple_sprints(project_key)

        if not selected_sprints:
            print("\n❌ No sprints selected for analysis")
            return

        print(f"\n🎯 Analyzing performance for: {selected_developer}")
        print(f"📅 Across {len(selected_sprints)} sprints")

        # Analyze each sprint
        all_sprint_data = []
        total_completed = 0
        total_scope = 0

        for sprint in selected_sprints:
            sprint_name = sprint.get('name', 'No name')
            sprint_start = self._parse_sprint_date(sprint.get('startDate'))
            sprint_end = self._parse_sprint_date(sprint.get('endDate'))

            print(f"\n🔄 Analyzing sprint: {sprint_name}")

            # Analyze completed tasks for this developer in this sprint
            completed_data, _ = self._analyze_completed_tasks(
                project_key, sprint_name, sprint_start, sprint_end, [selected_developer]
            )

            # Analyze scope tasks for this developer in this sprint
            scope_data, _ = self._analyze_scope_tasks(
                project_key, sprint_name, sprint_start, [selected_developer]
            )

            # Get values for selected developer
            completed_hours = completed_data.get(selected_developer, 0)
            scope_hours = scope_data.get(selected_developer, 0)

            # Get worked hours for this developer in this sprint period
            worked_hours = 0
            if sprint_start and sprint_end:
                print(f"   📊 Fetching worklogs for {selected_developer}...")
                worked_hours = self._get_developer_worklogs_in_period(
                    selected_developer, sprint_start, sprint_end
                )
                print(f"   ✅ Found {worked_hours:.1f}h logged")

            # Calculate performance and focus rate
            performance_percentage = (completed_hours / scope_hours * 100) if scope_hours > 0 else 0
            focus_rate = (completed_hours / worked_hours * 100) if worked_hours > 0 else 0

            sprint_result = {
                'sprint_name': sprint_name,
                'sprint_start': sprint_start,
                'sprint_end': sprint_end,
                'completed_hours': completed_hours,
                'scope_hours': scope_hours,
                'worked_hours': worked_hours,
                'performance_percentage': performance_percentage,
                'focus_rate': focus_rate
            }

            all_sprint_data.append(sprint_result)
            total_completed += completed_hours
            total_scope += scope_hours

        # Calculate total worked hours
        total_worked = sum(sprint['worked_hours'] for sprint in all_sprint_data)

        # Generate multi-sprint report
        self._generate_multi_sprint_report(project_key, selected_developer, all_sprint_data, total_completed, total_scope, total_worked)

        # Generate performance charts
        self._generate_performance_charts(selected_developer, all_sprint_data, project_key)

        # Print multi-sprint summary
        self._print_multi_sprint_summary(selected_developer, all_sprint_data, total_completed, total_scope, total_worked)

    def _get_all_developers_from_project(self, project_key):
        """Get all developers who have tasks in the project"""
        # Build JQL for all project issues
        jql = f"""
        project = "{project_key}"
        AND issuetype in (Bug, Task, Sub-bug, Sub-task)
        """

        # Only need responsible field
        fields = [CUSTOM_FIELDS['responsible']]

        # Execute query with limit
        print("   Fetching developers (this may take a moment)...")
        all_issues = self.jira_client.get_all_results(jql, fields)

        if not all_issues:
            return []

        # Collect unique developers
        developers = set()
        for issue in all_issues:
            fields = issue.get('fields', {})
            responsible = fields.get(CUSTOM_FIELDS['responsible'])
            if responsible:
                developer_name = responsible.get('displayName', '')
                if developer_name:
                    developers.add(developer_name)

        print(f"✅ Found {len(developers)} unique developers in project")
        return sorted(list(developers))

    def _select_single_developer(self, all_developers):
        """Let user select a single developer for multi-sprint analysis"""
        print(f"\n👥 DEVELOPERS IN PROJECT ({len(all_developers)} total):")

        # Show developers in columns for better readability
        for i, dev in enumerate(all_developers, 1):
            print(f"   {i:3d}. {dev}")

        print("\n📝 SELECT DEVELOPER FOR ANALYSIS:")

        while True:
            choice = input("\n👉 Enter developer number: ").strip()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(all_developers):
                    selected = all_developers[idx]
                    print(f"\n✅ Selected developer: {selected}")
                    return selected
                else:
                    print(f"⚠️  Invalid number. Please enter 1-{len(all_developers)}")
            except ValueError:
                print("⚠️  Please enter a valid number")

    def _select_multiple_sprints(self, project_key):
        """Let user select multiple sprints for analysis"""
        # Get all sprints
        print("\n📋 Fetching sprints...")

        # Get boards for project
        boards = self.jira_client.get_project_boards(project_key)
        if not boards:
            print(f"❌ No boards found for project {project_key}")
            return []

        # Use first scrum board
        scrum_boards = [b for b in boards if b.get('type') == 'scrum']
        if not scrum_boards:
            print(f"❌ No scrum boards found for project {project_key}")
            return []

        board = scrum_boards[0]
        board_id = board.get('id')

        # Get all sprints
        all_sprints = self.jira_client.get_project_sprints(project_key, board_id)

        if not all_sprints:
            print(f"❌ No sprints found")
            return []

        # Filter closed sprints (for historical analysis)
        closed_sprints = [s for s in all_sprints if s.get('state') == 'closed']

        if not closed_sprints:
            print(f"❌ No closed sprints found")
            return []

        # Sort by end date (oldest first, newest at bottom for better readability)
        closed_sprints.sort(key=lambda x: x.get('endDate', ''), reverse=False)

        print(f"\n📅 CLOSED SPRINTS (oldest first, newest at bottom):")
        for i, sprint in enumerate(closed_sprints, 1):  # Show all closed sprints
            sprint_name = sprint.get('name', 'No name')
            end_date = sprint.get('endDate', 'No date')
            if end_date and end_date != 'No date':
                end_date = self._parse_sprint_date(end_date)
                if end_date:
                    end_date = end_date.strftime('%Y-%m-%d')
            print(f"   {i:2d}. {sprint_name} (ended: {end_date})")

        print("\n📝 SELECT SPRINTS TO ANALYZE:")
        print("   • Enter sprint numbers separated by commas (e.g., 1,2,3)")
        print("   • Enter a range (e.g., 1-5)")
        print("   • Enter 'last X' to select last X sprints (e.g., last 5)")

        while True:
            choice = input("\n👉 Your choice: ").strip().lower()

            selected_indices = []

            # Handle "last X" format
            if choice.startswith('last '):
                try:
                    count = int(choice.split()[1])
                    selected_indices = list(range(min(count, len(closed_sprints))))
                except (ValueError, IndexError):
                    print("⚠️  Invalid format. Use 'last 5' for example.")
                    continue

            # Handle range format (1-5)
            elif '-' in choice and ',' not in choice:
                try:
                    start, end = choice.split('-')
                    start = int(start.strip()) - 1
                    end = int(end.strip())
                    selected_indices = list(range(start, min(end, len(closed_sprints))))
                except ValueError:
                    print("⚠️  Invalid range format. Use '1-5' for example.")
                    continue

            # Handle comma-separated format
            else:
                try:
                    for num in choice.split(','):
                        num = num.strip()
                        if num:
                            idx = int(num) - 1
                            if 0 <= idx < len(closed_sprints):
                                selected_indices.append(idx)
                except ValueError:
                    print("⚠️  Invalid format. Use numbers separated by commas.")
                    continue

            # Validate selection
            if not selected_indices:
                print("⚠️  No sprints selected.")
                continue

            # Get selected sprints
            selected_sprints = [closed_sprints[i] for i in selected_indices]

            # Show selection
            print(f"\n✅ Selected {len(selected_sprints)} sprints:")
            for sprint in selected_sprints:
                sprint_name = sprint.get('name', 'No name')
                print(f"   • {sprint_name}")

            # Confirm
            confirm = input("\n👉 Confirm selection? (y/n): ").strip().lower()
            if confirm == 'y':
                return selected_sprints
            else:
                print("\n🔄 Let's try again...")

    def _generate_multi_sprint_report(self, project_key, developer_name, sprint_data, total_completed, total_scope, total_worked):
        """Generate CSV report for multi-sprint analysis"""
        print(f"\n📁 FILE EXPORT:")

        # Prepare data for CSV
        report_data = []

        # Add total row
        total_performance = (total_completed / total_scope * 100) if total_scope > 0 else 0
        total_focus_rate = (total_completed / total_worked * 100) if total_worked > 0 else 0
        report_data.append({
            'Sprint': 'TOTAL',
            'Start Date': '',
            'End Date': '',
            'Completed Hours': round(total_completed, 2),
            'Scope Hours': round(total_scope, 2),
            'Worked Hours': round(total_worked, 2),
            'Completed %': round(total_performance, 1),
            'Focus Rate': round(total_focus_rate, 1)
        })

        # Add separator
        report_data.append({
            'Sprint': '---',
            'Start Date': '---',
            'End Date': '---',
            'Completed Hours': '---',
            'Scope Hours': '---',
            'Worked Hours': '---',
            'Completed %': '---',
            'Focus Rate': '---'
        })

        # Add individual sprint data
        for sprint in sprint_data:
            report_data.append({
                'Sprint': sprint['sprint_name'],
                'Start Date': sprint['sprint_start'].strftime('%Y-%m-%d') if sprint['sprint_start'] else '',
                'End Date': sprint['sprint_end'].strftime('%Y-%m-%d') if sprint['sprint_end'] else '',
                'Completed Hours': round(sprint['completed_hours'], 2),
                'Scope Hours': round(sprint['scope_hours'], 2),
                'Worked Hours': round(sprint['worked_hours'], 2),
                'Completed %': round(sprint['performance_percentage'], 1),
                'Focus Rate': round(sprint['focus_rate'], 1)
            })

        # Create DataFrame and save
        df = pd.DataFrame(report_data)

        # Generate filename with developer name
        safe_developer_name = developer_name.replace(' ', '_').replace('[', '').replace(']', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"devs_performance_multi_sprint_{project_key}_{safe_developer_name}_{timestamp}.csv"

        csv_path = self.get_output_path("reports", filename)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"   📊 Multi-Sprint Performance CSV: {csv_path}")

    def _generate_performance_charts(self, developer_name, sprint_data, project_key):
        """Generate performance charts for multi-sprint analysis"""
        if len(sprint_data) < 2:
            print("   ⚠️  Not enough data points for charts (need at least 2 sprints)")
            return

        # Set dark theme
        plt.style.use('dark_background')

        # Define custom colors for dark mode
        colors = {
            'completed': '#00D9FF',  # Bright cyan
            'scope': '#FF6B6B',      # Coral red
            'worked': '#4ECDC4',     # Teal
            'focus': '#95E1D3',      # Mint green
            'performance': '#FFD93D', # Golden yellow
            'grid': '#404040',       # Dark gray for grid
            'text': '#E0E0E0'        # Light gray for text
        }

        # Reverse data to show oldest sprint on the left, newest on the right
        sprint_data_reversed = list(reversed(sprint_data))

        # Prepare data
        sprints = [s['sprint_name'].replace('Devolo - ', '') for s in sprint_data_reversed]  # Shorten names
        completed = [s['completed_hours'] for s in sprint_data_reversed]
        scope = [s['scope_hours'] for s in sprint_data_reversed]
        worked = [s['worked_hours'] for s in sprint_data_reversed]
        focus_rate = [s['focus_rate'] for s in sprint_data_reversed]
        performance = [s['performance_percentage'] for s in sprint_data_reversed]

        # Create figure with dark background
        fig = plt.figure(figsize=(16, 12), facecolor='#1a1a1a')

        # 1. Hours Comparison Chart (Bar chart)
        ax1 = plt.subplot(2, 2, 1, facecolor='#1a1a1a')
        x = np.arange(len(sprints))
        width = 0.25

        bars1 = ax1.bar(x - width, completed, width, label='Completed', alpha=0.9, color=colors['completed'])
        bars2 = ax1.bar(x, scope, width, label='Scope', alpha=0.9, color=colors['scope'])
        bars3 = ax1.bar(x + width, worked, width, label='Worked', alpha=0.9, color=colors['worked'])

        ax1.set_xlabel('Sprint', color=colors['text'])
        ax1.set_ylabel('Hours', color=colors['text'])
        ax1.set_title(f'Hours Comparison - {developer_name}', color=colors['text'], fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(sprints, rotation=45, ha='right', color=colors['text'])
        ax1.tick_params(colors=colors['text'])
        ax1.legend(facecolor='#2a2a2a', edgecolor=colors['grid'])
        ax1.grid(True, alpha=0.3, color=colors['grid'])
        ax1.spines['bottom'].set_color(colors['grid'])
        ax1.spines['top'].set_color(colors['grid'])
        ax1.spines['left'].set_color(colors['grid'])
        ax1.spines['right'].set_color(colors['grid'])

        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height:.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize=8, color=colors['text'])

        # 2. Completed Hours Trend with Linear Regression
        ax2 = plt.subplot(2, 2, 2, facecolor='#1a1a1a')
        x_numeric = np.arange(len(completed))
        ax2.plot(x_numeric, completed, 'o-', linewidth=2, markersize=8,
                label='Completed Hours', color=colors['completed'])

        # Add trend line
        z = np.polyfit(x_numeric, completed, 1)
        p = np.poly1d(z)
        ax2.plot(x_numeric, p(x_numeric), "--", alpha=0.8, linewidth=2,
                color=colors['performance'], label=f'Trend (slope: {z[0]:.1f}h/sprint)')

        ax2.set_xlabel('Sprint', color=colors['text'])
        ax2.set_ylabel('Hours', color=colors['text'])
        ax2.set_title('Completed Hours Trend', color=colors['text'], fontsize=14, fontweight='bold')
        ax2.set_xticks(x_numeric)
        ax2.set_xticklabels(sprints, rotation=45, ha='right', color=colors['text'])
        ax2.tick_params(colors=colors['text'])
        ax2.legend(facecolor='#2a2a2a', edgecolor=colors['grid'])
        ax2.grid(True, alpha=0.3, color=colors['grid'])
        ax2.spines['bottom'].set_color(colors['grid'])
        ax2.spines['top'].set_color(colors['grid'])
        ax2.spines['left'].set_color(colors['grid'])
        ax2.spines['right'].set_color(colors['grid'])

        # 3. Focus Rate & Performance Trend
        ax3 = plt.subplot(2, 2, 3, facecolor='#1a1a1a')
        ax3_twin = ax3.twinx()

        line1 = ax3.plot(x_numeric, focus_rate, 'o-', color=colors['focus'], linewidth=2,
                        markersize=8, label='Focus Rate %')
        line2 = ax3_twin.plot(x_numeric, performance, 's-', color=colors['performance'], linewidth=2,
                            markersize=8, label='Completed %')

        ax3.set_xlabel('Sprint', color=colors['text'])
        ax3.set_ylabel('Focus Rate %', color=colors['focus'])
        ax3_twin.set_ylabel('Completed %', color=colors['performance'])
        ax3.set_title('Focus Rate vs Performance', color=colors['text'], fontsize=14, fontweight='bold')
        ax3.set_xticks(x_numeric)
        ax3.set_xticklabels(sprints, rotation=45, ha='right', color=colors['text'])
        ax3.tick_params(axis='y', labelcolor=colors['focus'])
        ax3.tick_params(axis='x', colors=colors['text'])
        ax3_twin.tick_params(axis='y', labelcolor=colors['performance'])
        ax3.grid(True, alpha=0.3, color=colors['grid'])
        ax3.spines['bottom'].set_color(colors['grid'])
        ax3.spines['top'].set_color(colors['grid'])
        ax3.spines['left'].set_color(colors['grid'])
        ax3.spines['right'].set_color(colors['grid'])
        ax3_twin.spines['bottom'].set_color(colors['grid'])
        ax3_twin.spines['top'].set_color(colors['grid'])
        ax3_twin.spines['left'].set_color(colors['grid'])
        ax3_twin.spines['right'].set_color(colors['grid'])

        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='best', facecolor='#2a2a2a', edgecolor=colors['grid'])

        # 4. Efficiency Matrix (Scatter plot)
        ax4 = plt.subplot(2, 2, 4, facecolor='#1a1a1a')
        scatter = ax4.scatter(worked, completed, s=200, c=focus_rate, cmap='viridis',
                            alpha=0.9, edgecolors=colors['text'], linewidth=1)

        # Add sprint labels
        for i, sprint in enumerate(sprints):
            ax4.annotate(sprint, (worked[i], completed[i]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9, color=colors['text'])

        # Add diagonal line (100% efficiency)
        max_val = max(max(worked), max(completed))
        ax4.plot([0, max_val], [0, max_val], '--', alpha=0.5,
                color=colors['grid'], label='100% Focus')

        ax4.set_xlabel('Worked Hours', color=colors['text'])
        ax4.set_ylabel('Completed Hours', color=colors['text'])
        ax4.set_title('Work Efficiency Matrix', color=colors['text'], fontsize=14, fontweight='bold')
        ax4.tick_params(colors=colors['text'])
        ax4.legend(facecolor='#2a2a2a', edgecolor=colors['grid'])
        ax4.grid(True, alpha=0.3, color=colors['grid'])
        ax4.spines['bottom'].set_color(colors['grid'])
        ax4.spines['top'].set_color(colors['grid'])
        ax4.spines['left'].set_color(colors['grid'])
        ax4.spines['right'].set_color(colors['grid'])

        # Add colorbar with dark theme
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('Focus Rate %', color=colors['text'])
        cbar.ax.tick_params(colors=colors['text'])
        cbar.outline.set_edgecolor(colors['grid'])

        # Overall title and layout
        fig.suptitle(f'Performance Analysis - {developer_name}\n{project_key} - {len(sprint_data)} Sprints',
                    fontsize=16, fontweight='bold', color=colors['text'])
        plt.tight_layout()

        # Save the figure
        safe_developer_name = developer_name.replace(' ', '_').replace('[', '').replace(']', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        chart_filename = f"performance_charts_{project_key}_{safe_developer_name}_{timestamp}.png"
        chart_path = self.get_output_path("reports", chart_filename)

        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
        plt.close()

        print(f"   📈 Performance Charts: {chart_path}")

    def _print_multi_sprint_summary(self, developer_name, sprint_data, total_completed, total_scope, total_worked):
        """Print summary for multi-sprint analysis"""
        print(f"\n📊 MULTI-SPRINT PERFORMANCE SUMMARY:")
        print(f"   • Developer: {developer_name}")
        print(f"   • Sprints analyzed: {len(sprint_data)}")

        # Total performance
        total_performance = (total_completed / total_scope * 100) if total_scope > 0 else 0
        total_focus_rate = (total_completed / total_worked * 100) if total_worked > 0 else 0

        print(f"\n   📈 TOTAL PERFORMANCE:")
        print(f"   • Total Completed: {total_completed:.1f}h")
        print(f"   • Total Scope: {total_scope:.1f}h")
        print(f"   • Total Worked: {total_worked:.1f}h")
        print(f"   • Overall Completed: {total_performance:.1f}%")
        print(f"   • Overall Focus Rate: {total_focus_rate:.1f}%")

        # Individual sprints
        print(f"\n   📊 PERFORMANCE BY SPRINT:")
        print(f"   {'Sprint':<30} {'Completed':>12} {'Scope':>12} {'Completed %':>12} {'Worked':>12} {'Focus Rate':>12}")
        print(f"   {'-'*30} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")

        for sprint in sprint_data:
            sprint_name = sprint['sprint_name']
            if len(sprint_name) > 30:
                sprint_name = sprint_name[:27] + '...'

            print(f"   {sprint_name:<30} {sprint['completed_hours']:>10.1f}h {sprint['scope_hours']:>10.1f}h {sprint['performance_percentage']:>10.1f}% {sprint['worked_hours']:>10.1f}h {sprint['focus_rate']:>10.1f}%")

        print(f"   {'-'*30} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
        print(f"   {'TOTAL':<30} {total_completed:>10.1f}h {total_scope:>10.1f}h {total_performance:>10.1f}% {total_worked:>10.1f}h {total_focus_rate:>10.1f}%")

        # Calculate averages
        num_sprints = len(sprint_data)
        avg_completed = total_completed / num_sprints if num_sprints > 0 else 0
        avg_scope = total_scope / num_sprints if num_sprints > 0 else 0
        avg_worked = total_worked / num_sprints if num_sprints > 0 else 0
        avg_performance = sum(s['performance_percentage'] for s in sprint_data) / num_sprints if num_sprints > 0 else 0
        avg_focus_rate = sum(s['focus_rate'] for s in sprint_data) / num_sprints if num_sprints > 0 else 0

        print(f"   {'AVG':<30} {avg_completed:>10.1f}h {avg_scope:>10.1f}h {avg_performance:>10.1f}% {avg_worked:>10.1f}h {avg_focus_rate:>10.1f}%")

    def _parse_sprint_date(self, date_str):
        """Parse sprint date from Jira format"""
        if not date_str:
            return None

        try:
            # Handle different Jira date formats
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
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None

    def _get_developer_worklogs_in_period(self, developer_name, start_date, end_date):
        """Get all worklogs for a developer in a specific period"""
        # Build JQL to get all issues with worklogs by this developer
        # We need to search broadly to catch all worklogs
        jql = f"""
        worklogAuthor = "{developer_name}"
        AND worklogDate >= "{start_date.strftime('%Y-%m-%d')}"
        AND worklogDate <= "{end_date.strftime('%Y-%m-%d')}"
        """

        fields = ['key', 'summary']

        try:
            # Get all issues where developer has logged work
            issues = self.jira_client.get_all_results(jql, fields)

            total_hours = 0

            for issue in issues:
                issue_key = issue.get('key', '')

                # Get issue with worklogs
                issue_data = self.jira_client.get_issue_with_worklogs(issue_key)

                if not issue_data:
                    continue

                # Extract worklogs
                worklogs = issue_data.get('fields', {}).get('worklog', {}).get('worklogs', [])

                for worklog in worklogs:
                    # Check if worklog is by our developer
                    author = worklog.get('author', {})
                    author_name = author.get('displayName', '')

                    if author_name != developer_name:
                        continue

                    # Parse worklog date
                    started = worklog.get('started', '')
                    if started:
                        try:
                            # Handle date format
                            if started.endswith('+0000'):
                                started = started[:-5] + '+00:00'
                            elif started.endswith('-0000'):
                                started = started[:-5] + '+00:00'

                            worklog_date = datetime.fromisoformat(started)

                            # Check if within period
                            if start_date <= worklog_date <= end_date:
                                time_spent_seconds = worklog.get('timeSpentSeconds', 0)
                                total_hours += time_spent_seconds / 3600

                        except ValueError:
                            logger.warning(f"Could not parse worklog date: {started}")
                            continue

            return total_hours

        except Exception as e:
            logger.error(f"Error getting worklogs for {developer_name}: {e}")
            return 0

    def _get_all_developers_from_sprint(self, project_key, sprint_name):
        """Get all developers who have tasks in the sprint"""
        print("\n🔍 Fetching all developers from sprint...")

        # Build JQL for all sprint issues
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Bug, Task, Sub-bug, Sub-task)
        """

        # Only need responsible field
        fields = [CUSTOM_FIELDS['responsible']]

        # Execute query
        all_issues = self.jira_client.get_all_results(jql, fields)

        if not all_issues:
            return set()

        # Collect unique developers
        developers = set()
        for issue in all_issues:
            fields = issue.get('fields', {})
            responsible = fields.get(CUSTOM_FIELDS['responsible'])
            if responsible:
                developer_name = responsible.get('displayName', '')
                if developer_name:
                    developers.add(developer_name)

        print(f"✅ Found {len(developers)} unique developers in sprint")
        return sorted(list(developers))

    def _select_developers(self, all_developers):
        """Let user select which developers to include in analysis"""
        if not all_developers:
            print("\n❌ No developers found in sprint")
            return []

        print(f"\n👥 DEVELOPERS IN SPRINT ({len(all_developers)} total):")
        for i, dev in enumerate(all_developers, 1):
            print(f"   {i}. {dev}")

        print("\n📝 SELECT DEVELOPERS TO INCLUDE:")
        print("   • Press Enter to include ALL developers")
        print("   • Enter numbers to EXCLUDE (comma-separated, e.g., 1,3,5)")
        print("   • Enter 'all' to exclude ALL (cancel analysis)")

        while True:
            choice = input("\n👉 Your choice: ").strip().lower()

            # Include all developers
            if not choice:
                print(f"\n✅ Including all {len(all_developers)} developers")
                return all_developers

            # Exclude all (cancel)
            if choice == 'all':
                return []

            # Parse exclusion list
            try:
                # Parse comma-separated numbers
                exclude_indices = []
                for num in choice.split(','):
                    num = num.strip()
                    if num:
                        idx = int(num) - 1
                        if 0 <= idx < len(all_developers):
                            exclude_indices.append(idx)
                        else:
                            print(f"⚠️  Invalid number: {num} (must be 1-{len(all_developers)})")
                            continue

                # Create list of included developers
                included_developers = []
                excluded_developers = []
                for i, dev in enumerate(all_developers):
                    if i in exclude_indices:
                        excluded_developers.append(dev)
                    else:
                        included_developers.append(dev)

                if not included_developers:
                    print("\n❌ All developers excluded. Canceling analysis.")
                    return []

                # Show summary
                print(f"\n✅ INCLUDED ({len(included_developers)} developers):")
                for dev in included_developers:
                    print(f"   • {dev}")

                if excluded_developers:
                    print(f"\n❌ EXCLUDED ({len(excluded_developers)} developers):")
                    for dev in excluded_developers:
                        print(f"   • {dev}")

                # Confirm selection
                confirm = input("\n👉 Confirm selection? (y/n): ").strip().lower()
                if confirm == 'y':
                    return included_developers
                else:
                    print("\n🔄 Let's try again...")

            except ValueError:
                print("⚠️  Invalid input. Please enter numbers separated by commas or press Enter.")

    def _analyze_completed_tasks(self, project_key, sprint_name, sprint_start, sprint_end, selected_developers=None):
        """Analyze completed tasks in sprint using logic from sprint_completion"""
        
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
            'timeoriginalestimate', 'timespent', CUSTOM_FIELDS['responsible'], 'labels'
        ]

        print(f"\n🚀 Fetching tasks for completed analysis...")
        
        # Execute query to get all issues with changelog
        all_issues = self.jira_client.get_all_results(jql, fields, expand=['changelog'])
        
        if not all_issues:
            print(f"❌ No tasks found in sprint '{sprint_name}'")
            return {}, []
        
        print(f"✅ Fetched {len(all_issues)} tasks")
        print("🔍 Analyzing completed tasks...")
        
        # Dictionary to store completed hours per developer
        completed_by_developer = {}
        # List to store detailed task information
        completed_details = []
        
        for issue in all_issues:
            # Check if task was completed during sprint
            completion_result = self._was_completed_during_sprint(issue, sprint_start, sprint_end)
            if completion_result['completed']:
                # Get task details
                fields = issue.get('fields', {})
                issue_key = issue.get('key', '')
                summary = fields.get('summary', '')
                issue_type = fields.get('issuetype', {}).get('name', '')
                status = fields.get('status', {}).get('name', '')
                
                # Get responsible developer
                responsible = fields.get(CUSTOM_FIELDS['responsible'])
                responsible_name = responsible.get('displayName', 'Unassigned') if responsible else 'Unassigned'

                # Skip if developer not in selected list
                if selected_developers and responsible_name not in selected_developers:
                    continue
                
                # Get assignee
                assignee = fields.get('assignee')
                assignee_name = assignee.get('displayName', '') if assignee else ''
                
                # Get original estimate and time spent
                original_estimate = fields.get('timeoriginalestimate', 0) or 0
                original_estimate_hours = original_estimate / 3600 if original_estimate else 0
                
                time_spent = fields.get('timespent', 0) or 0
                time_spent_hours = time_spent / 3600 if time_spent else 0
                
                # Get labels
                labels = fields.get('labels', [])
                
                # Add to developer's total
                if responsible_name not in completed_by_developer:
                    completed_by_developer[responsible_name] = 0
                completed_by_developer[responsible_name] += original_estimate_hours
                
                # Add to details list
                completed_details.append({
                    'Issue Key': issue_key,
                    'Summary': summary,
                    'Issue Type': issue_type,
                    'Status': status,
                    'Responsible': responsible_name,
                    'Assignee': assignee_name,
                    'Original Estimate (hours)': round(original_estimate_hours, 2),
                    'Time Spent (hours)': round(time_spent_hours, 2),
                    'Labels': ', '.join(labels),
                    'Completion Reason': completion_result['reason']
                })
        
        return completed_by_developer, completed_details

    def _was_completed_during_sprint(self, issue, sprint_start, sprint_end):
        """Check if task was completed during sprint (copied from sprint_completion)"""
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
                    if (to_status == 'code review' and
                        from_status in ['in progress', 'to do', 'backlog']):
                        valid_transitions_to_code_review.append({
                            'date': history_date,
                            'from': from_status,
                            'to': to_status
                        })
        
        # If no valid transitions to Code Review during sprint, not completed
        if not valid_transitions_to_code_review:
            return {'completed': False, 'reason': 'No transition to Code Review during sprint'}
        
        # Check if the first valid transition to Code Review was during this sprint
        first_transition = min(valid_transitions_to_code_review, key=lambda x: x['date'])
        
        # Additional validation for In Progress transitions only
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
                return {'completed': False, 'reason': 'Task did not start in this sprint'}
        
        # Task is completed
        return {'completed': True, 'reason': f'Completed during sprint'}

    def _analyze_scope_tasks(self, project_key, sprint_name, sprint_start, selected_developers=None):
        """Analyze scope tasks at sprint start"""
        
        # Build JQL for ALL tasks in sprint (regardless of current status)
        jql = f"""
        project = "{project_key}"
        AND sprint = "{sprint_name}"
        AND issuetype in (Bug, Task, Sub-bug, Sub-task)
        ORDER BY key ASC
        """
        
        # Define fields to retrieve
        fields = [
            'summary', 'status', 'issuetype', 'assignee', 'timeoriginalestimate', 
            CUSTOM_FIELDS['responsible'], 'labels', 'created'
        ]
        
        print(f"\n🚀 Fetching all tasks from sprint for scope analysis...")
        
        # Execute query to get all issues with changelog
        all_issues = self.jira_client.get_all_results(jql, fields, expand=['changelog'])
        
        if not all_issues:
            print(f"❌ No tasks found in sprint '{sprint_name}'")
            return {}, []
        
        print(f"✅ Fetched {len(all_issues)} tasks from sprint")
        print("🔍 Analyzing task statuses at sprint start...")
        
        # Dictionary to store scope hours per developer
        scope_by_developer = {}
        # List to store detailed task information
        scope_details = []
        
        # Target statuses for scope
        scope_statuses = ['to do', 'in progress', 'backlog']
        tasks_in_scope = 0
        
        for issue in all_issues:
            fields = issue.get('fields', {})
            issue_key = issue.get('key', '')
            
            # Determine status at sprint start
            status_at_start = self._get_status_at_sprint_start(issue, sprint_start)
            
            # Check if task was in scope statuses at sprint start
            if status_at_start and status_at_start.lower() in scope_statuses:
                tasks_in_scope += 1
                
                # Extract task details
                summary = fields.get('summary', '')
                issue_type = fields.get('issuetype', {}).get('name', '')
                current_status = fields.get('status', {}).get('name', '')
                
                # Get responsible developer
                responsible = fields.get(CUSTOM_FIELDS['responsible'])
                responsible_name = responsible.get('displayName', 'Unassigned') if responsible else 'Unassigned'

                # Skip if developer not in selected list
                if selected_developers and responsible_name not in selected_developers:
                    continue
                
                # Get assignee
                assignee = fields.get('assignee')
                assignee_name = assignee.get('displayName', '') if assignee else ''
                
                # Get original estimate
                original_estimate = fields.get('timeoriginalestimate', 0) or 0
                original_estimate_hours = original_estimate / 3600 if original_estimate else 0
                
                # Get labels
                labels = fields.get('labels', [])
                
                # Get created date
                created = fields.get('created', '')
                
                # Add to developer's total
                if responsible_name not in scope_by_developer:
                    scope_by_developer[responsible_name] = 0
                scope_by_developer[responsible_name] += original_estimate_hours
                
                # Add to details list
                scope_details.append({
                    'Issue Key': issue_key,
                    'Summary': summary,
                    'Issue Type': issue_type,
                    'Current Status': current_status,
                    'Status at Sprint Start': status_at_start,
                    'Responsible': responsible_name,
                    'Assignee': assignee_name,
                    'Original Estimate (hours)': round(original_estimate_hours, 2),
                    'Labels': ', '.join(labels),
                    'Created': created
                })
        
        print(f"✅ Found {tasks_in_scope} tasks in scope statuses (To Do, In Progress, Backlog) at sprint start")
        return scope_by_developer, scope_details
    
    def _get_status_at_sprint_start(self, issue, sprint_start):
        """Get the status of an issue at sprint start time"""
        if not sprint_start:
            return None
            
        fields = issue.get('fields', {})
        changelog = issue.get('changelog', {})
        
        # If no changelog, use current status if issue was created before sprint start
        if not changelog or not changelog.get('histories'):
            created_date = self._parse_sprint_date(fields.get('created'))
            if created_date and created_date < sprint_start:
                return fields.get('status', {}).get('name', '')
            return None
        
        # Sort histories by date (oldest first)
        histories = sorted(changelog['histories'], 
                         key=lambda h: self._parse_sprint_date(h.get('created')) or datetime.min)
        
        # Find the last status before or at sprint start
        last_status = None
        
        # Check if issue existed before sprint start
        first_history_date = self._parse_sprint_date(histories[0].get('created'))
        if first_history_date and first_history_date > sprint_start:
            # Issue was created after sprint start
            return None
        
        # Go through history to find status at sprint start
        for history in histories:
            history_date = self._parse_sprint_date(history.get('created'))
            if not history_date:
                continue
                
            # If this change happened after sprint start, we're done
            if history_date > sprint_start:
                break
                
            # Look for status changes in this history entry
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    last_status = item.get('toString', '')
        
        # If no status change found before sprint start, check initial status
        if last_status is None:
            # Check the first history entry for initial status
            for history in histories:
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        # This gives us the "from" status of the first status change
                        last_status = item.get('fromString', '')
                        break
                if last_status:
                    break
            
            # If still no status found, use current status
            if last_status is None:
                last_status = fields.get('status', {}).get('name', '')
        
        return last_status

    def _calculate_performance(self, completed_data, scope_data):
        """Calculate performance metrics for each developer"""
        
        # Get all developers from both datasets
        all_developers = set(completed_data.keys()) | set(scope_data.keys())
        
        # Calculate performance for each developer
        performance_data = []
        for developer in sorted(all_developers):  # Sort alphabetically
            completed_hours = completed_data.get(developer, 0)
            scope_hours = scope_data.get(developer, 0)
            
            # Calculate completed percentage
            if scope_hours > 0:
                completed_percentage = (completed_hours / scope_hours) * 100
            else:
                completed_percentage = 0
            
            performance_data.append({
                'Responsible': developer,
                'Completed Tasks (hours)': round(completed_hours, 2),
                'Scope Tasks (hours)': round(scope_hours, 2),
                'Completed %': round(completed_percentage, 1)
            })
        
        return performance_data

    def _generate_reports(self, project_key, sprint_name, performance_data, completed_details, scope_details):
        """Generate CSV reports"""
        if not performance_data:
            print("⚠️  No data to export")
            return
        
        print(f"\n📁 FILE EXPORT:")
        
        # 1. Summary report (existing format)
        df_summary = pd.DataFrame(performance_data)
        csv_filename_summary = self.generate_output_filename("devs_performance_summary", project_key, sprint_name, "csv")
        csv_path_summary = self.get_output_path("reports", csv_filename_summary)
        df_summary.to_csv(csv_path_summary, index=False, encoding='utf-8-sig')
        print(f"   📊 Performance Summary CSV: {csv_path_summary}")

        # 2. Completed tasks details report
        if completed_details:
            df_completed = pd.DataFrame(completed_details)
            # Sort by Responsible and then by Issue Key
            df_completed = df_completed.sort_values(['Responsible', 'Issue Key'])
            csv_filename_completed = self.generate_output_filename("devs_performance_completed_details", project_key, sprint_name, "csv")
            csv_path_completed = self.get_output_path("reports", csv_filename_completed)
            df_completed.to_csv(csv_path_completed, index=False, encoding='utf-8-sig')
            print(f"   ✅ Completed Tasks Details CSV: {csv_path_completed}")

        # 3. Scope tasks details report
        if scope_details:
            df_scope = pd.DataFrame(scope_details)
            # Sort by Responsible and then by Issue Key
            df_scope = df_scope.sort_values(['Responsible', 'Issue Key'])
            csv_filename_scope = self.generate_output_filename("devs_performance_scope_details", project_key, sprint_name, "csv")
            csv_path_scope = self.get_output_path("reports", csv_filename_scope)
            df_scope.to_csv(csv_path_scope, index=False, encoding='utf-8-sig')
            print(f"   📋 Scope Tasks Details CSV: {csv_path_scope}")

    def _print_summary(self, performance_data, project_key, sprint_name):
        """Print summary in terminal"""
        if not performance_data:
            print(f"\n📊 No performance data found")
            return
        
        print(f"\n📊 DEVELOPERS PERFORMANCE SUMMARY:")
        print(f"   • Project: {project_key}")
        print(f"   • Sprint: {sprint_name}")
        print(f"\n   Developer Performance:")
        
        # Print header
        print(f"   {'Responsible':<30} {'Completed (h)':<15} {'Scope (h)':<15} {'Completed %':<12}")
        print(f"   {'-'*30} {'-'*15} {'-'*15} {'-'*12}")
        
        # Print each developer's data
        total_completed = 0
        total_scope = 0
        
        for dev_data in performance_data:
            responsible = dev_data['Responsible']
            completed = dev_data['Completed Tasks (hours)']
            scope = dev_data['Scope Tasks (hours)']
            percentage = dev_data['Completed %']
            
            print(f"   {responsible:<30} {completed:<15.1f} {scope:<15.1f} {percentage:<12.1f}%")
            
            total_completed += completed
            total_scope += scope
        
        # Print totals
        print(f"   {'-'*30} {'-'*15} {'-'*15} {'-'*12}")
        total_percentage = (total_completed / total_scope * 100) if total_scope > 0 else 0
        print(f"   {'TOTAL':<30} {total_completed:<15.1f} {total_scope:<15.1f} {total_percentage:<12.1f}%")

def main():
    """Main function running the tool"""
    tool = DevsPerformanceTool()
    tool.safe_run()

if __name__ == "__main__":
    main()