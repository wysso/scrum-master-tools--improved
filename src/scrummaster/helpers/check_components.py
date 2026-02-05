"""
Helper tool to check components field structure in Jira
Author: Assistant
"""
import sys
import os

# Add path to main project directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.scrummaster.core.jira_client import JiraClient
import json


def check_components_structure():
    """Check how components field looks in different projects"""
    jira_client = JiraClient()
    
    print("🔍 Components Field Structure Checker")
    print("=" * 50)
    
    # Get project key from user
    project_key = input("📝 Enter project key (e.g. TMM): ").strip()
    
    if not project_key:
        print("❌ Project key cannot be empty!")
        return
    
    # Validate project
    validated_key = jira_client.validate_project_key(project_key)
    if not validated_key:
        print(f"❌ Project '{project_key}' does not exist or you don't have permissions!")
        return
    
    print(f"\n🎯 Checking project: {validated_key}")
    
    # Build JQL to get sample issues
    jql = f'project = "{validated_key}" ORDER BY created DESC'
    
    # Define fields to retrieve
    fields = ['key', 'summary', 'components', 'labels', 'issuetype', 'status']
    
    print(f"📊 Fetching sample issues...")

    # Get sample issues (limit to 10)
    issues_response = jira_client.search_issues(jql, fields=fields, max_results=10)

    # Extract issues from response
    if isinstance(issues_response, dict) and 'issues' in issues_response:
        issues = issues_response['issues']
    else:
        issues = []

    if not issues:
        print(f"❌ No issues found in project '{validated_key}'")
        return
    
    print(f"\n✅ Found {len(issues)} issues. Analyzing components structure...\n")
    
    # Analyze each issue
    for i, issue in enumerate(issues, 1):
        issue_key = issue.get('key', '')
        fields_data = issue.get('fields', {})
        
        print(f"\n{i}. Issue: {issue_key}")
        print(f"   Summary: {fields_data.get('summary', 'N/A')[:50]}...")
        print(f"   Type: {fields_data.get('issuetype', {}).get('name', 'N/A')}")
        print(f"   Status: {fields_data.get('status', {}).get('name', 'N/A')}")
        
        # Check components
        components = fields_data.get('components', [])
        print(f"   Components ({len(components)}):")
        if components:
            for comp in components:
                print(f"      - Name: {comp.get('name', 'N/A')}")
                print(f"        ID: {comp.get('id', 'N/A')}")
                if 'description' in comp and comp['description']:
                    print(f"        Description: {comp['description']}")
        else:
            print("      (no components)")
        
        # Check labels for comparison
        labels = fields_data.get('labels', [])
        print(f"   Labels ({len(labels)}): {', '.join(labels) if labels else '(no labels)'}")
    
    # Summary statistics
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")

    components_count = {}
    labels_count = {}
    issues_with_components = 0
    issues_with_labels = 0

    # Re-fetch more issues for statistics
    all_issues = jira_client.get_all_results(jql, fields)
    all_issues_response = jira_client.search_issues(jql, fields, max_results=100)

    # Extract issues from response
    if isinstance(all_issues_response, dict) and 'issues' in all_issues_response:
        all_issues = all_issues_response['issues']
    else:
        all_issues = []
    all_issues = jira_client.get_all_results(jql, fields, max_results=100)
    
    for issue in all_issues:
        fields_data = issue.get('fields', {})
        components = fields_data.get('components', [])
        labels = fields_data.get('labels', [])
        
        if components:
            issues_with_components += 1
            for comp in components:
                comp_name = comp.get('name', 'Unknown')
                components_count[comp_name] = components_count.get(comp_name, 0) + 1
        
        if labels:
            issues_with_labels += 1
            for label in labels:
                labels_count[label] = labels_count.get(label, 0) + 1
    
    print(f"\nTotal issues analyzed: {len(all_issues)}")
    print(f"Issues with components: {issues_with_components} ({issues_with_components/len(all_issues)*100:.1f}%)")
    print(f"Issues with labels: {issues_with_labels} ({issues_with_labels/len(all_issues)*100:.1f}%)")
    
    print("\n🏷️  Most common components:")
    for comp, count in sorted(components_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {comp}: {count} issues")
    
    print("\n🏷️  Most common labels:")
    for label, count in sorted(labels_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {label}: {count} issues")
    
    # Save raw data for analysis
    output_file = f"components_analysis_{validated_key}.json"
    output_data = {
        "project": validated_key,
        "total_issues": len(all_issues),
        "issues_with_components": issues_with_components,
        "issues_with_labels": issues_with_labels,
        "components_count": components_count,
        "labels_count": labels_count,
        "sample_issues": issues[:5]  # Save first 5 issues as samples
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {output_file}")


if __name__ == "__main__":
    check_components_structure()