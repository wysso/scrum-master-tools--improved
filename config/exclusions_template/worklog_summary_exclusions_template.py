"""
Template for Worklog Summary Tool exclusions configuration
Copy this file to ../exclusions/worklog_summary_exclusions.py and customize
"""

# Exclusions for Worklog Summary Tool
# Format: 'PROJECT_KEY': ['ISSUE-ID1', 'ISSUE-ID2', ...]
EXCLUSIONS = {
    'TMM': [
        # Example exclusions for TMM project
        # 'TMM-1222',  # Administrative task
        # 'TMM-333',   # Meeting coordination task
    ],
    'APIM': [
        # Example exclusions for APIM project
        # 'APIM-123',   # Time tracking test issue
        # 'APIM-456',   # Demo preparation task
    ],
    # Add more projects as needed
    # 'YOUR_PROJECT_KEY': [
    #     # 'YOUR_PROJECT-123',
    # ],
}

# Notes:
# - Issues listed here will be excluded from worklog analysis
# - Useful for excluding administrative tasks that don't represent actual development work
# - You can still add temporary exclusions during tool execution
# - Use uppercase for project keys and issue IDs
# - Remove the # to uncomment and activate exclusions