# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Auto-Accept/Decline Meeting Workflow

This workflow automates meeting invitation responses based on configurable rules:
- Auto-accept from trusted domains
- Auto-decline meetings outside working hours
- Auto-decline if meeting exceeds maximum duration
- Human-in-the-loop approval for complex cases
"""

import logging
from datetime import datetime, time
from typing import Any, Dict, List, Optional

from agent_framework.workflow import WorkflowBuilder, WorkflowExecutor

logger = logging.getLogger(__name__)


class ReceiveMeetingInviteExecutor(WorkflowExecutor):
    """Executor to process incoming meeting invitation"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate meeting invitation details.
        
        Expected context:
        - event_id: Calendar event ID
        - subject: Meeting subject
        - organizer_email: Organizer's email
        - start_time: Meeting start time (ISO format)
        - end_time: Meeting end time (ISO format)
        - attendees: List of attendee emails
        """
        try:
            event_id = context.get("event_id")
            subject = context.get("subject", "")
            organizer = context.get("organizer_email", "")
            start_time = context.get("start_time")
            end_time = context.get("end_time")
            
            logger.info(f"Received meeting invite: {subject}")
            logger.info(f"  Organizer: {organizer}")
            logger.info(f"  Time: {start_time} - {end_time}")
            
            # Parse times
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            duration_hours = (end_dt - start_dt).total_seconds() / 3600
            
            return {
                "status": "success",
                "event_id": event_id,
                "subject": subject,
                "organizer_email": organizer,
                "organizer_domain": organizer.split('@')[1] if '@' in organizer else "",
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "duration_hours": duration_hours,
                "meeting_day": start_dt.strftime("%A"),
                "meeting_time": start_dt.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to process meeting invite: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


class CheckCalendarAvailabilityExecutor(WorkflowExecutor):
    """Executor to check calendar availability at meeting time"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if there are conflicts in the calendar"""
        try:
            start_dt = context.get("start_datetime")
            end_dt = context.get("end_datetime")
            
            logger.info("Checking calendar availability...")
            
            # TODO: Use Outlook Calendar MCP to check for conflicts
            # - listCalendarEvents with time range
            # - Check for overlapping events
            
            # Placeholder response
            has_conflict = False  # Would be determined by MCP call
            conflicting_events = []
            
            return {
                "status": "success",
                "has_conflict": has_conflict,
                "is_available": not has_conflict,
                "conflicting_events": conflicting_events
            }
            
        except Exception as e:
            logger.error(f"Availability check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "is_available": False
            }


class ApplyAutoAcceptRulesExecutor(WorkflowExecutor):
    """Executor to apply auto-accept/decline rules"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply configured rules to determine meeting response.
        
        Rules checked:
        1. Is organizer from trusted domain?
        2. Is meeting within working hours?
        3. Is meeting duration acceptable?
        4. Is calendar available?
        """
        try:
            # Get meeting details
            organizer_domain = context.get("organizer_domain", "")
            duration_hours = context.get("duration_hours", 0)
            meeting_time = context.get("meeting_time")
            is_available = context.get("is_available", False)
            has_conflict = context.get("has_conflict", False)
            
            # Get rules from context (set by agent initialization)
            trusted_domains = context.get("auto_accept_domains", [])
            max_duration = context.get("auto_accept_max_duration", 2)
            check_working_hours = context.get("auto_decline_outside_hours", True)
            working_hours_start = context.get("working_hours_start", "09:00")
            working_hours_end = context.get("working_hours_end", "17:00")
            
            # Parse working hours
            work_start = time.fromisoformat(working_hours_start)
            work_end = time.fromisoformat(working_hours_end)
            
            # Apply rules
            reasons = []
            decision = "pending"  # Default to pending (requires approval)
            
            # Rule 1: Calendar conflict check
            if has_conflict:
                decision = "needs_approval"
                reasons.append("Calendar conflict detected")
                
            # Rule 2: Trusted domain check
            elif organizer_domain and trusted_domains and organizer_domain in trusted_domains:
                decision = "accept"
                reasons.append(f"Organizer from trusted domain: {organizer_domain}")
                
            # Rule 3: Working hours check
            elif check_working_hours and meeting_time:
                if not (work_start <= meeting_time <= work_end):
                    decision = "decline"
                    reasons.append(f"Meeting outside working hours ({working_hours_start}-{working_hours_end})")
                    
            # Rule 4: Duration check
            if duration_hours > max_duration:
                if decision == "accept":
                    decision = "needs_approval"
                elif decision == "pending":
                    decision = "decline"
                reasons.append(f"Meeting duration ({duration_hours:.1f}h) exceeds maximum ({max_duration}h)")
                
            # Rule 5: Availability check
            if not is_available and decision == "accept":
                decision = "needs_approval"
                reasons.append("Calendar shows unavailability")
            
            # If no rules matched, require approval
            if decision == "pending":
                decision = "needs_approval"
                reasons.append("No automatic rule matched - requires human approval")
            
            logger.info(f"Auto-accept decision: {decision}")
            for reason in reasons:
                logger.info(f"  - {reason}")
            
            return {
                "status": "success",
                "decision": decision,  # "accept", "decline", or "needs_approval"
                "reasons": reasons,
                "requires_approval": decision == "needs_approval"
            }
            
        except Exception as e:
            logger.error(f"Rule application failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "decision": "needs_approval",
                "requires_approval": True
            }


