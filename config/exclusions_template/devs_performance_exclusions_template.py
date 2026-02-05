"""
Template for Developer Performance Tool exclusions configuration
Copy this file to ../exclusions/devs_performance_exclusions.py and customize
"""

# Exclusions for Developer Performance Tool
# Format supports both developers and issues exclusions
EXCLUSIONS = {
    'TMM': {
        'developers': [
            # Example developer exclusions for TMM project
            # 'john.doe@company.com',      # On extended leave
            # 'inactive.user@company.com', # No longer with team
        ],
        'issues': [
            # Example issue exclusions that might skew developer metrics
            # 'TMM-1222',  # Bulk data migration task
            # 'TMM-999',   # Infrastructure setup
        ]
    },
    'APIM': {
        'developers': [
            # Example developer exclusions for APIM project
            # 'temp.contractor@company.com',  # Temporary contractor
        ],
        'issues': [
            # Example issue exclusions for APIM project
            # 'APIM-123',  # Automated task
        ]
    },
    # Add more projects as needed
    # 'YOUR_PROJECT_KEY': {
    #     'developers': [
    #         # 'developer.email@company.com',
    #     ],
    #     'issues': [
    #         # 'YOUR_PROJECT-123',
    #     ]
    # },
}

# Notes:
# - Developers should be specified by their email addresses as they appear in Jira
# - Issues listed here will be excluded when calculating developer performance metrics
# - Use uppercase for project keys and issue IDs
# - Remove the # to uncomment and activate exclusions