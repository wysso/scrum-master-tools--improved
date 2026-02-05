"""
Projects Lister - List of Jira projects
Helper tool for listing and exploring available Jira projects
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

logger = logging.getLogger(__name__)

class ProjectsListerTool(BaseScrumMasterTool):
    """Tool for listing Jira projects"""
    
    def __init__(self):
        super().__init__("List of Jira projects")

    def run(self):
        """Main method listing projects"""
        print("📋 List of Jira projects")
        print("=" * 30)
        
        try:
            # Get all projects
            print("\n🔍 Fetching project list...")
            projects = self.jira_client.get_projects()
            
            if not projects:
                print("❌ No projects found or insufficient permissions")
                return
            
            print(f"✅ Found {len(projects)} projects")
            
            # Sort projects by key
            projects.sort(key=lambda x: x['key'])
            
            # Display projects
            self._display_projects(projects)
            
            # Interactive menu
            self._interactive_menu(projects)
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            print(f"❌ Error listing projects: {e}")

    def _display_projects(self, projects):
        """Display project list"""
        print(f"\n📋 Available projects:")
        print("-" * 80)
        print(f"{'No.':<4} {'Key':<10} {'Name':<40} {'Type':<15}")
        print("-" * 80)
        
        for i, project in enumerate(projects, 1):
            project_key = project.get('key', 'N/A')
            project_name = project.get('name', 'N/A')
            project_type = project.get('projectTypeKey', 'N/A')
            
            # Truncate long names
            if len(project_name) > 37:
                project_name = project_name[:34] + "..."
            
            print(f"{i:<4} {project_key:<10} {project_name:<40} {project_type:<15}")
        
        print("-" * 80)

    def _interactive_menu(self, projects):
        """Show details of selected projects"""
        while True:
            print(f"\n🔧 Options:")
            print("1. Show project details")
            print("2. Save project list to file")
            print("3. Exit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                self._show_project_details(projects)
            elif choice == '2':
                self._save_projects_to_file(projects)
            elif choice == '3':
                break
            else:
                print("❌ Invalid option. Please select 1-3.")

    def _show_project_details(self, projects):
        """Show details of single project"""
        print(f"\nAvailable projects:")
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project['key']} - {project['name']}")
        
        try:
            choice = input(f"\nSelect project number (1-{len(projects)}): ").strip()
            project_index = int(choice) - 1
            
            if 0 <= project_index < len(projects):
                project = projects[project_index]
                self._display_project_details(project)
            else:
                print("❌ Invalid project number")
                
        except ValueError:
            print("❌ Please enter a valid number")

    def _display_project_details(self, project):
        """Show details of single project"""
        print(f"\n📊 PROJECT DETAILS:")
        print("=" * 50)
        print(f"Key: {project.get('key', 'N/A')}")
        print(f"Name: {project.get('name', 'N/A')}")
        print(f"Description: {project.get('description', 'No description')}")
        print(f"Project Type: {project.get('projectTypeKey', 'N/A')}")
        print(f"Lead: {project.get('lead', {}).get('displayName', 'N/A')}")
        
        # Additional project info
        try:
            project_key = project.get('key')
            if project_key:
                # Get project details from Jira
                jira_project = self.jira_client.jira.project(project_key)
                
                print(f"URL: {jira_project.self}")
                print(f"Avatar URL: {jira_project.avatarUrls.get('48x48', 'N/A')}")
                
                # Get project components
                if hasattr(jira_project, 'components') and jira_project.components:
                    print(f"Components: {len(jira_project.components)}")
                    for comp in jira_project.components[:5]:  # Show first 5
                        print(f"  • {comp.name}")
                    if len(jira_project.components) > 5:
                        print(f"  ... and {len(jira_project.components) - 5} more")
                
                # Get project versions
                if hasattr(jira_project, 'versions') and jira_project.versions:
                    print(f"Versions: {len(jira_project.versions)}")
                    for version in jira_project.versions[-3:]:  # Show last 3
                        print(f"  • {version.name}")
                
        except Exception as e:
            logger.warning(f"Could not get additional details for project {project.get('key')}: {e}")
        
        print("=" * 50)

    def _save_projects_to_file(self, projects):
        """Save project list to file"""
        try:
            # Generate filename
            filename = self.generate_output_filename("jira_projects", "", "", "json")
            file_path = self.get_output_path("reports", filename)
            
            # Prepare data
            output_data = {
                'export_date': self.get_current_timestamp(),
                'total_projects': len(projects),
                'projects': projects
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Project list saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving projects to file: {e}")
            print(f"❌ Error saving to file: {e}")

def main():
    """Main function running the tool"""
    tool = ProjectsListerTool()
    tool.safe_run()

if __name__ == "__main__":
    main()