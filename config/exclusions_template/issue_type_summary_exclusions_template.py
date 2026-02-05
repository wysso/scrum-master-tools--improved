"""
Template for Issue Type Summary Tool exclusions configuration
Copy this file to ../exclusions/issue_type_summary_exclusions.py and customize
"""

# Exclusions for Issue Type Summary Tool
# Format: 'PROJECT_KEY': ['ISSUE-ID1', 'ISSUE-ID2', ...]
EXCLUSIONS = {
    'TMM': [
        # Example exclusions for TMM project
        # 'TMM-1222',  # Spike task that skews metrics
        # 'TMM-333',   # Infrastructure task
    ],
    'APIM': [
        # Example exclusions for APIM project
        # 'APIM-123',   # Research task
        # 'APIM-456',   # Training task
    ],
    # Add more projects as needed
    # 'YOUR_PROJECT_KEY': [
    #     # 'YOUR_PROJECT-123',
    # ],
}

# Notes:
# - Issues listed here will be automatically excluded from analysis
# - You can still add temporary exclusions during tool execution
# - Use uppercase for project keys and issue IDs
# - Remove the # to uncomment and activate exclusions