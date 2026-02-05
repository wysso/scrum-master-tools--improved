# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.11.1]

### Fixed
- Minor bug fixes

## [2.11.0]

### Added
- Email notification suppression for bulk operations in Jira API calls
- `notify_users` parameter to all issue update methods (default: False)
- .env.example template file for easier configuration setup

### Changed
- All bulk update operations now suppress email notifications by default
- Enhanced jira_client.py with notifyUsers=false parameter support
- Improved user experience by preventing spam notifications during bulk operations

### Fixed
- Bulk operations in components_updater.py and label_updater.py no longer send hundreds of notification emails
- .gitignore updated to include .env.example file for users
- Notification flood issue resolved for watchers during mass updates

## [2.10.0]

### Added
- Clean production repository structure with development files properly excluded
- Enhanced .gitignore configuration for better development/production separation

### Changed
- Development files (.serena/, .claude/, CLAUDE.md, planning docs) now excluded from production repositories
- Streamlined GitLab repositories contain only end-user files
- Improved repository management workflow for triple-repository strategy

### Fixed
- Development files no longer pushed to GitLab production repositories
- Repository synchronization and cleanliness across all three repositories
- Enhanced separation between development and production codebases

## [2.9.0]

### Added
- Code cleanup and repository history reset for better version management
- Streamlined development workflow with clean repository state

### Changed
- Repository history cleaned up to remove redundant version commits
- Enhanced version management process for cleaner release cycles

### Fixed
- Repository synchronization issues between local and GitLab repositories
- Version history organization and consistency across repositories

## [2.8.0]

