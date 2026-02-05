# ScrumMaster Tools - Troubleshooting Guide

## Table of Contents

- [Quick Solutions](#quick-solutions)
- [Connection Problems](#connection-problems)
- [Configuration Issues](#configuration-issues)
- [Data Problems](#data-problems)
- [Performance Issues](#performance-issues)
- [Installation Problems](#installation-problems)
- [Debug Instructions](#debug-instructions)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Getting Help](#getting-help)

---

## Quick Solutions

### 🚀 Most Common Issues (90% of problems)

#### 1. "Connection failed" or "Authentication error"
```bash
# Run Connection Test first
python smt.py
# Choose option 7: Connection Test

# If it fails, check your .env file:
# - JIRA_BASE_URL should include https://
# - JIRA_PERSONAL_TOKEN should be valid PAT
# - No spaces or quotes around values
```

#### 2. "No projects found" or "Permission denied"
- Your PAT doesn't have sufficient permissions
- Check with Jira admin for project access
- Try **Projects Lister** tool to see what you can access

#### 3. "Custom field not found" errors
```bash
# Use Custom Fields Identifier to find correct IDs
python smt.py
# Choose: Custom Fields Identifier
# Update your .env file with correct field IDs
```

#### 4. "No data in reports" or empty CSV files
- Check your exclusions - you might be filtering out everything
- Verify sprint dates and issue status
- Try without exclusions first

#### 5. SMT won't start / "Module not found"
```bash
# Make sure you're in the right directory
cd /path/to/ScrumMaster\ Tools

# Check virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Connection Problems

### Error: "Failed to connect to Jira"

#### Symptoms
```
❌ Error: Failed to connect to Jira
Connection timeout after 30 seconds
```

#### Possible Causes & Solutions

**1. Network/Firewall Issues**
```bash
# Test basic connectivity
ping your-jira-instance.com
curl -I https://your-jira-instance.com

# If these fail, contact your IT/network team
```

**2. Incorrect Base URL**
```bash
# Common mistakes in .env file:
❌ JIRA_BASE_URL=jira.company.com          # Missing protocol
❌ JIRA_BASE_URL=https://jira.company.com/ # Trailing slash
✅ JIRA_BASE_URL=https://jira.company.com  # Correct format
```

**3. SSL Certificate Issues**
```bash
# If you get SSL certificate errors:
# Edit config/jira_config.py temporarily:
SETTINGS = {
    'verify_ssl': False,  # Only for testing!
    # ... other settings
}
```
⚠️ **Warning**: Only disable SSL verification for testing. Never use in production.

### Error: "Authentication failed" or "401 Unauthorized"

#### Symptoms
```
❌ Authentication failed
HTTP 401: Unauthorized
Invalid or expired token
```

#### Solutions

**1. Check Personal Access Token (PAT)**
- Go to your Jira instance → Profile → Security → Personal Access Tokens
- Verify token is not expired
- Create new token if needed
- Copy token exactly (no spaces, complete string)

**2. Update .env file**
```bash
# Check .env file format:
JIRA_PERSONAL_TOKEN=your_token_here_without_quotes
# NOT:
JIRA_PERSONAL_TOKEN="your_token_here"  # ❌ Don't use quotes
JIRA_PERSONAL_TOKEN='your_token_here'  # ❌ Don't use quotes
```

**3. Test with Connection Test Tool**
```bash
python smt.py
# Choose: Connection Test (option 7)
# This will validate your authentication
```

### Error: "403 Forbidden" or "Insufficient permissions"

#### Symptoms
```
❌ HTTP 403: Forbidden
You don't have permission to access this resource
```

#### Solutions

**1. Check Project Permissions**
- Use **Projects Lister** to see which projects you can access
- Contact Jira admin to grant access to required projects
- Ensure you have "Browse Projects" permission

**2. Required Permissions for SMT**
Your Jira user needs:
- Browse Projects
- View Development Tools (for worklogs)
- View Issues (basic read access)
- Access to specific boards/sprints you want to analyze

---

## Configuration Issues

### Error: "Custom field 'customfield_xxxxx' not found"

#### Symptoms
```
❌ Custom field 'customfield_10016' not found
Field may not exist or you may not have access
```

#### Solution Process

**1. Identify Available Custom Fields**
```bash
python smt.py
# Choose: Custom Fields Identifier
# This shows all custom fields in your Jira instance
```

**2. Common Custom Fields to Configure**
```bash
# In your .env file:
JIRA_STORY_POINTS_FIELD=customfield_10016        # Story Points
JIRA_RESPONSIBLE_FIELD=customfield_11000         # Responsible Person
JIRA_EPIC_LINK_FIELD=customfield_10014           # Epic Link
JIRA_SPRINT_FIELD=customfield_10020              # Sprint Field
```

**3. Finding the Right Field IDs**
- Story Points: Usually `customfield_10016` or `customfield_10002`
- Sprint: Usually `customfield_10020` or similar
- Epic Link: Usually `customfield_10014`
- Use **Custom Fields Identifier** to find your specific IDs

### Error: ".env file not found" or configuration errors

#### Creating .env File
```bash
# Copy from template (if exists)
cp .env.example .env

# Or create manually:
cat > .env << EOF
JIRA_BASE_URL=https://your-jira-instance.com
JIRA_PERSONAL_TOKEN=your_personal_access_token_here
JIRA_STORY_POINTS_FIELD=customfield_10016
JIRA_RESPONSIBLE_FIELD=customfield_11000
JIRA_EPIC_LINK_FIELD=customfield_10014
JIRA_SPRINT_FIELD=customfield_10020
OUTPUT_BASE_PATH=output
LOG_LEVEL=INFO
VERIFY_SSL=True
EOF
```

#### Common Configuration Mistakes
```bash
# ❌ Wrong format:
JIRA_BASE_URL = "https://jira.company.com"  # Spaces and quotes

# ✅ Correct format:
JIRA_BASE_URL=https://jira.company.com       # No spaces, no quotes

# ❌ Wrong field references:
JIRA_STORY_POINTS_FIELD=Story Points         # Human name

# ✅ Correct field references:
JIRA_STORY_POINTS_FIELD=customfield_10016    # Field ID
```

---

## Data Problems

### Problem: "No data in reports" or empty CSV files

#### Symptoms
```
📊 Analysis completed successfully!
📁 Report saved: output/reports/PROJ_sprint_completion_20240118_1430.csv

# But when you open the CSV, it's empty or has only headers
```

#### Diagnosis Process

**1. Check Exclusions First**
```bash
# During tool run, when asked about exclusions:
📝 Choose option (1-5): 5  # Continue with current settings

# Or temporarily disable all exclusions:
📝 Choose option (1-5): 2  # Show current exclusions
# Then option 4 to remove all temporary exclusions
```

**2. Verify Sprint Data**
- Check if sprint actually has issues assigned to it
- Verify sprint date range includes the work period
- Ensure issues are in correct project

**3. Test with Different Sprint**
- Try a different, older sprint that you know had activity
- Use a sprint with obvious completed work

#### Common Causes & Solutions

**Over-Aggressive Exclusions**
```bash
# Check your exclusions config:
# You might be excluding:
- All issue types (Stories, Bugs, Tasks)
- All components or labels
- Specific issues that represent most of your work
```

**Wrong Sprint Selection**
```bash
# Symptoms:
- Selected FUTURE sprint (no work completed yet)
- Selected very old sprint (issues moved or archived)
- Selected sprint from different project

# Solution: Use recent CLOSED sprint
```

**Project Access Issues**
```bash
# Even if you can see the project, you might not see all issues
# Contact Jira admin to verify full project read access
```

### Problem: Incorrect or unexpected data in reports

#### Symptoms
- Completion percentages don't match your experience
- Missing developers or issues you know exist
- Wrong time calculations or story points

#### Diagnosis Steps

**1. Spot Check Individual Issues**
```bash
# Pick 3-4 issues you know well
# Manually verify in Jira:
- Current status
- Story points value
- Who completed it and when
- Time logged during sprint period
```

**2. Check Custom Field Configuration**
```bash
# Use Custom Fields Identifier to verify:
- Story Points field ID is correct
- Responsible/Assignee field is right
- Sprint field mapping is accurate
```

**3. Verify Date Ranges**
```bash
# SMT uses sprint start/end dates
# Check in Jira that sprint dates are correct
# Some issues might have been completed outside sprint dates
```

### Problem: "Sprint not found" or board access issues

#### Symptoms
```
❌ No boards found for project PROJ
❌ Cannot fetch sprints: HTTP 404
❌ Sprint 'Sprint 23' not found on board
```

#### Solutions

**1. Verify Board Access**
```bash
# In Jira web interface:
- Go to your project
- Click on "Boards" in left sidebar
- Verify you can see at least one board
- Note the board name exactly
```

**2. Check Board Configuration**
```bash
# Board might be configured for different projects
# Or you might not have access to agile boards
# Contact Jira admin to verify board permissions
```

**3. Alternative: Use JQL Queries**
```bash
# If boards don't work, SMT can use JQL
# This is more advanced - see docs/API.md for details
```

---

## Performance Issues

### Problem: SMT is very slow or hangs

#### Symptoms
- Tool takes >5 minutes to analyze single sprint
- Progress stops at "Fetching sprint data..."
- Memory usage grows continuously

#### Common Causes & Solutions

**1. Large Sprints (100+ issues)**
```bash
# Use exclusions to reduce dataset:
- Exclude issue types you don't need (Epics, Sub-tasks)
- Exclude specific components with lots of issues
- Focus on specific assignees or labels
```

**2. API Rate Limiting**
```bash
# Jira limits API calls per minute
# SMT automatically handles this, but large requests take time
# Solution: Be patient, or break analysis into smaller chunks
```

**3. Network Latency**
```bash
# If Jira instance is geographically distant:
# Each API call takes longer
# Solution: Run during off-peak hours, be patient
```

**4. Memory Issues**
```bash
# For very large datasets:
# Close other applications
# Use 64-bit Python if analyzing huge projects
# Consider breaking analysis into multiple smaller sprints
```

### Problem: Frequent timeouts or connection drops

#### Symptoms
```
❌ Request timeout after 30 seconds
❌ Connection reset by peer
❌ Intermittent connection failures
```

#### Solutions

**1. Check Network Stability**
```bash
# Test sustained connectivity:
ping -c 100 your-jira-instance.com

# If packet loss >5%, network issues likely
```

**2. Adjust Timeout Settings**
```bash
# Edit config/jira_config.py (if using old config system)
# Or add to .env file:
REQUEST_TIMEOUT=60  # Increase from default 30 seconds
```

**3. Run During Off-Peak Hours**
- Jira server may be overloaded during business hours
- Try running analysis early morning or evening
- Check with Jira admin about server load patterns

---

## Installation Problems

### Problem: "Python not found" or version issues

#### Symptoms
```bash
bash: python: command not found
# OR
Python 2.7.x detected, but SMT requires Python 3.8+
```

#### Solutions

**1. Install Python 3.8+**
```bash
# Windows: Download from python.org
# macOS: brew install python3
# Linux: sudo apt update && sudo apt install python3 python3-pip
```

**2. Use Correct Python Command**
```bash
# Try these variants:
python3 smt.py
python3.9 smt.py
py smt.py          # Windows Python Launcher
```

### Problem: Virtual environment issues

#### Symptoms
```bash
❌ ModuleNotFoundError: No module named 'requests'
❌ Virtual environment not activating
❌ pip: command not found
```

#### Solutions

**1. Recreate Virtual Environment**
```bash
# Remove old environment
rm -rf venv

# Create new environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**2. Check Python Path**
```bash
# After activating venv:
which python    # Should show venv/bin/python
which pip       # Should show venv/bin/pip

# If not, venv activation failed
```

### Problem: Dependencies won't install

#### Symptoms
```bash
❌ ERROR: Could not install packages due to an EnvironmentError
❌ Microsoft Visual C++ 14.0 is required  # Windows
❌ Failed building wheel for some-package
```

#### Solutions

**1. Update pip and setuptools**
```bash
pip install --upgrade pip setuptools wheel
```

**2. Install Build Tools (Windows)**
```bash
# Download and install Microsoft C++ Build Tools
# Or install Visual Studio Community with C++ workload
```

**3. Use Pre-compiled Packages**
```bash
# If specific packages fail to build:
pip install --only-binary=all -r requirements.txt
```

---

## Debug Instructions

### Enabling Debug Logging

**1. Temporary Debug Mode**
```bash
# Set environment variable before running:
export LOG_LEVEL=DEBUG  # Linux/Mac
set LOG_LEVEL=DEBUG     # Windows

python smt.py
```

**2. Permanent Debug Mode**
```bash
# Add to .env file:
LOG_LEVEL=DEBUG
```

**3. Check Log Files**
```bash
# Logs are written to:
ls -la output/logs/

# View recent logs:
tail -f output/logs/application.log
```

### Collecting Debug Information

When reporting issues, collect this information:

**1. System Information**
```bash
python --version
pip list | grep -E "(requests|pandas|jira)"
uname -a  # Linux/Mac
```

**2. Configuration (sanitized)**
```bash
# Share your .env file BUT remove:
# - JIRA_PERSONAL_TOKEN (replace with "REDACTED")
# - JIRA_BASE_URL (replace with "REDACTED" or genericize)

# Example sanitized config:
JIRA_BASE_URL=https://company.atlassian.net  # or REDACTED
JIRA_PERSONAL_TOKEN=REDACTED
JIRA_STORY_POINTS_FIELD=customfield_10016
...
```

**3. Error Messages**
- Complete error message and stack trace
- Steps to reproduce the issue
- Which tool and options you were using

**4. Test Results**
```bash
# Run Connection Test and share results:
python smt.py
# Choose: Connection Test
# Share output (but redact personal info)
```

### Manual API Testing

**Test Jira API manually:**
```bash
# Test basic connectivity:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-jira-instance.com/rest/api/2/myself

# Test project access:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-jira-instance.com/rest/api/2/project

# Test issue search:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://your-jira-instance.com/rest/api/2/search?jql=project=YOURPROJECT"
```

---

## Frequently Asked Questions

### General Usage

**Q: How often should I run SMT analysis?**
A:
- **Sprint retrospectives**: After each sprint closes
- **Planning improvement**: Monthly, analyzing last 4-6 sprints
- **Team development**: Quarterly for performance trends
- **Process optimization**: When you suspect issues or want to measure improvements

**Q: Can I analyze multiple projects at once?**
A: Not directly. SMT analyzes one project at a time, but you can:
- Run multiple analyses and compare results manually
- Use exclusions to focus on specific components across projects
- Export CSV data and combine in Excel/Google Sheets

**Q: How far back in history can I analyze?**
A: As far back as your Jira data goes, but consider:
- Very old data may not be relevant to current team/process
- Jira performance may degrade with very large date ranges
- 3-6 months of data is usually sufficient for trend analysis

### Data Accuracy

**Q: Why don't my completion percentages match what I remember?**
A: Common reasons:
- SMT uses actual Jira status transitions, not memory
- Issues might have been completed outside sprint boundaries
- Exclusions might be filtering out some work
- Different definition of "completion" (status vs. sprint close date)

**Q: Can I trust the time logging data if developers don't log consistently?**
A: Time logging analysis is only as good as the data quality:
- Use **Worklog Summary** as trends, not absolute values
- Focus on patterns (focus rate, distribution) rather than exact hours
- Consider team education on consistent time logging
- Use story point velocity as alternative productivity metric

**Q: Why do some developers show zero original estimate (h) but have time logged?**
A: This happens when:
- Developer worked on issues not assigned to them (pair programming)
- Work on bugs or tasks without story point estimates
- Time logged on research/spikes that don't have original estimate (h)
- Custom field mapping issues (original estimate (h) field not configured correctly)

### Performance and Scale

**Q: How big a project can SMT handle?**
A: SMT has been tested with:
- ✅ Projects with 500+ active issues per sprint
- ✅ 50+ developers across multiple teams
- ✅ 6+ months of historical data
- ❌ Very large enterprises (1000+ issues) may need performance tuning

**Q: Can I run SMT on a schedule/automation?**
A: SMT is designed for interactive use, but you can:
- Script the tool execution with input files
- Use the helper tools (Connection Test) in automated health checks
- Export data programmatically using the JiraClient class
- Contact us for enterprise automation needs

### Integration and Customization

**Q: Can I export data to other tools (Excel, Tableau, etc.)?**
A: Yes! SMT exports standard CSV files that work with:
- Microsoft Excel, Google Sheets
- Tableau, Power BI, Looker
- R, Python pandas for custom analysis
- Any tool that reads CSV format

**Q: Can SMT work with Jira Server (not Cloud)?**
A: Yes, but:
- Use the on-premises Jira URL in configuration
- API endpoints are the same for Server and Cloud
- Authentication might differ (check with your Jira admin)
- Some features might have slight differences

**Q: Can I add custom analysis tools?**
A: Yes! SMT is designed for extensibility:
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- All tools inherit from `BaseScrumMasterTool`
- Follow existing patterns for consistency
- Share useful tools with the community

---

## Getting Help

### Self-Service Options

**1. Check This Guide First**
- Use Ctrl+F/Cmd+F to search for your specific error message
- Try the Quick Solutions section
- Run the Connection Test tool

**2. Review Documentation**
- [USER_GUIDE.md](USER_GUIDE.md) - Comprehensive usage guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [TOOLS.md](TOOLS.md) - Individual tool documentation

**3. Enable Debug Logging**
- Add `LOG_LEVEL=DEBUG` to your .env file
- Check `output/logs/application.log` for detailed error information

### Community Support

**GitHub Issues**: [Repository Issues Page]
- Search existing issues first
- Provide detailed information (see Debug Instructions section)
- Include sanitized configuration and error messages

**Documentation Updates**:
If you solve an issue not covered here, please contribute:
- Submit documentation improvements
- Share your solution with the community
- Help make SMT better for everyone

### Professional Support

For enterprise deployments or custom development:
- Contact: marek@mroz.consulting
- Professional services available for:
  - Custom tool development
  - Enterprise integration
  - Training and workshops
  - Large-scale deployment support

---

Remember: Most SMT issues are configuration-related and can be solved with the Connection Test tool and proper .env file setup. When in doubt, start there!