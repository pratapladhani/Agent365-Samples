# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Workflows package for Admin Agent

This package contains Agent Framework workflows demonstrating:
- Delegated calendar access verification
- Auto-accept/decline meeting invitations
- Find meeting time and scheduling
- Conflict detection and resolution
"""

from .delegated_access import build_delegated_access_workflow, run_access_verification
from .auto_accept import build_auto_accept_workflow
from .find_meeting_time import build_find_meeting_time_workflow, find_and_schedule_meeting
from .conflict_resolution import build_conflict_resolution_workflow, detect_and_resolve_conflicts

__all__ = [
    "build_delegated_access_workflow",
    "run_access_verification",
    "build_auto_accept_workflow",
    "build_find_meeting_time_workflow",
    "find_and_schedule_meeting",
    "build_conflict_resolution_workflow",
    "detect_and_resolve_conflicts",
]
