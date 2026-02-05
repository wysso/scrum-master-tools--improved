"""
ScrumMaster Tools - Tools for analyzing Jira projects

Package contains a set of tools for analyzing Jira data,
designed for ScrumMasters and development teams.

Author: Marek Mróz <marek@mroz.consulting>
"""

__version__ = "2.0.0"

# Import main classes for easier access
from .core.base_tool import BaseScrumMasterTool
from .core.jira_client import JiraClient

# Import all tools
from .tools.anomaly_detector import AnomalyDetectorTool
from .tools.sprint_completion import SprintCompletionTool
from .tools.worklog_summary import WorklogSummaryTool
from .tools.planning import PlanningTool

# Import helpers
from .helpers.connection_test import ConnectionTestTool
from .helpers.projects_lister import ProjectsListerTool
from .helpers.label_updater import LabelUpdaterTool
from .helpers.custom_fields_identifier import CustomFieldsIdentifierTool

__all__ = [
    'BaseScrumMasterTool',
    'JiraClient',
    'AnomalyDetectorTool',
    'SprintCompletionTool',
    'WorklogSummaryTool',
    'PlanningTool',
    'CustomFieldsIdentifierTool',
    'ConnectionTestTool',
    'ProjectsListerTool',
    'LabelUpdaterTool'
]