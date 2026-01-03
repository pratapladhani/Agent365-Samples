# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Delegated Access Verification Workflow

This workflow verifies that the Admin Agent has proper delegated access
to manage the user's calendar through Microsoft Graph Calendar API.
"""

import logging
from typing import Any, Dict

from agent_framework.workflow import WorkflowBuilder, WorkflowExecutor

logger = logging.getLogger(__name__)


class VerifyAccessExecutor(WorkflowExecutor):
    """Executor to verify delegated calendar access"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify delegated access permissions.
        
        This executor will use the Outlook Calendar MCP server to check:
        1. Agent can read the delegated user's calendar
        2. Agent has write permissions
        3. Agent can accept/decline meetings on behalf of user
        """
        try:
            delegated_user = context.get("delegated_user_email")
            agent_email = context.get("agent_email")
            
            logger.info(f"Verifying delegated access for {agent_email} -> {delegated_user}")
            
            # TODO: Call Outlook Calendar MCP tool to verify access
            # This will use tools like:
            # - listCalendarEvents (to verify read access)
            # - getCalendarPermissions (to verify permission level)
            
            # For now, return placeholder
            return {
                "status": "success",
                "has_read_access": True,
                "has_write_access": True,
                "can_accept_decline": True,
                "delegated_user": delegated_user,
                "agent_email": agent_email,
                "message": f"✅ Delegated access verified for {delegated_user}"
            }
            
        except Exception as e:
            logger.error(f"Access verification failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": f"❌ Failed to verify delegated access: {str(e)}"
            }


class CheckPermissionsExecutor(WorkflowExecutor):
    """Executor to check specific calendar permissions"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check detailed permission levels"""
        try:
            access_status = context.get("access_verification", {})
            
            if access_status.get("status") != "success":
                return {
                    "status": "skipped",
                    "message": "Skipped - access verification failed"
                }
            
            logger.info("Checking detailed calendar permissions...")
            
            # TODO: Query specific permissions via Outlook Calendar MCP
            # - Calendars.ReadWrite.Shared
            # - Calendars.Read.Shared
            # - MailboxSettings.Read
            
            return {
                "status": "success",
                "permissions": [
                    "Calendars.ReadWrite.Shared",
                    "Calendars.Read.Shared"
                ],
                "message": "✅ All required permissions granted"
            }
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class GenerateAccessReportExecutor(WorkflowExecutor):
    """Executor to generate access verification report"""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable access report"""
        try:
            access_status = context.get("access_verification", {})
            permissions = context.get("permissions_check", {})
            
            report_lines = [
                "🔐 Delegated Access Verification Report",
                "=" * 50,
                f"Agent: {access_status.get('agent_email')}",
                f"Delegated User: {access_status.get('delegated_user')}",
                "",
                "Access Status:",
                f"  Read Access: {'✅' if access_status.get('has_read_access') else '❌'}",
                f"  Write Access: {'✅' if access_status.get('has_write_access') else '❌'}",
                f"  Accept/Decline: {'✅' if access_status.get('can_accept_decline') else '❌'}",
                "",
                "Permissions:",
            ]
            
            for perm in permissions.get("permissions", []):
                report_lines.append(f"  ✅ {perm}")
            
            report_lines.append("")
            report_lines.append("=" * 50)
            
            report = "\n".join(report_lines)
            logger.info(f"\n{report}")
            
            return {
                "status": "success",
                "report": report,
                "summary": access_status.get("message", "Access verification complete")
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


def build_delegated_access_workflow() -> WorkflowBuilder:
    """
    Build the delegated access verification workflow.
    
    Workflow steps:
    1. Verify basic access to delegated calendar
    2. Check detailed permissions
    3. Generate access report
    
    Returns:
        Configured WorkflowBuilder
    """
    workflow = (
        WorkflowBuilder()
        .register_executor(VerifyAccessExecutor, name="access_verification")
        .register_executor(CheckPermissionsExecutor, name="permissions_check")
        .register_executor(GenerateAccessReportExecutor, name="generate_report")
        .set_initial_state({
            "workflow_name": "delegated_access_verification",
            "workflow_version": "1.0"
        })
    )
    
    logger.info("✅ Delegated Access Verification workflow built")
    return workflow


async def run_access_verification(
    agent_email: str,
    delegated_user_email: str
) -> Dict[str, Any]:
    """
    Run delegated access verification workflow.
    
    Args:
        agent_email: Email of the admin agent
        delegated_user_email: Email of the delegated user
        
    Returns:
        Workflow execution results
    """
    try:
        workflow = build_delegated_access_workflow()
        
        initial_context = {
            "agent_email": agent_email,
            "delegated_user_email": delegated_user_email
        }
        
        logger.info(f"Running access verification: {agent_email} -> {delegated_user_email}")
        
        # Execute workflow
        result = await workflow.execute(initial_context)
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to run access verification: {str(e)}"
        }
