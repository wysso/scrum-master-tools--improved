"""
Connection Test Tool - Testing connection to Jira
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import logging

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

class ConnectionTestTool(BaseScrumMasterTool):
    """Tool for testing connection to Jira"""
    
    def __init__(self):
        super().__init__("Testing connection to Jira")

    def run(self):
        """Main method testing connection"""
        print("\n🔗 Testing connection to Jira...")
        
        try:
            # Test basic connection
            print("1. Testing basic authentication...")
            user_info = self.jira_client.test_connection()
            display_name = user_info.get('displayName', 'Unknown User')
            email = user_info.get('emailAddress', user_info.get('name', 'No email'))
            print(f"   ✅ Successfully authenticated as: {display_name} ({email})")

            # Test projects access
            print("2. Testing projects access...")
            projects = self.jira_client.get_projects()
            print(f"   ✅ Access to {len(projects)} projects")

            # Show first few projects
            if projects:
                print("   📋 Available projects (first 5):")
                for project in projects[:5]:
                    print(f"      • {project['key']}: {project['name']}")

            # Test search functionality
            print("3. Testing search functionality...")
            test_jql = "project is not EMPTY ORDER BY created DESC"
            test_results = self.jira_client.execute_jql(test_jql, max_results=1)

            issues = test_results.get("issues", [])
            total = test_results.get("total")

            if total is not None:
                print(f"   ✅ Search functionality working (found {total} total issues)")
            else:
                print(f"   ✅ Search functionality working (retrieved {len(issues)} issue(s) on test query)")

            
            print(f"\n🎉 All connection tests passed successfully!")
            print(f"   Your Jira connection is working properly.")
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            print(f"\n❌ Connection test failed!")
            print(f"   Error: {e}")
            print(f"\n🔧 Troubleshooting tips:")
            print(f"   1. Check your Jira URL in config/jira_config.py")
            print(f"   2. Verify your API token is correct")
            print(f"   3. Make sure your email address is correct")
            print(f"   4. Check if your Jira instance is accessible")
            print(f"   5. Verify you have proper permissions")

def main():
    """Main function running the tool"""
    tool = ConnectionTestTool()
    tool.safe_run()

if __name__ == "__main__":
    main()