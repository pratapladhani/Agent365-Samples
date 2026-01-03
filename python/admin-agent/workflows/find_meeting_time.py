# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Find Meeting Time Workflow

This workflow helps find optimal meeting times and schedule meetings:
1. Parse natural language meeting request
2. Extract attendees and constraints
3. Query availability via Outlook Calendar MCP
4. Suggest optimal meeting slots
5. Create meeting with user confirmation
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agent_framework.workflow import WorkflowBuilder, WorkflowExecutor

logger = logging.getLogger(__name__)


class ParseMeetingRequestExecutor(WorkflowExecutor):
    """Executor to parse natural language meeting request"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract meeting details from natural language request.
        
        Expected context:
        - user_message: Natural language request (e.g., "Find time with sarah@contoso.com tomorrow")
        
        Returns:
        - attendees: List of email addresses
        - duration_minutes: Meeting duration
        - time_constraints: Start/end time constraints
        - preferences: User preferences (morning/afternoon, etc.)
        """
        try:
            user_message = context.get("user_message", "")
            
            logger.info(f"Parsing meeting request: {user_message}")
            
            # TODO: Use LLM to extract structured data from natural language
            # This would use the ChatAgent to parse the message
            
            # Placeholder extraction
            attendees = []
            duration_minutes = 60  # Default 1 hour
            
            # Extract email addresses (simple regex)
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            attendees = re.findall(email_pattern, user_message.lower())
            
            # Extract duration hints
            if "30 min" in user_message.lower() or "half hour" in user_message.lower():
                duration_minutes = 30
            elif "2 hour" in user_message.lower():
                duration_minutes = 120
            
            # Extract time constraints
            time_constraint_start = None
            time_constraint_end = None
            
            if "tomorrow" in user_message.lower():
                tomorrow = datetime.now() + timedelta(days=1)
                time_constraint_start = tomorrow.replace(hour=9, minute=0, second=0)
                time_constraint_end = tomorrow.replace(hour=17, minute=0, second=0)
            elif "this week" in user_message.lower():
                today = datetime.now()
                time_constraint_start = today
                time_constraint_end = today + timedelta(days=7)
            elif "next week" in user_message.lower():
                today = datetime.now()
                time_constraint_start = today + timedelta(days=7)
                time_constraint_end = today + timedelta(days=14)
            else:
                # Default: next 3 business days
                today = datetime.now()
                time_constraint_start = today
                time_constraint_end = today + timedelta(days=3)
            
            logger.info(f"Extracted: {len(attendees)} attendees, {duration_minutes}min duration")
            
            return {
                "status": "success",
                "attendees": attendees,
                "duration_minutes": duration_minutes,
                "time_constraint_start": time_constraint_start.isoformat() if time_constraint_start else None,
                "time_constraint_end": time_constraint_end.isoformat() if time_constraint_end else None,
                "original_request": user_message
            }
            
        except Exception as e:
            logger.error(f"Failed to parse meeting request: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


class QueryAvailabilityExecutor(WorkflowExecutor):
    """Executor to query availability using Outlook Calendar MCP"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query availability for all attendees using findMeetingTimes.
        
        Uses Outlook Calendar MCP's findMeetingTimes tool to get:
        - Available time slots
        - Confidence scores for each slot
        - Attendee availability status
        """
        try:
            attendees = context.get("attendees", [])
            duration_minutes = context.get("duration_minutes", 60)
            time_constraint_start = context.get("time_constraint_start")
            time_constraint_end = context.get("time_constraint_end")
            
            if not attendees:
                return {
                    "status": "error",
                    "error": "No attendees specified"
                }
            
            logger.info(f"Querying availability for {len(attendees)} attendees...")
            logger.info(f"  Duration: {duration_minutes} minutes")
            logger.info(f"  Time range: {time_constraint_start} to {time_constraint_end}")
            
            # TODO: Call Outlook Calendar MCP findMeetingTimes tool
            # This would return:
            # - Available time slots
            # - Confidence scores
            # - Attendee statuses
            
            # Placeholder response
            available_slots = [
                {
                    "start": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                    "end": (datetime.now() + timedelta(days=1, hours=11)).isoformat(),
                    "confidence": 100,
                    "attendee_availability": "all_available"
                },
                {
                    "start": (datetime.now() + timedelta(days=1, hours=14)).isoformat(),
                    "end": (datetime.now() + timedelta(days=1, hours=15)).isoformat(),
                    "confidence": 100,
                    "attendee_availability": "all_available"
                },
                {
                    "start": (datetime.now() + timedelta(days=2, hours=11)).isoformat(),
                    "end": (datetime.now() + timedelta(days=2, hours=12)).isoformat(),
                    "confidence": 80,
                    "attendee_availability": "some_tentative"
                }
            ]
            
            return {
                "status": "success",
                "available_slots": available_slots,
                "total_slots_found": len(available_slots)
            }
            
        except Exception as e:
            logger.error(f"Availability query failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "available_slots": []
            }


class RankMeetingTimesExecutor(WorkflowExecutor):
    """Executor to rank and suggest optimal meeting times"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank available slots by optimality considering:
        - Attendee availability confidence
        - Time of day preferences
        - Proximity to other meetings
        - Work hours alignment
        """
        try:
            available_slots = context.get("available_slots", [])
            
            if not available_slots:
                return {
                    "status": "error",
                    "error": "No available slots to rank"
                }
            
            logger.info(f"Ranking {len(available_slots)} meeting time slots...")
            
            # Sort by confidence score (placeholder logic)
            ranked_slots = sorted(
                available_slots,
                key=lambda x: x.get("confidence", 0),
                reverse=True
            )
            
            # Take top 3 suggestions
            top_suggestions = ranked_slots[:3]
            
            # Format suggestions for user
            suggestions_text = []
            for i, slot in enumerate(top_suggestions, 1):
                start_dt = datetime.fromisoformat(slot["start"])
                end_dt = datetime.fromisoformat(slot["end"])
                suggestions_text.append(
                    f"{i}. {start_dt.strftime('%A, %B %d at %I:%M %p')} - {end_dt.strftime('%I:%M %p')} "
                    f"(confidence: {slot['confidence']}%)"
                )
            
            suggestions_message = "\n".join(suggestions_text)
            logger.info(f"Top suggestions:\n{suggestions_message}")
            
            return {
                "status": "success",
                "ranked_slots": ranked_slots,
                "top_suggestions": top_suggestions,
                "suggestions_message": suggestions_message
            }
            
        except Exception as e:
            logger.error(f"Ranking failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


class RequestTimeSelectionExecutor(WorkflowExecutor):
    """Executor to request user selection of meeting time"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Present suggestions and request user selection"""
        try:
            suggestions_message = context.get("suggestions_message", "")
            top_suggestions = context.get("top_suggestions", [])
            
            if not top_suggestions:
                return {
                    "status": "error",
                    "error": "No suggestions available"
                }
            
            logger.info("Requesting user to select meeting time...")
            
            # TODO: Use Agent 365 notifications or adaptive cards
            # to present options and get selection
            
            selection_prompt = f"""
📅 Available Meeting Times

I found the following times that work for everyone:

{suggestions_message}

Which time works best for you? (Reply with 1, 2, or 3, or ask me to find more options)
"""
            
            logger.info(selection_prompt)
            
            # Placeholder: Auto-select first option for demo
            selected_slot = top_suggestions[0]
            
            return {
                "status": "success",
                "selection_prompt": selection_prompt,
                "selected_slot": selected_slot,
                "selected_index": 0
            }
            
        except Exception as e:
            logger.error(f"Selection request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class CreateMeetingExecutor(WorkflowExecutor):
    """Executor to create the meeting via Outlook Calendar MCP"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create meeting on user's calendar"""
        try:
            selected_slot = context.get("selected_slot")
            attendees = context.get("attendees", [])
            original_request = context.get("original_request", "")
            
            if not selected_slot:
                return {
                    "status": "error",
                    "error": "No time slot selected"
                }
            
            # Extract meeting details
            start_time = selected_slot["start"]
            end_time = selected_slot["end"]
            
            # Generate meeting subject from original request
            subject = "Meeting"  # Could use LLM to generate better subject
            if "about" in original_request.lower():
                # Extract topic
                subject = original_request.split("about")[-1].strip()[:50]
            
            logger.info(f"Creating meeting: {subject}")
            logger.info(f"  Time: {start_time} - {end_time}")
            logger.info(f"  Attendees: {', '.join(attendees)}")
            
            # TODO: Call Outlook Calendar MCP createCalendarEvent tool
            # Parameters:
            # - subject
            # - start_datetime (ISO format)
            # - end_datetime (ISO format)
            # - attendees (list of emails)
            # - body (optional)
            # - location (optional)
            
            # Placeholder response
            event_id = "placeholder_event_123"
            
            return {
                "status": "success",
                "event_id": event_id,
                "subject": subject,
                "start_time": start_time,
                "end_time": end_time,
                "attendees": attendees,
                "message": f"✅ Meeting created: {subject}"
            }
            
        except Exception as e:
            logger.error(f"Meeting creation failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": f"❌ Failed to create meeting: {str(e)}"
            }


class SendConfirmationExecutor(WorkflowExecutor):
    """Executor to send meeting creation confirmation"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send confirmation to user"""
        try:
            event_status = context.get("create_meeting", {})
            
            if event_status.get("status") != "success":
                return {
                    "status": "error",
                    "message": "Meeting creation failed - no confirmation sent"
                }
            
            subject = event_status.get("subject")
            start_time = event_status.get("start_time")
            attendees = event_status.get("attendees", [])
            
            start_dt = datetime.fromisoformat(start_time)
            
            confirmation_message = f"""
✅ Meeting Scheduled Successfully!

📅 {subject}
🕒 {start_dt.strftime('%A, %B %d at %I:%M %p')}
👥 Attendees: {', '.join(attendees)}

Calendar invitations have been sent to all attendees.
"""
            
            logger.info(confirmation_message)
            
            return {
                "status": "success",
                "confirmation_message": confirmation_message
            }
            
        except Exception as e:
            logger.error(f"Confirmation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


def build_find_meeting_time_workflow() -> WorkflowBuilder:
    """
    Build the find meeting time workflow.
    
    Workflow steps:
    1. Parse natural language meeting request
    2. Query availability for attendees
    3. Rank meeting times by optimality
    4. Request user selection
    5. Create meeting
    6. Send confirmation
    
    Returns:
        Configured WorkflowBuilder
    """
    workflow = (
        WorkflowBuilder()
        .register_executor(ParseMeetingRequestExecutor, name="parse_request")
        .register_executor(QueryAvailabilityExecutor, name="query_availability")
        .register_executor(RankMeetingTimesExecutor, name="rank_times")
        .register_executor(RequestTimeSelectionExecutor, name="request_selection")
        .register_executor(CreateMeetingExecutor, name="create_meeting")
        .register_executor(SendConfirmationExecutor, name="send_confirmation")
        .set_initial_state({
            "workflow_name": "find_meeting_time",
            "workflow_version": "1.0"
        })
    )
    
    logger.info("✅ Find meeting time workflow built")
    return workflow


async def find_and_schedule_meeting(user_message: str) -> Dict[str, Any]:
    """
    Run find meeting time workflow.
    
    Args:
        user_message: Natural language meeting request
        
    Returns:
        Workflow execution results
    """
    try:
        workflow = build_find_meeting_time_workflow()
        
        initial_context = {
            "user_message": user_message
        }
        
        logger.info(f"Finding meeting time for: {user_message}")
        
        # Execute workflow
        result = await workflow.execute(initial_context)
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to find meeting time: {str(e)}"
        }