### Added
- **Triple Repository Strategy**: Integration with new GitLab PM/PMO Tools repository for expanded distribution
- GitLab PM/PMO repository configuration (https://gitlab.divante.pl/pm-pmo-tools/scrum-master-tools.git)
- Enhanced git workflow documentation for managing three repositories (GitHub dev + 2 GitLab production)

### Changed
- **Repository Management**: Updated from dual to triple repository strategy with comprehensive push verification
- **Documentation**: Enhanced CLAUDE.md with detailed triple repository workflow and safety checks
- **Git Configuration**: Added gitlab-pmo remote configuration with proper SSH port setup (60022)
- **Version Management**: Updated tagging process to support distribution to three repositories
- **Development Tools**: Refined exclusions management templates and core functionality

### Fixed
- Git remote configuration for consistent SSH port usage across all GitLab repositories
- Documentation accuracy for repository management and version tagging processes
- Enhanced verification procedures to prevent development files from reaching production repositories

## [2.7.0]

### Added
- **Comprehensive Documentation Suite**: Complete docs/ folder with 7 major documentation files
  - USER_GUIDE.md: Complete user guide for Scrum Masters with practical examples
  - CONFIGURATION.md: Detailed setup and configuration instructions
  - ARCHITECTURE.md: Technical architecture and system design documentation
  - TOOLS.md: Comprehensive documentation for all analysis and helper tools
  - API.md: Jira API integration guide with code examples
  - TROUBLESHOOTING.md: Extended troubleshooting guide with solutions and FAQ
  - CONTRIBUTING.md: Development guidelines and contribution process
- Environment-based configuration system (.env file approach) for enhanced security and portability
- .env.example template file with comprehensive configuration options and setup instructions
- Enhanced cross-platform launcher compatibility with improved PowerShell support

### Changed
- **Configuration System Enhancement**: New .env-based configuration approach with config/jira_config.py loader
- **CLI User Experience**: Improved tool descriptions, reorganized menu structure with bulk operations section
- **Cross-platform Launchers**: Enhanced PowerShell support with better error handling and Unicode compatibility
- **Connection Test Tool**: Enhanced error handling, better user feedback, and improved connection validation
- **Base Tool Architecture**: Enhanced documentation and code structure with comprehensive docstrings
- **Project Structure**: Updated .gitignore for better development/production repository separation

### Fixed
- Enhanced stability and error reporting in connection testing
- Improved cross-platform launcher compatibility and user experience
- Better organization of CLI menu with logical tool grouping
- Enhanced code documentation and maintainability

## [2.6.0]

### Added
- **Comprehensive Documentation Suite**: Complete docs/ folder with 6 major documentation files
  - USER_GUIDE.md: Complete user guide for Scrum Masters with practical examples
  - CONFIGURATION.md: Detailed setup and configuration instructions
  - ARCHITECTURE.md: Technical architecture and system design documentation
  - TOOLS.md: Comprehensive documentation for all analysis and helper tools
  - API.md: Jira API integration guide with code examples
  - TROUBLESHOOTING.md: Extended troubleshooting guide with solutions and FAQ
  - CONTRIBUTING.md: Development guidelines and contribution process
- Environment-based configuration system (.env file approach) for enhanced security and portability
- .env.example template file with comprehensive configuration options and setup instructions
- JQL-based component updates in Components Updater tool for more flexible component management
- Enhanced cross-platform launcher compatibility with improved PowerShell support

### Changed
- **Configuration System Overhaul**: Hybrid system using .env files loaded through config/jira_config.py
- **README.md Enhancement**: Updated to v2.6.0 with comprehensive documentation links and new features
- **CLI User Experience**: Improved tool descriptions, better UI text consistency, and enhanced user feedback
- **Components Updater**: Enhanced description from "Backend/Frontend labels" to "JQL-based" updates
- **Launcher Files**: Updated all platform-specific launchers with improved error handling and user experience
- **Connection Test Tool**: Enhanced error handling, better user feedback, and improved connection validation
- **Project Structure**: Updated to reflect new docs/ folder and .env configuration approach

### Fixed
- Configuration file gitignore handling to better support new .env approach
- User experience improvements across all helper tools
- Enhanced stability and error reporting in connection testing
- Documentation cross-references and navigation between all guides

## [2.5.0]

### Added
- Exclusions Management System with interactive UI for managing project-specific exclusions
- Components Updater helper tool for bulk updating Jira issue components based on labels
- ExclusionsManager class for centralized exclusions handling across all tools
- Enhanced issue type summary with detailed reporting and verification totals
- Developer filtering capability in worklog summary tool
- Support for component management in JiraClient (get_project_components, update_issue_components)
- Interactive exclusions configuration templates

### Changed
- All analysis tools now integrate with new exclusions management system
- Issue type summary tool provides more detailed CSV reports with individual issue tracking
- Worklog summary tool supports single developer analysis mode
- Base tool framework enhanced with exclusions support and better error handling
- Improved estimation accuracy calculations in issue type summary

### Fixed
- Enhanced error handling in component validation
- Better user experience with exclusions management
- Improved reporting accuracy and verification capabilities

## [2.4.0]

### Added
- Unified category detection method `_get_category_from_labels_and_components()` in base_tool

### Changed
- All tools now use components as primary source for categorization (components → labels → 'Others')
- Modified anomaly detector to check both components and labels for missing technology indicators
- Modified planning tool to check both components and labels for missing technology indicators
- Changed anomaly type from "Missing Tech Labels" to "Missing technology labels or components"
- Updated category detection to be case-sensitive (e.g., only "Backend" not "backend")

### Fixed
- Inconsistent category detection across different tools
- Planning tool now properly checks components in addition to labels

## [2.3.1]

### Changed
- Updated tool descriptions for better clarity
- Minor improvements in user interface text

### Fixed
- Improved consistency in tool descriptions across the CLI interface

## [2.3.0]

### Added
- Unified category detection method `_get_category_from_labels_and_components()` in base_tool
- Support for Jira components as primary source for task categorization
- Case-sensitive category matching for consistency

### Changed
- All tools now use components as primary source for categorization (components → labels → 'Others')
- Modified anomaly detector to check both components and labels for missing technology indicators
- Modified planning tool to check both components and labels for missing technology indicators
- Changed anomaly type from "Missing Tech Labels" to "Missing technology labels or components"
- Updated category detection to be case-sensitive (e.g., only "Backend" not "backend")

### Fixed
- Inconsistent category detection across different tools
- Planning tool now properly checks components in addition to labels

## [2.2.0]

### Added
- Board selection for multi-board projects
- Support for retrieving all sprints (not just first 50)
- Multi-sprint analysis mode for single developer across multiple sprints
- Worked Hours column showing actual hours logged by developer
- Focus Rate metric (Completed/Worked ratio)
- `_get_developer_worklogs_in_period()` method to fetch all developer worklogs

### Changed
- Updated CSV export and console output with new metrics
- Renamed Performance column to Completed %

### Removed
- Performance Trend section from summary

## [2.1.0]

### Added
- Multi-board support for projects with multiple boards
- Automatic board selection for single-board projects
- `get_project_boards()` method to JiraClient
- Optional board_id parameter to `get_project_sprints()`
- Sprint status indicators (active/closed/future)

### Changed
- Updated `get_sprint_selection()` in base_tool to handle board selection
- Board selection is automatic when project has only one board

## [2.0.0]

### Added
- Initial release of ScrumMaster Tools 2.0
- Sprint Completion analysis tool
- Worklog Summary tool
- Anomaly Detector tool
- Planning Tool
- Base tool framework with Jira integration
- CSV and JSON export capabilities
- Interactive CLI interface