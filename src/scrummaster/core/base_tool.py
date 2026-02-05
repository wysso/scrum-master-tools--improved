"""
Base class for all ScrumMaster tools
Author: Marek Mróz <marek@mroz.consulting>
"""
import os
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from .jira_client import JiraClient
from .exclusions_manager import ExclusionsManager
from config.jira_config import OUTPUT_PATHS

logger = logging.getLogger(__name__)

class BaseScrumMasterTool(ABC):
    """
    Abstract base class for all ScrumMaster analysis tools.

    Provides common functionality and workflow template for Jira data analysis tools.
    Implements the Template Method pattern where subclasses define specific analysis
    logic while inheriting common operations like project selection, sprint management,
    exclusions handling, and output generation.

    Attributes:
        tool_name (str): Human-readable name of the analysis tool
        jira_client (JiraClient): Client for Jira API communication
        exclusions_manager (ExclusionsManager): Manages project-specific data exclusions

    Example:
        >>> class MyAnalysisTool(BaseScrumMasterTool):
        ...     def __init__(self):
        ...         super().__init__("My Analysis")
        ...
        ...     def run(self):
        ...         project_key = self.get_project_key()
        ...         sprint = self.get_sprint_selection(project_key)
        ...         # Custom analysis logic here
    """
    
    def __init__(self, tool_name):
        self.tool_name = tool_name
        self.jira_client = JiraClient()

        # Initialize exclusions manager based on class name
        class_name = self.__class__.__name__
        # Convert class name from CamelCase to snake_case tool name
        tool_name_for_exclusions = self._camel_to_snake(class_name).replace('_tool', '').replace('scrummaster_', '')
        if not tool_name_for_exclusions:
            tool_name_for_exclusions = 'base_tool'  # fallback

        self.exclusions_manager = ExclusionsManager(tool_name_for_exclusions)
        self._ensure_output_directories()
        logger.info(f"Initializing tool: {tool_name} (exclusions: {tool_name_for_exclusions})")

    def _ensure_output_directories(self):
        """Ensure output directories exist"""
        for path in OUTPUT_PATHS.values():
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.debug(f"Created directory: {path}")

    def get_project_key(self):
        """
        Get and validate project key from user input.

        Prompts user for project name or key, validates it against Jira,
        and returns the validated project key.

        Returns:
            str: Validated Jira project key

        Raises:
            ValueError: If project input is empty or project doesn't exist/no permissions

        Example:
            >>> tool = MyAnalysisTool()
            >>> project_key = tool.get_project_key()
            📝 Enter project name or key (e.g. TMM or APIM): PROJ
            🎯 Working with project: PROJ
        """
        print(f"🎯 {self.tool_name}")
        print("=" * 50)
        project_input = input("📝 Enter project name or key (e.g. TMM or APIM): ").strip()

        if not project_input:
            raise ValueError("Project name/key cannot be empty!")

        # Validate project (try both name and key)
        project_key = self.jira_client.validate_project_key(project_input)
        if not project_key:
            raise ValueError(f"Project '{project_input}' does not exist or you don't have permissions!")

        print(f"🎯 Working with project: {project_key}")
        return project_key

    def get_project_exclusions(self, project_key):
        """Load and manage exclusions for project using interactive UI"""
        return self.exclusions_manager.get_interactive_exclusions(project_key)

    def get_project_exclusions_silent(self, project_key, exclusion_type='issues'):
        """Load exclusions for project without interactive UI"""
        return self.exclusions_manager.get_exclusions_for_project(project_key, exclusion_type)

    def get_sprint_selection(self, project_key):
        """
        Interactive sprint selection for analysis.

        Discovers project boards, allows user to select board (if multiple),
        then displays available sprints and allows user to select one for analysis.

        Args:
            project_key (str): Validated Jira project key

        Returns:
            dict: Selected sprint information containing id, name, state, dates

        Raises:
            ValueError: If no boards or sprints found, or invalid selection

        Example:
            >>> sprint = tool.get_sprint_selection("PROJ")
            📋 Checking boards for project PROJ...
            ✅ Found 2 boards:
               1. PROJ Scrum Board (scrum)
               2. PROJ Kanban Board (kanban)
        """
        print(f"\n📋 Checking boards for project {project_key}...")

        # Get all boards for the project
        boards = self.jira_client.get_project_boards(project_key)

        board_id = None
        board_name = None

        # If multiple boards exist, let user choose
        if len(boards) > 1:
            print(f"✅ Found {len(boards)} boards:")
            print()

            for i, board in enumerate(boards, 1):
                board_name = board.get('name', 'Unknown')
                board_type = board.get('type', 'scrum')
                print(f"   {i:2d}. {board_name} ({board_type})")

            print()

            while True:
                try:
                    choice = input("📝 Choose board number: ").strip()
                    board_index = int(choice) - 1

                    if 0 <= board_index < len(boards):
                        selected_board = boards[board_index]
                        board_id = selected_board['id']
                        board_name = selected_board.get('name', 'Unknown')
                        print(f"✅ Selected board: {board_name}")
                        break
                    else:
                        print(f"❌ Error: Choose number from 1 to {len(boards)}")
                except ValueError:
                    print("❌ Error: Enter valid number")
        elif len(boards) == 1:
            # Only one board, use it automatically
            board_id = boards[0]['id']
            board_name = boards[0].get('name', 'Unknown')
            print(f"✅ Using board: {board_name}")
        else:
            # No boards found
            raise ValueError(f"No boards found for project {project_key}")

        print(f"\n📅 Fetching sprints from board '{board_name}'...")

        try:
            sprints = self.jira_client.get_project_sprints(project_key, board_id)
        except Exception as e:
            raise ValueError(f"Cannot fetch sprints: {str(e)}")

        if not sprints:
            raise ValueError(f"No sprints found on board '{board_name}' for project {project_key}")

        # Sort sprints by end date (oldest first, newest at bottom for better readability)
        sprints.sort(key=lambda x: x.get('endDate', ''), reverse=False)

        print(f"✅ Found {len(sprints)} sprints:")
        print()

        # Display sprints with status indicators
        for i, sprint in enumerate(sprints, 1):
            sprint_name = sprint.get('name', 'No name')
            sprint_state = sprint.get('state', 'UNKNOWN')

            # Status indicators
            status_icon = {
                'ACTIVE': '🟢',
                'CLOSED': '🔵',
                'FUTURE': '⚪'
            }.get(sprint_state, '❓')

            print(f"   {i:2d}. {status_icon} {sprint_name} ({sprint_state})")

        print()

        while True:
            try:
                choice = input("📝 Choose sprint number: ").strip()
                sprint_index = int(choice) - 1

                if 0 <= sprint_index < len(sprints):
                    selected_sprint = sprints[sprint_index]
                    sprint_name = selected_sprint.get('name', 'No name')
                    print(f"✅ Selected sprint: {sprint_name}")
                    return selected_sprint
                else:
                    print(f"❌ Error: Choose number from 1 to {len(sprints)}")
            except ValueError:
                print("❌ Error: Enter valid number")

    def generate_output_filename(self, prefix, project_key, sprint_name=None, extension="csv"):
        """Generate output filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Clean sprint name for filename
        if sprint_name:
            sprint_safe = sprint_name.replace(' ', '_').replace('-', '_').replace('/', '_')
            filename = f"{prefix}_{project_key}_{sprint_safe}_{timestamp}.{extension}"
        else:
            filename = f"{prefix}_{project_key}_{timestamp}.{extension}"
        
        return filename

    def get_output_path(self, category, filename):
        """Get full path to output file"""
        if category == "reports":
            base_path = OUTPUT_PATHS['reports']
        elif category == "logs":
            base_path = OUTPUT_PATHS['logs']
        elif category == "exports":
            base_path = OUTPUT_PATHS['exports']
        else:
            base_path = OUTPUT_PATHS['base']
        
        return os.path.join(base_path, filename)

    def print_summary(self, project_key, sprint_name=None, **stats):
        """Print operation summary"""
        print(f"\n📊 SUMMARY:")
        print(f"   • Project: {project_key}")
        if sprint_name:
            print(f"   • Sprint: {sprint_name}")

        for key, value in stats.items():
            print(f"   • {key}: {value}")

        print(f"   • Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _get_category_from_labels_and_components(self, labels, components, categories=None):
        """Determine category from components and labels

        Args:
            labels: List of labels from Jira issue
            components: List of components from Jira issue
            categories: List of categories to check (default: ['Backend', 'Frontend', 'Fullstack', 'DevOps', 'QA'])

        Returns:
            Category name or 'Others' if no match found
        """
        # Default categories if not provided
        if categories is None:
            categories = ['Backend', 'Frontend', 'Fullstack', 'DevOps', 'QA']

        # First check components
        if components:
            for component in components:
                if isinstance(component, dict):
                    component_name = component.get('name', '')
                    if component_name in categories:
                        return component_name

        # If no category from components, check labels
        if labels:
            for label in labels:
                if label in categories:
                    return label

        # No matching category found
        return 'Others'

    def _camel_to_snake(self, name):
        """Convert CamelCase to snake_case"""
        import re
        # Insert an underscore before any uppercase letter that follows a lowercase letter or digit
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        # Insert an underscore before any uppercase letter that follows a lowercase letter
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @abstractmethod
    def run(self):
        """
        Main method to execute the analysis tool.

        This is the template method that must be implemented by all subclasses.
        Should contain the specific analysis logic for each tool, typically following
        the pattern: get project → get sprint → apply exclusions → analyze → output.

        Raises:
            NotImplementedError: This is an abstract method that must be implemented
        """
        pass

    def safe_run(self):
        """Safe tool execution with error handling"""
        try:
            self.run()
        except KeyboardInterrupt:
            print("\n❌ Operation interrupted by user")
        except ValueError as e:
            print(f"❌ Error: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error in {self.tool_name}")
            print(f"❌ Unexpected error occurred: {str(e)}")
            print("💡 Check logs for more details")