class RequestApprovalExecutor(WorkflowExecutor):
    """Executor to request human approval for meeting response"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Request human-in-the-loop approval"""
        try:
            decision = context.get("decision")
            
            # Skip if approval not required
            if not context.get("requires_approval", False):
                return {
                    "status": "skipped",
                    "approved_decision": decision
                }
            
            subject = context.get("subject", "")
            organizer = context.get("organizer_email", "")
            reasons = context.get("reasons", [])
            
            logger.info(f"Requesting approval for meeting: {subject}")
            
            # TODO: Implement approval request
            # This could use:
            # - Agent 365 notifications
            # - Teams adaptive card
            # - Email notification
            
            # For now, return placeholder
            approval_message = f"""
📅 Meeting Response Approval Required

Subject: {subject}
Organizer: {organizer}
Time: {context.get('start_datetime')} - {context.get('end_datetime')}

Reasons for approval request:
{chr(10).join(f'  • {r}' for r in reasons)}

Please approve or decline this meeting response.
"""
            
            logger.info(approval_message)
            
            return {
                "status": "pending_approval",
                "approval_message": approval_message,
                "approved_decision": None  # Will be set by human
            }
            
        except Exception as e:
            logger.error(f"Approval request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class SendMeetingResponseExecutor(WorkflowExecutor):
    """Executor to send meeting acceptance or decline"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send the meeting response via Outlook Calendar MCP"""
        try:
            event_id = context.get("event_id")
            decision = context.get("approved_decision") or context.get("decision")
            subject = context.get("subject", "")
            reasons = context.get("reasons", [])
            
            if not decision or decision not in ["accept", "decline"]:
                return {
                    "status": "skipped",
                    "message": "No decision to execute"
                }
            
            # Generate response comment
            comment = f"Automated response by Admin Agent. {reasons[0] if reasons else ''}"
            
            logger.info(f"{decision.upper()} meeting: {subject}")
            
            # TODO: Call Outlook Calendar MCP tools
            # - acceptMeeting(event_id, comment) if decision == "accept"
            # - declineMeeting(event_id, comment) if decision == "decline"
            
            return {
                "status": "success",
                "action_taken": decision,
                "event_id": event_id,
                "comment": comment,
                "message": f"✅ Meeting {decision}ed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to send meeting response: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": f"❌ Failed to {decision} meeting: {str(e)}"
            }


def build_auto_accept_workflow(
    auto_accept_domains: List[str],
    auto_accept_max_duration: int,
    auto_decline_outside_hours: bool,
    working_hours_start: str,
    working_hours_end: str
) -> WorkflowBuilder:
    """
    Build the auto-accept/decline workflow.
    
    Args:
        auto_accept_domains: List of trusted domains for auto-accept
        auto_accept_max_duration: Maximum meeting duration in hours
        auto_decline_outside_hours: Whether to decline outside working hours
        working_hours_start: Working hours start time (HH:MM)
        working_hours_end: Working hours end time (HH:MM)
        
    Returns:
        Configured WorkflowBuilder
    """
    workflow = (
        WorkflowBuilder()
        .register_executor(ReceiveMeetingInviteExecutor, name="receive_invite")
        .register_executor(CheckCalendarAvailabilityExecutor, name="check_availability")
        .register_executor(ApplyAutoAcceptRulesExecutor, name="apply_rules")
        .register_executor(RequestApprovalExecutor, name="request_approval")
        .register_executor(SendMeetingResponseExecutor, name="send_response")
        .set_initial_state({
            "workflow_name": "auto_accept_decline",
            "workflow_version": "1.0",
            "auto_accept_domains": auto_accept_domains,
            "auto_accept_max_duration": auto_accept_max_duration,
            "auto_decline_outside_hours": auto_decline_outside_hours,
            "working_hours_start": working_hours_start,
            "working_hours_end": working_hours_end
        })
    )
    
    logger.info("✅ Auto-accept/decline workflow built")
    return workflow
