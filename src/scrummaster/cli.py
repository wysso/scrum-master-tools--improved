"""
ScrumMaster CLI - Command Line Interface for ScrumMaster tools
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import logging

# Add path to main project directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Handle imports for different execution methods
try:
    # Try relative imports (when run as module)
    # Main tools
    from .tools.sprint_completion import SprintCompletionTool
    from .tools.worklog_summary import WorklogSummaryTool
    from .tools.anomaly_detector import AnomalyDetectorTool
    from .tools.planning import PlanningTool
    from .tools.issue_type_summary import IssueTypeSummaryTool
    from .tools.devs_performance import DevsPerformanceTool

    # Helper tools
    from .helpers.connection_test import ConnectionTestTool
    from .helpers.projects_lister import ProjectsListerTool
    from .helpers.label_updater import LabelUpdaterTool
    from .helpers.components_updater import ComponentsUpdaterTool
    from .helpers.responsible_field_updater import ResponsibleFieldUpdaterTool
    from .helpers.test_responsible_field import test_responsible_field
    from .helpers.custom_fields_identifier import CustomFieldsIdentifierTool
except ImportError:
    # Fallback to absolute imports (when run directly)
    # Main tools
    from src.scrummaster.tools.sprint_completion import SprintCompletionTool
    from src.scrummaster.tools.worklog_summary import WorklogSummaryTool
    from src.scrummaster.tools.anomaly_detector import AnomalyDetectorTool
    from src.scrummaster.tools.planning import PlanningTool
    from src.scrummaster.tools.issue_type_summary import IssueTypeSummaryTool
    from src.scrummaster.tools.devs_performance import DevsPerformanceTool

    # Helper tools
    from src.scrummaster.helpers.connection_test import ConnectionTestTool
    from src.scrummaster.helpers.projects_lister import ProjectsListerTool
    from src.scrummaster.helpers.label_updater import LabelUpdaterTool
    from src.scrummaster.helpers.components_updater import ComponentsUpdaterTool
    from src.scrummaster.helpers.responsible_field_updater import ResponsibleFieldUpdaterTool
    from src.scrummaster.helpers.test_responsible_field import test_responsible_field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ScrumMasterCLI:
    """Main CLI interface for ScrumMaster tools"""
    
    def __init__(self):
        """Initialize CLI with available tools"""
        self.tools = {
            # Main ScrumMaster tools
            'sprint-completion': {
                'name': 'Sprint Completion Analysis',
                'description': 'Analyze completed tasks during sprint',
                'class': SprintCompletionTool,
                'category': 'main'
            },
            'worklog-summary': {
                'name': 'Worklog Summary',
                'description': 'Summarize work logs in sprint',
                'class': WorklogSummaryTool,
                'category': 'main'
            },
            'issue-type-summary': {
                'name': 'Issue Type Summary',
                'description': 'Summarize time spent by issue type (Task, Sub-task, Bug, Sub-Bug)',
                'class': IssueTypeSummaryTool,
                'category': 'main'
            },
            'anomaly-detector': {
                'name': 'Anomaly Detector',
                'description': 'Detect anomalies in sprint data',
                'class': AnomalyDetectorTool,
                'category': 'main'
            },
            'planning': {
                'name': 'Planning Analysis',
                'description': 'Analyze sprint planning quality',
                'class': PlanningTool,
                'category': 'main'
            },
            'devs-performance': {
                'name': 'Developers Performance',
                'description': 'Analyze developers performance',
                'class': DevsPerformanceTool,
                'category': 'main'
            },

            # Helper tools
            'connection-test': {
                'name': 'Connection Test',
                'description': 'Test connection to Jira API',
                'class': ConnectionTestTool,
                'category': 'helper'
            },
            'projects-list': {
                'name': 'Projects List',
                'description': 'List available Jira projects',
                'class': ProjectsListerTool,
                'category': 'helper'
            },
            'label-updater': {
                'name': 'Label Updater',
                'description': 'Update labels in Jira issues',
                'class': LabelUpdaterTool,
                'category': 'helper'
            },
            'components-updater': {
                'name': 'Components Updater',
                'description': 'Update components based on JQL',
                'class': ComponentsUpdaterTool,
                'category': 'helper'
            },
            'custom-fields': {
                'name': 'Custom Fields Identifier',
                'description': 'Identify custom fields in Jira',
                'class': CustomFieldsIdentifierTool,
                'category': 'helper'
            },
            'responsible-updater': {
                'name': 'Responsible Field Updater',
                'description': 'Auto-update responsible field in tasks',
                'class': ResponsibleFieldUpdaterTool,
                'category': 'helper'
            },
            'test-responsible': {
                'name': 'Test Responsible Field',
                'description': 'Test responsible field configuration',
                'class': None,  # Special case - function not class
                'category': 'helper'
            }
        }

    def show_main_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("🚀 ScrumMaster Tools 2.11.1 (SMT)")
        print("="*60)
        print("Advanced tools for analyzing Jira data")
        print("for Scrum Masters and development teams")
        print("💡 Quick access: python smt.py")
        print("="*60)

        # Main tools
        print("\n📊 MAIN SCRUMMASTER TOOLS:")
        main_tools = {k: v for k, v in self.tools.items() if v['category'] == 'main'}
        current_num = 1
        for key, tool in main_tools.items():
            print(f"  {current_num}. {tool['name']}")
            print(f"     {tool['description']}")
            current_num += 1

        # Bulk Operations tools
        print(f"\n🔄 BULK OPERATIONS:")
        bulk_tools = {k: v for k, v in self.tools.items() if k in ['components-updater', 'label-updater']}
        for key, tool in bulk_tools.items():
            print(f"  {current_num}. {tool['name']}")
            print(f"     {tool['description']}")
            current_num += 1

        # Helper tools (excluding bulk operations tools)
        print(f"\n🔧 HELPER TOOLS:")
        helper_tools = {k: v for k, v in self.tools.items() if v['category'] == 'helper' and k not in ['components-updater', 'label-updater']}
        for key, tool in helper_tools.items():
            print(f"  {current_num}. {tool['name']}")
            print(f"     {tool['description']}")
            current_num += 1

        print(f"\n  0. Exit")
        print("="*60)

    def get_user_choice(self):
        """Get user choice from menu"""
        max_choice = len(self.tools)
        
        while True:
            try:
                choice = input(f"\nSelect tool (0-{max_choice}): ").strip()
                
                if choice == '0':
                    return 0
                
                choice_num = int(choice)
                if 1 <= choice_num <= max_choice:
                    return choice_num
                else:
                    print(f"❌ Invalid choice. Please select 0-{max_choice}.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return 0

    def run_tool(self, choice):
        """Run selected tool"""
        # Create ordered list matching menu display order
        main_tools = [(k, v) for k, v in self.tools.items() if v['category'] == 'main']
        bulk_tools = [(k, v) for k, v in self.tools.items() if k in ['components-updater', 'label-updater']]
        helper_tools = [(k, v) for k, v in self.tools.items() if v['category'] == 'helper' and k not in ['components-updater', 'label-updater']]

        tools_list = main_tools + bulk_tools + helper_tools
        tool_key, tool_info = tools_list[choice - 1]
        
        print(f"\n🔄 Running: {tool_info['name']}")
        print("-" * 50)
        
        try:
            if tool_key == 'test-responsible':
                # Special case for test function
                test_responsible_field()
            else:
                # Regular tool class
                tool_class = tool_info['class']
                tool_instance = tool_class()
                tool_instance.safe_run()
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Tool '{tool_info['name']}' interrupted by user")
        except Exception as e:
            print(f"\n❌ Error running tool '{tool_info['name']}': {e}")
            logging.error(f"Error in tool {tool_key}: {e}")

    def run(self):
        """Main CLI loop"""
        try:
            while True:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice == 0:
                    print("\n👋 Thank you for using ScrumMaster Tools!")
                    break
                
                self.run_tool(choice)
                
                # Ask if user wants to continue
                print("\n" + "-" * 50)
                continue_choice = input("Do you want to run another tool? (Y/n): ").strip().lower()
                if continue_choice in ['n', 'no']:
                    print("\n👋 Thank you for using ScrumMaster Tools!")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            logging.error(f"CLI error: {e}")

def main():
    """Main entry point"""
    cli = ScrumMasterCLI()
    cli.run()

if __name__ == "__main__":
    main()