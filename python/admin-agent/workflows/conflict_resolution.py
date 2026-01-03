# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Conflict Detection and Resolution Workflow

This workflow monitors for calendar conflicts and helps resolve them:
1. Detect double-bookings and overlapping meetings
2. Analyze meeting priority and importance
3. Suggest resolution strategies
4. Execute resolution with human approval
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agent_framework.workflow import WorkflowBuilder, WorkflowExecutor

logger = logging.getLogger(__name__)


class DetectConflictsExecutor(WorkflowExecutor):
    """Executor to detect calendar conflicts"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan calendar for conflicts (overlapping events).
        
        Expected context:
        - time_range_start: Start of scan window (optional, default: now)
        - time_range_end: End of scan window (optional, default: +7 days)
        """
        try:
            # Get time range
            time_range_start = context.get("time_range_start")
            if not time_range_start:
                time_range_start = datetime.now()
            elif isinstance(time_range_start, str):
                time_range_start = datetime.fromisoformat(time_range_start)
            
            time_range_end = context.get("time_range_end")
            if not time_range_end:
                time_range_end = time_range_start + timedelta(days=7)
            elif isinstance(time_range_end, str):
                time_range_end = datetime.fromisoformat(time_range_end)
            
            logger.info(f"Scanning for conflicts: {time_range_start} to {time_range_end}")
            
            # TODO: Call Outlook Calendar MCP listCalendarEvents
            # Get all events in time range and check for overlaps
            
            # Placeholder conflict detection
            conflicts = [
                {
                    "conflict_id": "conflict_1",
                    "event_1": {
                        "id": "event_123",
                        "subject": "Team Standup",
                        "organizer": "manager@contoso.com",
                        "start": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                        "end": (datetime.now() + timedelta(days=1, hours=11)).isoformat(),
                        "required_attendees": 5
                    },
                    "event_2": {
                        "id": "event_456",
                        "subject": "Client Call",
                        "organizer": "client@external.com",
                        "start": (datetime.now() + timedelta(days=1, hours=10, minutes=30)).isoformat(),
                        "end": (datetime.now() + timedelta(days=1, hours=11, minutes=30)).isoformat(),
                        "required_attendees": 3
                    },
                    "overlap_minutes": 30
                }
            ]
            
            logger.info(f"Found {len(conflicts)} conflict(s)")
            
            return {
                "status": "success",
                "conflicts": conflicts,
                "total_conflicts": len(conflicts),
                "has_conflicts": len(conflicts) > 0
            }
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "conflicts": [],
                "has_conflicts": False
            }


