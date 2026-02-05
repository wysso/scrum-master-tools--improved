"""
Test Responsible Field - Testing the responsible field configuration
Helper script for testing and identifying the correct responsible field in Jira
Author: Marek Mróz <marek@mroz.consulting>
"""
import sys
import os
import requests
import json

# Add path to main project directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from config.jira_config import JIRA_CONFIG, CUSTOM_FIELDS

def test_responsible_field():
    """Test the responsible field configuration"""
    print("🧪 Testing responsible field configuration")
    print("=" * 50)

    # Test configuration
    print(f"🔗 Jira URL: {JIRA_CONFIG['base_url']}")
    print(f"🔑 Personal Token: {'*' * len(JIRA_CONFIG['personal_token']) if JIRA_CONFIG['personal_token'] else 'NOT SET'}")
    print(f"🏷️  Responsible field: {CUSTOM_FIELDS.get('responsible', 'NOT SET')}")

    # Test connection and get specific issue
    print(f"\n🔍 Testing with issue TMM-299...")

    try:
        # Get issue TMM-299
        url = f"{JIRA_CONFIG['base_url']}/rest/api/2/issue/TMM-299"
        headers = {
            'Authorization': f"Bearer {JIRA_CONFIG['personal_token']}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            fields = data.get('fields', {})
            
            print(f"✅ Successfully retrieved issue TMM-299")
            print(f"📝 Title: {fields.get('summary', 'None')}")
            
            # Test responsible field
            responsible_field_id = CUSTOM_FIELDS.get('responsible')
            if responsible_field_id and responsible_field_id in fields:
                responsible_value = fields[responsible_field_id]
                
                if responsible_value:
                    if isinstance(responsible_value, dict):
                        responsible_name = responsible_value.get('displayName', responsible_value.get('name', str(responsible_value)))
                        print(f"✅ Responsible field value: {responsible_name}")
                        print(f"    (full object: {responsible_value})")
                    else:
                        print(f"✅ Responsible field value: {responsible_value}")
                    
                    print("\n🎉 SUCCESS! The 'responsible' field was found and correctly retrieved!")
                    return True
                else:
                    print(f"⚠️  Responsible field exists but is empty")
            else:
                print(f"❌ Responsible field '{responsible_field_id}' not found in issue fields")
                
                print(f"\n🔍 Checking custom fields that might be 'responsible':")
                for field_id, field_value in fields.items():
                    if field_id.startswith('customfield_') and field_value:
                        if isinstance(field_value, dict) and 'displayName' in field_value:
                            print(f"  • {field_id}: {field_value.get('displayName', '')}")
                            
                            # Check if this might be customfield_11000
                            if field_id == 'customfield_11000':
                                print("\n✅ FOUND! customfield_11000 might be the 'responsible' field!")
                                print(f"    Value: {field_value.get('displayName', '')}")
                                print(f"    (text value: {field_value})")
                                
                                # Update config suggestion
                                print(f"\n💡 SUGGESTION: Update your config/jira_config.py:")
                                print(f"    CUSTOM_FIELDS = {{")
                                print(f"        'responsible': 'customfield_11000',")
                                print(f"        # ... other fields")
                                print(f"    }}")
                                return True
                        elif isinstance(field_value, str) and field_value.strip():
                            print(f"  • {field_id}: {field_value}")
        else:
            print(f"❌ Error retrieving issue TMM-299: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_issues():
    """Test responsible field on multiple issues"""
    if test_responsible_field():
        print("\n✅ Test completed successfully - found responsible field!")
        return
    
    print("\n🔍 Checking other issues in TMM project...")
    
    try:
        # Search for issues with responsible field
        responsible_field_id = CUSTOM_FIELDS.get('responsible', 'customfield_11000')
        
        url = f"{JIRA_CONFIG['base_url']}/rest/api/2/search"
        headers = {
            'Authorization': f"Bearer {JIRA_CONFIG['personal_token']}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # JQL to find issues with responsible field
        jql = f'project = "TMM" AND "{responsible_field_id}" is not EMPTY'
        
        params = {
            'jql': jql,
            'maxResults': 5,
            'fields': f'summary,{responsible_field_id}'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            
            if issues:
                print(f"✅ Found {len(data['issues'])} issues with filled 'responsible' field:")
                
                for issue in issues:
                    issue_key = issue.get('key', '')
                    fields = issue.get('fields', {})
                    responsible_value = fields.get(responsible_field_id)
                    
                    print(f"  • {issue_key}")
                    if isinstance(responsible_value, dict):
                        print(f"    Responsible: {responsible_value.get('displayName', '')}")
                    else:
                        print(f"    Responsible: {responsible_value}")
                    print(f"    Title: {fields.get('summary', '')[:60]}...")
                
                print("✅ Test completed successfully - found issues with 'responsible' field!")
            else:
                print("❌ No issues found with filled 'responsible' field")
                
                # Try with customfield_11000
                print("\n🔍 Checking issues with customfield_11000...")
                
                jql_custom = 'project = "TMM" AND customfield_11000 is not EMPTY'
                params_custom = {
                    'jql': jql_custom,
                    'maxResults': 5,
                    'fields': 'summary,customfield_11000'
                }
                
                response_custom = requests.get(url, headers=headers, params=params_custom)
                
                if response_custom.status_code == 200:
                    data_custom = response_custom.json()
                    issues_custom = data_custom.get('issues', [])
                    
                    if issues_custom:
                        print(f"✅ Found {len(data_custom['issues'])} issues with customfield_11000:")
                        
                        for issue in issues_custom:
                            issue_key = issue.get('key', '')
                            fields = issue.get('fields', {})
                            custom_value = fields.get('customfield_11000')
                            
                            print(f"  • {issue_key}")
                            if isinstance(custom_value, dict):
                                print(f"    customfield_11000: {custom_value.get('displayName', '')}")
                            else:
                                print(f"    customfield_11000: {custom_value}")
                        
                        print("✅ customfield_11000 can be used as 'responsible' field!")
        else:
            print(f"❌ Error searching issues: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_multiple_issues()