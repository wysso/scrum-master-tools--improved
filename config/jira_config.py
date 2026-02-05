"""
Jira configuration for ScrumMaster Tool
"""
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Jira connection configuration
JIRA_CONFIG = {
    'base_url': os.getenv('JIRA_BASE_URL', 'https://your-domain.atlassian.net'),
    'personal_token': os.getenv('JIRA_PERSONAL_TOKEN', ''),
    'email': os.getenv('JIRA_EMAIL', ''),
}

# Application settings
SETTINGS = {
    'timeout': int(os.getenv('JIRA_TIMEOUT', 30)),
    'verify_ssl': os.getenv('JIRA_VERIFY_SSL', 'true').lower() == 'true',
    'max_results_per_page': int(os.getenv('MAX_RESULTS_PER_PAGE', 100)),
}

# Custom fields
CUSTOM_FIELDS = {
    'responsible': os.getenv('JIRA_RESPONSIBLE_FIELD', 'customfield_11000'),
}

# Output paths
OUTPUT_PATHS = {
    'base': os.getenv('OUTPUT_DIR', 'output'),
    'reports': os.getenv('REPORTS_DIR', 'output/reports'),
    'logs': os.getenv('LOGS_DIR', 'output/logs'),
    'exports': os.getenv('EXPORTS_DIR', 'output/exports'),
}

# Logging configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
}

# Configuration validation
def validate_config():
    """Check if configuration is complete"""
    errors = []
    
    if not JIRA_CONFIG['base_url'] or JIRA_CONFIG['base_url'] == 'https://your-domain.atlassian.net':
        errors.append("JIRA_BASE_URL is not configured")
    
    if not JIRA_CONFIG['personal_token']:
        errors.append("JIRA_PERSONAL_TOKEN is not configured")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {error}" for error in errors))
    
    return True