class AnalyzePriorityExecutor(WorkflowExecutor):
    """Executor to analyze meeting priority and importance"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze priority of conflicting meetings using various signals:
        - Organizer (internal vs external, seniority)
        - Number of required attendees
        - Meeting recurrence
        - Time until meeting
        - Past user behavior
        """
        try:
            conflicts = context.get("conflicts", [])
            
            if not conflicts:
                return {
                    "status": "skipped",
                    "message": "No conflicts to analyze"
                }
            
            logger.info(f"Analyzing priority for {len(conflicts)} conflict(s)...")
            
            analyzed_conflicts = []
            
            for conflict in conflicts:
                event_1 = conflict["event_1"]
                event_2 = conflict["event_2"]
                
                # Calculate priority scores (placeholder logic)
                score_1 = self._calculate_priority_score(event_1)
                score_2 = self._calculate_priority_score(event_2)
                
                # Determine higher priority event
                if score_1 > score_2:
                    higher_priority = event_1
                    lower_priority = event_2
                    recommendation = "decline_event_2"
                else:
                    higher_priority = event_2
                    lower_priority = event_1
                    recommendation = "decline_event_1"
                
                analyzed_conflicts.append({
                    **conflict,
                    "event_1_priority_score": score_1,
                    "event_2_priority_score": score_2,
                    "higher_priority_event": higher_priority,
                    "lower_priority_event": lower_priority,
                    "recommendation": recommendation,
                    "confidence": "medium"  # Could be calculated based on score difference
                })
                
                logger.info(f"  Conflict: {event_1['subject']} (score: {score_1}) vs {event_2['subject']} (score: {score_2})")
                logger.info(f"  Recommendation: {recommendation}")
            
            return {
                "status": "success",
                "analyzed_conflicts": analyzed_conflicts
            }
            
        except Exception as e:
            logger.error(f"Priority analysis failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_priority_score(self, event: Dict[str, Any]) -> int:
        """Calculate priority score for an event (placeholder logic)"""
        score = 50  # Base score
        
        # External organizers get higher priority
        organizer = event.get("organizer", "")
        if "@external.com" in organizer or "@client.com" in organizer:
            score += 30
        
        # More attendees = higher priority
        required_attendees = event.get("required_attendees", 0)
        score += min(required_attendees * 5, 20)
        
        # Keywords in subject
        subject = event.get("subject", "").lower()
        if any(word in subject for word in ["client", "customer", "executive"]):
            score += 20
        if any(word in subject for word in ["1:1", "one-on-one"]):
            score += 15
        
        return score


class GenerateResolutionStrategiesExecutor(WorkflowExecutor):
    """Executor to generate resolution strategies"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate multiple resolution strategies for each conflict:
        - Decline lower priority meeting
        - Propose alternate time for one meeting
        - Shorten one or both meetings
        - Delegate attendance to another team member
        """
        try:
            analyzed_conflicts = context.get("analyzed_conflicts", [])
            
            if not analyzed_conflicts:
                return {
                    "status": "skipped",
                    "message": "No conflicts to resolve"
                }
            
            logger.info("Generating resolution strategies...")
            
            conflicts_with_strategies = []
            
            for conflict in analyzed_conflicts:
                higher_priority = conflict["higher_priority_event"]
                lower_priority = conflict["lower_priority_event"]
                
                # Generate multiple strategies
                strategies = [
                    {
                        "strategy": "decline_lower_priority",
                        "description": f"Decline '{lower_priority['subject']}' to attend '{higher_priority['subject']}'",
                        "action": "decline",
                        "target_event_id": lower_priority["id"],
                        "confidence": "high",
                        "trade_offs": "Will miss lower priority meeting"
                    },
                    {
                        "strategy": "reschedule_lower_priority",
                        "description": f"Request to reschedule '{lower_priority['subject']}' to avoid conflict",
                        "action": "request_reschedule",
                        "target_event_id": lower_priority["id"],
                        "confidence": "medium",
                        "trade_offs": "Requires organizer cooperation"
                    },
                    {
                        "strategy": "shorten_both",
                        "description": f"Attend first 30min of '{higher_priority['subject']}', then join '{lower_priority['subject']}'",
                        "action": "partial_attendance",
                        "confidence": "low",
                        "trade_offs": "Partial attendance at both meetings"
                    }
                ]
                
                conflicts_with_strategies.append({
                    **conflict,
                    "resolution_strategies": strategies,
                    "recommended_strategy": strategies[0]  # First strategy is recommended
                })
                
                logger.info(f"  Generated {len(strategies)} strategies for conflict")
            
            return {
                "status": "success",
                "conflicts_with_strategies": conflicts_with_strategies
            }
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


class RequestResolutionApprovalExecutor(WorkflowExecutor):
    """Executor to request human approval for conflict resolution"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Present conflict and strategies to user for approval"""
        try:
            conflicts_with_strategies = context.get("conflicts_with_strategies", [])
            
            if not conflicts_with_strategies:
                return {
                    "status": "skipped",
                    "message": "No conflicts requiring approval"
                }
            
            logger.info("Requesting approval for conflict resolution...")
            
            approval_requests = []
            
            for conflict in conflicts_with_strategies:
                event_1 = conflict["event_1"]
                event_2 = conflict["event_2"]
                recommended_strategy = conflict["recommended_strategy"]
                all_strategies = conflict["resolution_strategies"]
                
                # Format approval message
                approval_message = f"""
⚠️ Calendar Conflict Detected

Meeting 1: {event_1['subject']}
  Organizer: {event_1['organizer']}
  Time: {datetime.fromisoformat(event_1['start']).strftime('%A, %B %d at %I:%M %p')}
  Priority Score: {conflict['event_1_priority_score']}

Meeting 2: {event_2['subject']}
  Organizer: {event_2['organizer']}
  Time: {datetime.fromisoformat(event_2['start']).strftime('%A, %B %d at %I:%M %p')}
  Priority Score: {conflict['event_2_priority_score']}

Overlap: {conflict['overlap_minutes']} minutes

🎯 Recommended Resolution:
{recommended_strategy['description']}
Trade-offs: {recommended_strategy['trade_offs']}

Other Options:
"""
                for i, strategy in enumerate(all_strategies[1:], 2):
                    approval_message += f"\n{i}. {strategy['description']}"
                
                approval_message += "\n\nDo you approve the recommended resolution? (Yes/No/Choose option #)"
                
                logger.info(approval_message)
                
                # TODO: Use Agent 365 notifications to get user approval
                # For now, auto-approve for demo purposes
                approved_strategy = recommended_strategy
                
                approval_requests.append({
                    "conflict_id": conflict["conflict_id"],
                    "approval_message": approval_message,
                    "approved": True,
                    "approved_strategy": approved_strategy
                })
            
            return {
                "status": "success",
                "approval_requests": approval_requests,
                "all_approved": True  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Approval request failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


class ExecuteResolutionExecutor(WorkflowExecutor):
    """Executor to execute approved resolution strategy"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the approved resolution actions"""
        try:
            approval_requests = context.get("approval_requests", [])
            
            if not approval_requests:
                return {
                    "status": "skipped",
                    "message": "No approved resolutions to execute"
                }
            
            logger.info("Executing conflict resolutions...")
            
            execution_results = []
            
            for approval in approval_requests:
                if not approval.get("approved"):
                    continue
                
                strategy = approval["approved_strategy"]
                action = strategy["action"]
                
                if action == "decline":
                    # TODO: Call Outlook Calendar MCP declineMeeting tool
                    target_event_id = strategy["target_event_id"]
                    logger.info(f"Declining meeting: {target_event_id}")
                    
                    execution_results.append({
                        "conflict_id": approval["conflict_id"],
                        "action": "decline",
                        "status": "success",
                        "message": f"✅ Declined meeting {target_event_id}"
                    })
                    
                elif action == "request_reschedule":
                    # TODO: Send reschedule request via Outlook Mail MCP
                    logger.info("Sending reschedule request...")
                    
                    execution_results.append({
                        "conflict_id": approval["conflict_id"],
                        "action": "reschedule_request",
                        "status": "success",
                        "message": "✅ Reschedule request sent"
                    })
                
                else:
                    execution_results.append({
                        "conflict_id": approval["conflict_id"],
                        "action": action,
                        "status": "manual",
                        "message": "Manual action required by user"
                    })
            
            return {
                "status": "success",
                "execution_results": execution_results,
                "resolved_conflicts": len(execution_results)
            }
            
        except Exception as e:
            logger.error(f"Resolution execution failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


def build_conflict_resolution_workflow() -> WorkflowBuilder:
    """
    Build the conflict detection and resolution workflow.
    
    Workflow steps:
    1. Detect calendar conflicts
    2. Analyze meeting priorities
    3. Generate resolution strategies
    4. Request user approval
    5. Execute approved resolution
    
    Returns:
        Configured WorkflowBuilder
    """
    workflow = (
        WorkflowBuilder()
        .register_executor(DetectConflictsExecutor, name="detect_conflicts")
        .register_executor(AnalyzePriorityExecutor, name="analyze_priority")
        .register_executor(GenerateResolutionStrategiesExecutor, name="generate_strategies")
        .register_executor(RequestResolutionApprovalExecutor, name="request_approval")
        .register_executor(ExecuteResolutionExecutor, name="execute_resolution")
        .set_initial_state({
            "workflow_name": "conflict_resolution",
            "workflow_version": "1.0"
        })
    )
    
    logger.info("✅ Conflict resolution workflow built")
    return workflow


async def detect_and_resolve_conflicts(
    time_range_start: Optional[datetime] = None,
    time_range_end: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Run conflict detection and resolution workflow.
    
    Args:
        time_range_start: Start of scan window (default: now)
        time_range_end: End of scan window (default: +7 days)
        
    Returns:
        Workflow execution results
    """
    try:
        workflow = build_conflict_resolution_workflow()
        
        initial_context = {
            "time_range_start": time_range_start.isoformat() if time_range_start else None,
            "time_range_end": time_range_end.isoformat() if time_range_end else None
        }
        
        logger.info("Starting conflict detection and resolution...")
        
        # Execute workflow
        result = await workflow.execute(initial_context)
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to resolve conflicts: {str(e)}"
        }
