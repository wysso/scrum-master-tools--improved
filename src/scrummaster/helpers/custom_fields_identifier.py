"""
Custom Fields Identifier Tool - Identification of custom fields in Jira
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import json
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

class CustomFieldsIdentifierTool(BaseScrumMasterTool):
    """Tool for identifying custom fields in Jira"""
    
    def __init__(self):
        super().__init__("Identification of custom fields in Jira")

    def run(self):
        """Main method identifying custom fields"""
        # Get project
        project_key = self.get_project_key()
        
        print(f"\n🔍 Identifying custom fields for project: {project_key}")
        
        # Get custom fields
        custom_fields = self._get_custom_fields(project_key)
        
        # Display results
        self._display_results(custom_fields, project_key)
        
        # Save to file
        self._save_results(custom_fields, project_key)

    def _get_custom_fields(self, project_key):
        """Get all custom fields from Jira"""
        print("🚀 Fetching custom fields from Jira...")

        try:
            # Get all fields from Jira using our JiraClient method
            all_fields = self.jira_client.get_fields()

            # Filter custom fields (they start with 'customfield_')
            custom_fields = []
            for field in all_fields:
                if field['id'].startswith('customfield_'):
                    # Check usage in project
                    usage_count = self._get_field_usage_in_project(project_key, field['id'])

                    custom_fields.append({
                        'id': field['id'],
                        'name': field['name'],
                        'type': field.get('schema', {}).get('type', 'unknown'),
                        'custom': field.get('custom', True),
                        'searchable': field.get('searchable', False),
                        'usage_count': usage_count,
                        'value_types': [],
                        'sample_values': []
                    })

            print(f"✅ Found {len(custom_fields)} custom fields")
            return custom_fields

        except Exception as e:
            logger.error(f"Error fetching custom fields: {e}")
            print(f"❌ Error fetching custom fields: {e}")
            return []

    def _get_field_usage_in_project(self, project_key, field_id):
        """Check if custom field is used in specific project"""
        try:
            # Try to search for issues with this field using our JiraClient
            jql = f'project = "{project_key}" AND "{field_id}" is not EMPTY'

            # Execute search with limit 1 to check if field is used
            results = self.jira_client.search_issues(jql, fields=['key'], max_results=1)
            return len(results.get('issues', [])) if results else 0

        except Exception as e:
            # If search fails, field might not be available for this project
            logger.debug(f"Could not check usage for field {field_id}: {e}")
            return 0

    def _display_results(self, custom_fields, project_key):
        """Display analysis results"""
        if not custom_fields:
            print("⚠️  No custom fields found")
            return
        
        print(f"\n📊 CUSTOM FIELDS ANALYSIS:")
        print(f"   • Project: {project_key}")
        print(f"   • Total custom fields: {len(custom_fields)}")

        print(f"\n📋 Custom fields list:")
        for i, field in enumerate(custom_fields, 1):
            print(f"   {i:2d}. {field['name']}")
            print(f"       ID: {field['id']}")
            print(f"       Type: {field.get('type', 'unknown')}")
            print(f"       Searchable: {'Yes' if field['searchable'] else 'No'}")
            print(f"       Usage count: {field.get('usage_count', 0)}")
            print()
            print()
        
        # Group by common patterns
        print(f"\n🏷️  Common field patterns:")
        patterns = {}
        for field in custom_fields:
            name_lower = field['name'].lower()
            if 'story' in name_lower or 'epic' in name_lower:
                patterns.setdefault('Story/Epic fields', []).append(field['name'])
            elif 'time' in name_lower or 'date' in name_lower:
                patterns.setdefault('Time/Date fields', []).append(field['name'])
            elif 'team' in name_lower or 'responsible' in name_lower or 'assignee' in name_lower:
                patterns.setdefault('Team/People fields', []).append(field['name'])
            elif 'priority' in name_lower or 'severity' in name_lower:
                patterns.setdefault('Priority/Severity fields', []).append(field['name'])
            else:
                patterns.setdefault('Other fields', []).append(field['name'])
        
        for pattern, fields in patterns.items():
            print(f"   • {pattern}: {len(fields)}")
            for field_name in fields[:3]:  # Show first 3
                print(f"     - {field_name}")
            if len(fields) > 3:
                print(f"     ... and {len(fields) - 3} more")
            print()

    def _save_results(self, custom_fields, project_key):
        """Save results to JSON file"""
        if not custom_fields:
            return

        # Generate filename
        filename = self.generate_output_filename("custom_fields_mapping", project_key, "", "json")
        file_path = self.get_output_path("reports", filename)

        # Prepare data for saving
        from datetime import datetime
        output_data = {
            'project': project_key,
            'analysis_date': datetime.now().isoformat(),
            'total_custom_fields': len(custom_fields),
            'custom_fields': custom_fields,
            'field_mapping_suggestions': self._generate_mapping_suggestions(custom_fields)
        }

        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n📁 FILE EXPORT:")
        print(f"   📄 Custom fields mapping: {file_path}")

    def _generate_mapping_suggestions(self, custom_fields):
        """Generate suggestions for field mapping based on field names"""
        suggestions = {}
        
        for field in custom_fields:
            name_lower = field['name'].lower()
            field_id = field['id']
            
            # Suggest mappings based on common patterns
            if 'responsible' in name_lower or 'odpowiedzialny' in name_lower:
                suggestions['responsible'] = {
                    'field_id': field_id,
                    'field_name': field['name'],
                    'confidence': 'high'
                }
            elif 'story point' in name_lower or 'punkt' in name_lower:
                suggestions['story_points'] = {
                    'field_id': field_id,
                    'field_name': field['name'],
                    'confidence': 'high'
                }
            elif 'epic' in name_lower and 'link' in name_lower:
                suggestions['epic_link'] = {
                    'field_id': field_id,
                    'field_name': field['name'],
                    'confidence': 'medium'
                }
            elif 'sprint' in name_lower:
                suggestions['sprint'] = {
                    'field_id': field_id,
                    'field_name': field['name'],
                    'confidence': 'medium'
                }
        
        return suggestions

def main():
    """Main function running the tool"""
    tool = CustomFieldsIdentifierTool()
    tool.safe_run()

if __name__ == "__main__":
    main()