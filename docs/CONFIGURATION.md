# ScrumMaster Tools - Configuration Guide

This guide covers the complete setup and configuration process for ScrumMaster Tools (SMT), including environment setup, Jira integration, and custom field mapping.

## Table of Contents

- [Quick Setup](#quick-setup)
- [Configuration System Overview](#configuration-system-overview)
- [Environment Variables Reference](#environment-variables-reference)
- [Jira Integration Setup](#jira-integration-setup)
- [Custom Fields Configuration](#custom-fields-configuration)
- [Security Best Practices](#security-best-practices)
- [Different Jira Instances](#different-jira-instances)
- [Troubleshooting Configuration](#troubleshooting-configuration)

---

## Quick Setup

### Step 1: Copy Configuration Template
```bash
cp .env.example .env
```

### Step 2: Edit Configuration
Open `.env` file in your favorite editor and configure the required settings:

```bash
# Minimum required configuration
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_PERSONAL_TOKEN=your_personal_access_token_here
```

### Step 3: Test Connection
```bash
python smt.py
# Choose: Connection Test (option 7)
```

If the connection test passes, you're ready to use SMT!

---

## Configuration System Overview

SMT uses a hybrid configuration system that combines:
1. **Environment Variables** (`.env` file) - for sensitive and instance-specific data
2. **Python Configuration** (`config/jira_config.py`) - for loading and validating settings
3. **Default Values** - sensible defaults for most settings

### Architecture
```
.env file → python-dotenv → config/jira_config.py → SMT Tools
```

This approach provides:
- ✅ **Security**: Sensitive data in gitignored .env file
- ✅ **Portability**: Easy deployment across environments
- ✅ **Validation**: Python-based configuration validation
- ✅ **Flexibility**: Override any setting via environment variables

---

## Environment Variables Reference

### Core Jira Settings

#### JIRA_BASE_URL (Required)
**Description**: Base URL of your Jira instance
**Format**: Complete URL including protocol
**Examples**:
```bash
# Atlassian Cloud
JIRA_BASE_URL=https://yourcompany.atlassian.net

# Self-hosted Jira Server
JIRA_BASE_URL=https://jira.yourcompany.com

# Custom domain
JIRA_BASE_URL=https://issues.yourcompany.com
```

**Common Mistakes**:
```bash
❌ JIRA_BASE_URL=yourcompany.atlassian.net      # Missing protocol
❌ JIRA_BASE_URL=https://yourcompany.atlassian.net/  # Trailing slash
✅ JIRA_BASE_URL=https://yourcompany.atlassian.net   # Correct
```

#### JIRA_PERSONAL_TOKEN (Required)
**Description**: Personal Access Token for Jira API authentication
**Format**: Token string without quotes or prefixes
**Example**:
```bash
JIRA_PERSONAL_TOKEN=ATATT3xFfGF0T...your_actual_token_here...yxWKJQ
```

**How to obtain**:
1. Log into your Jira instance
2. Go to Profile → Security → Personal Access Tokens
3. Create new token with appropriate permissions
4. Copy the token (you won't see it again!)

### Connection Settings

#### JIRA_TIMEOUT
**Description**: Request timeout in seconds
**Default**: 30
**Range**: 10-300
```bash
JIRA_TIMEOUT=60  # For slow networks or large instances
```

#### JIRA_VERIFY_SSL
**Description**: Whether to verify SSL certificates
**Default**: true
**Values**: true, false
```bash
JIRA_VERIFY_SSL=false  # Only for development with self-signed certs
```

⚠️ **Security Warning**: Only set to `false` for development. Never disable SSL verification in production.

### Custom Fields Configuration

#### JIRA_RESPONSIBLE_FIELD
**Description**: Custom field ID for responsible person
**Default**: customfield_11000
**Format**: customfield_XXXXX
```bash
JIRA_RESPONSIBLE_FIELD=customfield_11000
```

#### Additional Custom Fields
```bash
# Story Points (common IDs: customfield_10016, customfield_10002)
JIRA_STORY_POINTS_FIELD=customfield_10016

# Epic Link (common ID: customfield_10014)
JIRA_EPIC_LINK_FIELD=customfield_10014

# Sprint field (common ID: customfield_10020)
JIRA_SPRINT_FIELD=customfield_10020
```

### Application Settings

#### Output Directories
```bash
OUTPUT_DIR=output
REPORTS_DIR=output/reports
LOGS_DIR=output/logs
EXPORTS_DIR=output/exports
```

#### API Settings
```bash
MAX_RESULTS_PER_PAGE=100  # API pagination size (50-1000)
```

#### Logging Configuration
```bash
LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

---

## Jira Integration Setup

### Personal Access Token Setup

#### For Atlassian Cloud
1. **Navigate to Token Management**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Or: Jira → Profile → Personal Access Tokens

2. **Create New Token**:
   - Click "Create API token"
   - Give it a descriptive name: "ScrumMaster Tools - [Your Name]"
   - Click "Create"

3. **Copy Token Immediately**:
   - Copy the token (you won't see it again)
   - Paste into your `.env` file as `JIRA_PERSONAL_TOKEN`

#### For Jira Server/Data Center
1. **Check with Admin**: Verify Personal Access Tokens are enabled
2. **Navigate to Token Management**: Usually Profile → Security → Personal Access Tokens
3. **Create Token**: Similar process to Cloud
4. **Configure Permissions**: Ensure token has necessary project access

### Required Permissions

Your Jira user (and Personal Access Token) needs:
- ✅ **Browse Projects** - Access to projects you want to analyze
- ✅ **View Issues** - Read issue details and metadata
- ✅ **View Development Tools** - Access to worklogs and time tracking
- ✅ **Browse Users** - See user information for assignees

### Testing Your Connection

Use the built-in Connection Test:
```bash
python smt.py
# Choose option 7: Connection Test

# Expected success output:
✅ Testing connection to Jira...
✅ Connected successfully!
✅ User: Your Name (you@company.com)
✅ Permissions: Verified
✅ Custom fields: Configured correctly
```

---

## Custom Fields Configuration

### Why Custom Fields Matter

Jira custom fields have internal IDs like `customfield_10016` that vary between instances. SMT needs these IDs to access:
- Responsible Person
- Epic Links
- Sprint assignments
- Any other custom fields you use

### Finding Custom Field IDs

#### Method 1: Use SMT's Built-in Tool
```bash
python smt.py
# Choose: Custom Fields Identifier

# This will show all custom fields with their IDs and names
```

#### Method 2: Manual Discovery
1. **Open any Jira issue in your browser**
2. **View page source** (Ctrl+U or Cmd+U)
3. **Search for "customfield_"** to find field IDs
4. **Match field names** to IDs in the HTML

#### Method 3: Jira API
```bash
# Use curl to query Jira API directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-jira-instance.com/rest/api/2/field
```

### Common Custom Field Mappings

#### Story Points
**Common IDs**: `customfield_10016`, `customfield_10002`
```bash
JIRA_STORY_POINTS_FIELD=customfield_10016
```

#### Epic Link
**Common IDs**: `customfield_10014`, `customfield_10011`
```bash
JIRA_EPIC_LINK_FIELD=customfield_10014
```

#### Sprint Field
**Common IDs**: `customfield_10020`, `customfield_10021`
```bash
JIRA_SPRINT_FIELD=customfield_10020
```

### Validation

After configuring custom fields, verify they work:
1. Run **Connection Test** - checks basic field access
2. Run any analysis tool with a small dataset
3. Check that fields appear correctly in CSV exports

---

## Security Best Practices

### Environment File Security

#### File Permissions
```bash
# Secure your .env file
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw------- (600)
```

#### Git Security
The `.env` file should **never** be committed to version control:
```bash
# Check .gitignore includes:
.env
config/jira_config_local.py
*.env
```

#### Token Management
- ✅ Use descriptive token names: "SMT-Production-John-Doe"
- ✅ Rotate tokens regularly (quarterly recommended)
- ✅ Revoke unused tokens immediately
- ✅ Use separate tokens for different environments

### Network Security

#### HTTPS Only
```bash
# Always use HTTPS for Jira connections
JIRA_BASE_URL=https://your-jira-instance.com  # ✅ Secure
JIRA_BASE_URL=http://your-jira-instance.com   # ❌ Insecure
```

#### SSL Verification
```bash
# Keep SSL verification enabled in production
JIRA_VERIFY_SSL=true   # ✅ Secure
JIRA_VERIFY_SSL=false  # ❌ Only for development
```

### Access Control

#### Principle of Least Privilege
Configure tokens with minimal necessary permissions:
- Only projects you need to analyze
- Read-only access where possible
- No admin permissions unless required

#### Environment Separation
Use different tokens for different environments:
```bash
# Development
JIRA_PERSONAL_TOKEN=dev_token_here

# Production
JIRA_PERSONAL_TOKEN=prod_token_here
```

---

## Different Jira Instances

### Atlassian Cloud
**URL Format**: `https://yourcompany.atlassian.net`
**Authentication**: Personal Access Token
**Configuration**:
```bash
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_PERSONAL_TOKEN=ATATT3xFfGF0...
JIRA_VERIFY_SSL=true
```

### Jira Server (Self-hosted)
**URL Format**: `https://jira.yourcompany.com`
**Authentication**: Personal Access Token (if enabled)
**Configuration**:
```bash
JIRA_BASE_URL=https://jira.yourcompany.com
JIRA_PERSONAL_TOKEN=your_server_token
JIRA_VERIFY_SSL=true  # or false for self-signed certs
```

### Jira Data Center
**URL Format**: Custom domain
**Authentication**: Personal Access Token
**Configuration**:
```bash
JIRA_BASE_URL=https://issues.yourcompany.com
JIRA_PERSONAL_TOKEN=your_datacenter_token
JIRA_VERIFY_SSL=true
```

### Special Configurations

#### Behind Corporate Proxy
```bash
# You may need to configure proxy settings in your environment
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
```

#### Self-Signed Certificates
```bash
JIRA_VERIFY_SSL=false
```
⚠️ **Warning**: Use only for development or internal testing

#### Custom Ports
```bash
JIRA_BASE_URL=https://jira.company.com:8443
```

---

## Troubleshooting Configuration

### Connection Issues

#### "Authentication failed"
```bash
❌ HTTP 401: Unauthorized

Troubleshooting:
1. Verify token is correct (no extra spaces/characters)
2. Check token hasn't expired
3. Ensure token has necessary permissions
4. Try regenerating token
```

#### "Connection timeout"
```bash
❌ Request timeout after 30 seconds

Solutions:
1. Increase timeout: JIRA_TIMEOUT=60
2. Check network connectivity
3. Verify Jira instance URL
4. Check if behind firewall/proxy
```

#### "SSL Certificate verification failed"
```bash
❌ SSL: CERTIFICATE_VERIFY_FAILED

Solutions:
1. Check URL uses https://
2. For development only: JIRA_VERIFY_SSL=false
3. Update certificates on your system
4. Contact IT for certificate issues
```

### Custom Field Issues

#### "Custom field not found"
```bash
❌ Custom field 'customfield_10016' not found

Solutions:
1. Run "Custom Fields Identifier" tool
2. Verify field ID in .env file
3. Check if field exists in your Jira instance
4. Ensure you have permission to access the field
```

#### "Story points not showing in reports"
```bash
Symptoms: CSV exports missing story point data

Solutions:
1. Verify JIRA_STORY_POINTS_FIELD is configured
2. Check if issues actually have story points assigned
3. Confirm field ID is correct for your instance
4. Test with a known issue that has story points
```

### Permission Issues

#### "Project not found"
```bash
❌ Project 'PROJ' not found

Solutions:
1. Verify project key is correct (case sensitive)
2. Check if you have Browse Projects permission
3. Ensure token has access to the specific project
4. Try with a different project you know you can access
```

#### "No boards found"
```bash
❌ No boards found for project PROJ

Solutions:
1. Verify project has Agile boards configured
2. Check if you have permission to view boards
3. Contact Jira admin for board access
4. Try using different project
```

### Configuration Validation

#### Validate Your Configuration
```python
# You can test configuration programmatically:
from config.jira_config import validate_config

try:
    validate_config()
    print("✅ Configuration is valid")
except ValueError as e:
    print(f"❌ Configuration errors: {e}")
```

#### Common Configuration Mistakes
```bash
# ❌ Wrong format
JIRA_BASE_URL = "https://company.atlassian.net"  # Spaces around =

# ✅ Correct format
JIRA_BASE_URL=https://company.atlassian.net      # No spaces, no quotes

# ❌ Trailing slash
JIRA_BASE_URL=https://company.atlassian.net/

# ✅ No trailing slash
JIRA_BASE_URL=https://company.atlassian.net

# ❌ Missing protocol
JIRA_BASE_URL=company.atlassian.net

# ✅ Include protocol
JIRA_BASE_URL=https://company.atlassian.net
```

---

## Advanced Configuration

### Environment-Specific Configuration

You can maintain different configurations for different environments:

```bash
# .env.development
JIRA_BASE_URL=https://dev-jira.company.com
JIRA_PERSONAL_TOKEN=dev_token
LOG_LEVEL=DEBUG

# .env.production
JIRA_BASE_URL=https://jira.company.com
JIRA_PERSONAL_TOKEN=prod_token
LOG_LEVEL=INFO
```

Load specific environment:
```bash
cp .env.development .env  # For development
cp .env.production .env   # For production
```

### Docker Configuration

When running SMT in Docker:
```dockerfile
# Pass environment variables
docker run -e JIRA_BASE_URL=https://your-jira.com \
           -e JIRA_PERSONAL_TOKEN=your_token \
           smt:latest
```

### CI/CD Configuration

For automated deployments:
```bash
# Use environment variables in CI/CD
export JIRA_BASE_URL=$CI_JIRA_URL
export JIRA_PERSONAL_TOKEN=$CI_JIRA_TOKEN
```

---

## Getting Help

### Self-Service
1. **Run Connection Test** - First step for any configuration issue
2. **Check [Troubleshooting Guide](TROUBLESHOOTING.md)** - Comprehensive problem-solving guide
3. **Use Custom Fields Identifier** - For field mapping issues

### Documentation
- **[User Guide](USER_GUIDE.md)** - Complete usage instructions
- **[API Documentation](API.md)** - Technical integration details
- **[Architecture Guide](ARCHITECTURE.md)** - System design overview

### Support
For complex configuration issues:
- **GitHub Issues**: Report configuration bugs or feature requests
- **Professional Support**: marek@mroz.consulting for enterprise deployments

---

This configuration guide provides comprehensive setup instructions for ScrumMaster Tools. Following these steps will ensure secure, reliable integration with your Jira instance.