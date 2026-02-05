"""
Exclusions Manager - Manages exclusion configurations for ScrumMaster tools
Author: Marek Mróz <marek@mroz.consulting>
"""
import os
import sys
import logging
from typing import Dict, List, Set, Any, Optional
import importlib.util

logger = logging.getLogger(__name__)

class ExclusionsManager:
    """
    Manager for handling tool-specific exclusions configuration.

    Manages project-specific exclusions that filter out certain issues, types,
    components, or labels from analysis. Provides both persistent configuration
    storage and temporary session-based exclusions.

    Attributes:
        tool_name (str): Name of the tool using this exclusions manager
        config_file (str): Filename for the exclusions configuration
        config_path (str): Full path to the configuration file
        template_path (str): Path to the configuration template
        exclusions_data (dict): Loaded exclusions data from configuration
        temp_exclusions (set): Temporary exclusions for current session

    Example:
        >>> manager = ExclusionsManager("sprint_completion")
        >>> exclusions = manager.get_exclusions_for_project("PROJ")
        >>> manager.add_temp_exclusion("PROJ-123")
    """

    def __init__(self, tool_name: str):
        """
        Initialize exclusions manager for specific tool

        Args:
            tool_name: Name of the tool (e.g., 'issue_type_summary')
        """
        self.tool_name = tool_name
        self.config_file = f"{tool_name}_exclusions.py"
        self.config_path = os.path.join("config", "exclusions", self.config_file)
        self.template_path = os.path.join("config", "exclusions_template", f"{self.config_file.replace('.py', '_template.py')}")
        self.exclusions_data = {}
        self.temp_exclusions = set()  # Temporary exclusions for current session

        logger.debug(f"ExclusionsManager initialized for tool: {tool_name}")

    def _load_exclusions_from_file(self) -> Dict[str, Any]:
        """Load exclusions from configuration file"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Exclusions config file not found: {self.config_path}")
            logger.info(f"You can create it by copying from template: {self.template_path}")
            return {}

        try:
            # Load the exclusions module dynamically
            spec = importlib.util.spec_from_file_location("exclusions_config", self.config_path)
            exclusions_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(exclusions_module)

            if hasattr(exclusions_module, 'EXCLUSIONS'):
                logger.info(f"Loaded exclusions configuration from {self.config_path}")
                return exclusions_module.EXCLUSIONS
            else:
                logger.warning(f"No EXCLUSIONS found in {self.config_path}")
                return {}

        except Exception as e:
            logger.error(f"Error loading exclusions from {self.config_path}: {str(e)}")
            return {}

    def load_exclusions(self, project_key: str) -> Dict[str, Any]:
        """
        Load exclusions for specific project

        Args:
            project_key: Jira project key (e.g., 'TMM', 'APIM')

        Returns:
            Dictionary with exclusions data for the project
        """
        if not self.exclusions_data:
            self.exclusions_data = self._load_exclusions_from_file()

        project_exclusions = self.exclusions_data.get(project_key, {})

        # Normalize data structure - handle both simple lists and complex dictionaries
        if isinstance(project_exclusions, list):
            # Simple list format (e.g., for issue_type_summary)
            return {
                'issues': project_exclusions,
                'count': len(project_exclusions)
            }
        elif isinstance(project_exclusions, dict):
            # Complex dictionary format (e.g., for devs_performance)
            total_count = 0
            for key, value in project_exclusions.items():
                if isinstance(value, list):
                    total_count += len(value)
            project_exclusions['count'] = total_count
            return project_exclusions
        else:
            return {'issues': [], 'count': 0}

    def get_exclusions_for_project(self, project_key: str, exclusion_type: str = 'issues') -> Set[str]:
        """
        Get exclusions for project and type

        Args:
            project_key: Jira project key
            exclusion_type: Type of exclusions ('issues', 'developers', etc.)

        Returns:
            Set of exclusion values
        """
        project_data = self.load_exclusions(project_key)

        if exclusion_type in project_data and isinstance(project_data[exclusion_type], list):
            persistent_exclusions = set(project_data[exclusion_type])
        else:
            persistent_exclusions = set()

        # Combine with temporary exclusions (for current session only)
        return persistent_exclusions.union(self.temp_exclusions)

    def add_temp_exclusion(self, exclusion_value: str) -> None:
        """
        Add temporary exclusion for current session only

        Args:
            exclusion_value: Value to exclude (e.g., 'TMM-123')
        """
        self.temp_exclusions.add(exclusion_value.strip().upper())
        logger.info(f"Added temporary exclusion: {exclusion_value}")

    def remove_temp_exclusion(self, exclusion_value: str) -> bool:
        """
        Remove temporary exclusion

        Args:
            exclusion_value: Value to remove

        Returns:
            True if exclusion was removed, False if not found
        """
        exclusion_value = exclusion_value.strip().upper()
        if exclusion_value in self.temp_exclusions:
            self.temp_exclusions.remove(exclusion_value)
            logger.info(f"Removed temporary exclusion: {exclusion_value}")
            return True
        return False

    def get_interactive_exclusions(self, project_key: str) -> Set[str]:
        """
        Simple UI for managing exclusions - shows current exclusions and allows adding more

        Args:
            project_key: Jira project key

        Returns:
            Set of all exclusions (persistent + temporary)
        """
        # Load persistent exclusions
        project_data = self.load_exclusions(project_key)
        persistent_issues = set(project_data.get('issues', []))

        # Show current persistent exclusions
        if persistent_issues:
            print(f"✅ Configured exclusions: {', '.join(sorted(persistent_issues))} ({len(persistent_issues)} issues)")
        else:
            print("ℹ️ No exclusions configured for this project")

        # Simple prompt for additional exclusions
        print("📝 Add additional issues to exclude for this run (comma-separated, e.g. TMM-123,TMM-456):")
        exclude_input = input("   Issues to exclude (or ENTER to continue): ").strip()

        if exclude_input:
            new_exclusions = {issue_id.strip().upper() for issue_id in exclude_input.split(',') if issue_id.strip()}
            for exclusion in new_exclusions:
                self.add_temp_exclusion(exclusion)
            print(f"✅ Added {len(new_exclusions)} additional exclusions for this run")

        # Return combined exclusions
        all_exclusions = persistent_issues.union(self.temp_exclusions)
        if all_exclusions:
            print(f"❌ Will exclude {len(all_exclusions)} issues: {', '.join(sorted(all_exclusions))}")

        return all_exclusions

    def _add_temp_exclusion_interactive(self):
        """Interactive method to add temporary exclusions"""
        print("\\n📝 Enter issue IDs to exclude (comma-separated, e.g. TMM-123,TMM-456):")
        exclude_input = input("   Issues to exclude: ").strip()

        if exclude_input:
            new_exclusions = {issue_id.strip().upper() for issue_id in exclude_input.split(',') if issue_id.strip()}
            for exclusion in new_exclusions:
                self.add_temp_exclusion(exclusion)
            print(f"✅ Added {len(new_exclusions)} temporary exclusions")
        else:
            print("ℹ️ No exclusions added")

    def _remove_temp_exclusion_interactive(self):
        """Interactive method to remove temporary exclusions"""
        if not self.temp_exclusions:
            print("\\nℹ️ No temporary exclusions to remove")
            return

        print(f"\\n📝 Current temporary exclusions: {', '.join(sorted(self.temp_exclusions))}")
        remove_input = input("Enter issue IDs to remove (comma-separated): ").strip()

        if remove_input:
            to_remove = {issue_id.strip().upper() for issue_id in remove_input.split(',') if issue_id.strip()}
            removed_count = 0
            for exclusion in to_remove:
                if self.remove_temp_exclusion(exclusion):
                    removed_count += 1
            print(f"✅ Removed {removed_count} temporary exclusions")
        else:
            print("ℹ️ No exclusions removed")

    def _show_all_exclusions(self, project_key: str):
        """Show all exclusions for the project"""
        print(f"\\n📊 All exclusions for project {project_key}:")

        project_data = self.load_exclusions(project_key)
        persistent_issues = set(project_data.get('issues', []))

        if persistent_issues:
            print(f"\\n📁 Persistent exclusions ({len(persistent_issues)}):")
            for issue in sorted(persistent_issues):
                print(f"   - {issue}")

        if self.temp_exclusions:
            print(f"\\n⏱️ Temporary exclusions ({len(self.temp_exclusions)}):")
            for issue in sorted(self.temp_exclusions):
                print(f"   - {issue}")

        if not persistent_issues and not self.temp_exclusions:
            print("   No exclusions configured")

        total = len(persistent_issues) + len(self.temp_exclusions)
        print(f"\\n📈 Total exclusions: {total}")

    def get_all_exclusions(self, project_key: str) -> Set[str]:
        """
        Get all exclusions (persistent + temporary) for a project

        Args:
            project_key: Jira project key

        Returns:
            Set of all exclusions
        """
        return self.get_exclusions_for_project(project_key, 'issues')