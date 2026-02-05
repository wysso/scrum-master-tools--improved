# 🚀 ScrumMaster Tools (SMT) v2.11.1

Advanced Jira data analysis tools for Scrum Masters and development teams with comprehensive sprint analytics, worklog management, and exclusions handling.

💡 **Quick start:**
- **Windows:** Double-click `ScrumMaster Tools.bat` or `ScrumMaster Tools (PowerShell).bat`
- **macOS:** Double-click `ScrumMaster Tools.command`
- **Linux/Command Line:** `python smt.py`

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Tools](#-tools)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)

## 🎯 Features

### 📊 Available tools:

**Main Analysis Tools:**
- **Sprint Completion** - Comprehensive analysis of tasks completed during sprint with exclusions support
- **Worklog Summary** - Detailed work logs analysis with developer filtering and focus rate metrics
- **Anomaly Detector** - Detection of sprint data anomalies and unusual patterns
- **Planning Tool** - Sprint planning quality analysis with multi-sprint support
- **Issue Type Summary** - Comprehensive issue type analysis with estimation accuracy
- **Developer Performance** - Team performance metrics and individual developer analysis

**Helper Tools:**
- **Connection Test** - Validate Jira API connectivity and authentication
- **Projects Lister** - Browse and list available Jira projects
- **Label Updater** - Bulk update labels in Jira issues based on patterns
- **Components Updater** - JQL-based bulk update of Jira issue components
- **Responsible Field Updater** - Update responsible/assignee fields in bulk
- **Custom Fields Identifier** - Discover custom field IDs for configuration
- **Check Components** - Validate project components and structure

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher (supports 3.8, 3.9, 3.10, 3.11)
- Access to Jira instance with API permissions
- Jira Personal Access Token (PAT) with appropriate project access

### Setup

1. **Clone the repository:**
   ```bash
   git clone link
   or
   git clone ssh: link
   or
   git clone link
   cd scrummastertool
   ```
   
2. **Install Python**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   echo 'alias python=python3' >> ~/.bashrc && source ~/.bashrc
   ```

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4**Install dependencies:**
   ```bash
   pip install -r requirements.txt

   # Or install as editable package for development:
   pip install -e .
   ```

5.**Configure Jira connection:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file and configure your Jira settings:
   - `JIRA_BASE_URL`: Your Jira instance URL (eg. https://jira./)
   - `JIRA_PERSONAL_TOKEN`: Your Jira Personal Access Token
   - `JIRA_RESPONSIBLE_FIELD`: Update with your instance's custom field ID for responsible person (eg. customfield_11000)
   - Other settings can be left as defaults or customized as needed

## 🚀 Usage

### Quick launch options:

#### 🪟 Windows - Batch files:
**Option 1: Standard Command Prompt**
Double-click `ScrumMaster Tools.bat`

**Option 2: PowerShell (Recommended for Windows 10/11)**
Double-click `ScrumMaster Tools (PowerShell).bat`

Both options will automatically:
- Activate the virtual environment
- Launch the application
- Keep the command window open

**Tips:**
- Create a shortcut on your Desktop for easy access
- Pin the shortcut to Start Menu or Taskbar
- If you see security warning, click "More info" → "Run anyway"
- Use PowerShell version for better Unicode support

#### 🍎 macOS - Command file:
1. **First time setup** (only once):
   ```bash
   chmod +x "ScrumMaster Tools.command"
   ```

2. **Running the tool:**
   - Double-click `ScrumMaster Tools.command` file
   - The tool will automatically activate environment and launch

**Tips:**
- Drag the .command file to your Dock for quick access
- If macOS blocks the file, right-click → Open → Open anyway

#### 🐧 Linux / Manual method (all platforms):
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the tool
python smt.py
```

### Using the Application

1. **Select a tool** from the interactive menu
2. **Choose project** from your available Jira projects
3. **Configure exclusions** (new in v2.5.0) - define which issues to exclude from analysis
4. **Select sprint(s)** for analysis
5. **Review results** in the generated reports

### Key Features in v2.6.0

- **Environment-based Configuration**: Secure .env file configuration system for enhanced portability
- **JQL-based Components Updater**: Advanced component management with flexible JQL queries
- **Enhanced Cross-platform Support**: Improved PowerShell launcher with better error handling
- **Enhanced Connection Testing**: Better validation and user feedback for API connectivity
- **Comprehensive Documentation**: Complete docs/ folder with user guides, API docs, and troubleshooting

## 📁 Project Structure

```
ScrumMaster Tool/
├── smt.py                           # Main entry point
├── ScrumMaster Tools.bat            # Windows launcher (Command Prompt)
├── ScrumMaster Tools (PowerShell).bat  # Windows launcher (PowerShell)
├── ScrumMaster Tools.command        # macOS launcher
├── requirements.txt                 # Python dependencies
├── setup.py                        # Package configuration
├── CHANGELOG.md                    # Version history
├── .env.example                    # Environment configuration template
├── config/                         # Configuration files
│   ├── __init__.py
│   ├── jira_config.py             # Configuration loader (uses .env)
│   └── exclusions/                # Tool-specific exclusions config
├── docs/                           # Comprehensive documentation (NEW in v2.6.0)
│   ├── USER_GUIDE.md              # Complete user guide
│   ├── ARCHITECTURE.md            # Technical architecture
│   ├── TOOLS.md                   # Detailed tools documentation
│   ├── API.md                     # Jira API integration guide
│   ├── TROUBLESHOOTING.md         # Extended troubleshooting
│   └── CONTRIBUTING.md            # Development guidelines
├── src/scrummaster/               # Source code
│   ├── __init__.py
│   ├── cli.py                     # CLI interface
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── base_tool.py           # Abstract base class
│   │   ├── jira_client.py         # Jira API client
│   │   └── exclusions_manager.py  # Exclusions management (v2.5.0)
│   ├── tools/                     # Analysis tools
│   │   ├── __init__.py
│   │   ├── sprint_completion.py
│   │   ├── worklog_summary.py
│   │   ├── anomaly_detector.py
│   │   ├── planning.py
│   │   ├── issue_type_summary.py
│   │   └── devs_performance.py
│   └── helpers/                   # Helper tools
│       ├── __init__.py
│       ├── connection_test.py
│       ├── projects_lister.py
│       ├── label_updater.py
│       ├── components_updater.py    # NEW in v2.5.0
│       ├── responsible_field_updater.py
│       ├── test_responsible_field.py
│       ├── check_components.py
│       └── custom_fields_identifier.py
└── output/                        # Generated reports
    ├── reports/                   # Analysis reports
    ├── logs/                      # Application logs
    └── exports/                   # Data exports
```

## 📚 Documentation

ScrumMaster Tools includes comprehensive documentation to help you get the most out of the analysis tools:

### 📖 User Documentation
- **[User Guide](docs/USER_GUIDE.md)** - Complete guide for Scrum Masters with examples and best practices
- **[Configuration Guide](docs/CONFIGURATION.md)** - Detailed setup and configuration instructions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solutions for common problems and FAQs

### 🔧 Technical Documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and technical architecture
- **[Tools Reference](docs/TOOLS.md)** - Detailed documentation for each analysis tool
- **[API Integration](docs/API.md)** - Jira API integration details and extension points

### 👨‍💻 Developer Documentation
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute and develop new tools

## 🔧 Configuration

### Getting Jira Personal Access Token:
1. Log in to your Jira instance
2. Go to Account Settings → Security → Personal Access Tokens
   - Or visit: https://id.atlassian.com/manage-profile/security/api-tokens
3. Create new token with appropriate permissions
4. Copy token to `.env` file as `JIRA_PERSONAL_TOKEN`

### Finding Custom Field IDs:
Use the built-in "Custom Fields Identifier" tool to discover your Jira instance's custom field IDs, then update them in the `.env` file.

### Exclusions Management (New in v2.5.0):
Configure project-specific exclusions to filter out:
- Specific issue types (e.g., Epic, Sub-task)
- Individual issues by key
- Issues with specific components or labels
- Issues matching custom criteria

### Supported Dependencies:
- `requests>=2.28.0` - HTTP client for Jira API
- `pandas>=1.5.0` - Data analysis and manipulation
- `jira>=3.4.0` - Official Jira Python client
- `matplotlib>=3.5.0` - Data visualization
- `seaborn>=0.12.0` - Statistical data visualization
- `python-dotenv>=0.19.0` - Environment variable management

## 🔍 Troubleshooting

### Common Issues:

**Connection Problems:**
- Use "Connection Test" tool to verify API access
- Check your Personal Access Token permissions
- Verify Jira base URL format (should include protocol)

**Custom Fields Not Found:**
- Run "Custom Fields Identifier" to discover correct field IDs
- Update `.env` file with your instance-specific field IDs

**Missing Data in Reports:**
- Check exclusions configuration - you might be excluding too much data
- Verify sprint dates and issue status transitions
- Ensure proper permissions for project access

**Performance Issues:**
- Consider using exclusions to reduce data volume for large projects
- Run analysis on smaller date ranges first
- Check network connectivity to Jira instance

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

Marek Mróz <marek@mroz.consulting>

## 🚀 Latest Updates (v2.7.0)

- **Environment-based Configuration** - Secure .env file system for enhanced security and portability
- **JQL-based Component Updates** - Advanced Components Updater with flexible JQL query support
- **Enhanced Cross-platform Launchers** - Improved PowerShell support with better error handling
- **Enhanced Connection Testing** - Better validation, error reporting, and user feedback
- **Comprehensive Documentation Suite** - Complete docs/ folder with user guides, architecture, API docs, and troubleshooting
- **CLI User Experience** - Improved tool descriptions, better UI consistency, and enhanced feedback