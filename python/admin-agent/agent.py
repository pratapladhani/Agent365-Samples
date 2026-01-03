# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Admin Agent - Calendar Management Assistant

This agent demonstrates Agent 365 platform capabilities and Agent Framework features
for intelligent calendar management using delegated access patterns.

## Overview

The Admin Agent acts as a calendar management assistant with its own identity
(e.g., adminagent@contoso.com) that manages calendars for delegated users through
Microsoft Graph Calendar API via Agent 365 MCP servers.

## Architecture

**Delegated Access Model:**
- Agent has its own Microsoft 365 mailbox and identity
- Granted Calendars.ReadWrite.Shared permissions on delegated user's calendar
- Operates independently while respecting user preferences

**Key Components:**
1. **Agent Framework Integration**: Uses ChatAgent with Azure OpenAI for intelligent responses
2. **Agent 365 MCP Servers**: Connects to Outlook Calendar, Mail, Teams, SharePoint, User Profile
3. **Workflows**: Four core workflows demonstrating Agent Framework capabilities
4. **Observability**: OpenTelemetry-based tracing and custom span decorators

## Key Features

**Calendar Management:**
- Verify and maintain delegated calendar access
- List, create, update, and delete calendar events
- Accept/decline meeting invitations with reasoning

**Intelligent Automation:**
- Auto-accept/decline based on configurable rules (sender domain, keywords, time slots)
- Find optimal meeting times using natural language queries
- Detect and resolve calendar conflicts with multiple resolution strategies

**Agent 365 Showcase:**
- Multi-channel deployment (Teams, Email, Documents)
- Premium MCP server integration
- Authentication and authorization patterns
- Agentic behaviors (proactive notifications, context awareness)

**Agent Framework Showcase:**
- Workflow orchestration with executors
- DevUI for workflow visualization (when available)
- Custom observability with span decorators
- Tool integration patterns

## Workflows

1. **Delegated Access Workflow** (`workflows/delegated_access.py`)
   - Verify permissions, test access, validate scopes
   
2. **Auto-Accept Workflow** (`workflows/auto_accept.py`)
   - Process invitations, apply rules, send responses
   
3. **Find Meeting Time Workflow** (`workflows/find_meeting_time.py`)
   - Parse NL query, check availability, create event
   
4. **Conflict Resolution Workflow** (`workflows/conflict_resolution.py`)
   - Detect conflicts, analyze priority, resolve with strategies

## Usage

**Local Testing:**
```python
python test_agent.py
```

**Production Deployment:**
1. Configure Agent 365 CLI: `a365 config init`
2. Setup agent blueprint: `a365 setup`
3. Publish and deploy: `a365 publish`

## Configuration

See `.env.template` for all configuration options including:
- Azure OpenAI credentials
- Agent identity and delegated user
- Working hours and auto-accept rules
- Observability settings

## Dependencies

- agent-framework-azure-ai: Agent Framework with Azure OpenAI integration
- microsoft-agents-*: Agent 365 SDK components
- microsoft_agents_a365_*: Agent 365 observability and tooling
- azure-ai-agents: Azure AI Agents SDK

## License

Copyright (c) Microsoft Corporation. Licensed under the MIT License.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# DEPENDENCY IMPORTS
# =============================================================================

# AgentFramework SDK
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

# Azure Identity
from azure.identity import AzureCliCredential

# Microsoft Agents SDK
from microsoft_agents.hosting.core import Authorization, TurnContext
from microsoft_agents.activity import Activity

# Observability Components
from microsoft_agents_a365.observability.extensions.agentframework.trace_instrumentor import (
    AgentFrameworkInstrumentor,
)

# MCP Tooling
from microsoft_agents_a365.tooling.extensions.agentframework.services.mcp_tool_registration_service import (
    McpToolRegistrationService,
)


# =============================================================================
# ADMIN AGENT CLASS
# =============================================================================

class AdminAgent:
    """
    Admin Agent for intelligent calendar management using delegated access.
    
    This agent operates with its own identity (e.g., adminagent@contoso.com) and
    manages the calendar of a delegated user through Microsoft Graph Calendar API
    via Agent 365 MCP servers.
    """

    AGENT_PROMPT = """You are an Admin Agent, a highly capable calendar management assistant.

Your primary role is to help manage the calendar of your delegated user efficiently.

CAPABILITIES:
- Verify and maintain delegated calendar access
- Automatically accept or decline meeting invitations based on rules
- Find optimal meeting times and schedule meetings
- Detect and resolve calendar conflicts
- Provide meeting preparation briefs
- Analyze calendar patterns and suggest optimizations

RULES AND GUIDELINES:
1. Always verify delegated access before performing calendar operations
2. When auto-accepting/declining, explain your reasoning
3. For conflicts, suggest multiple resolution options
4. Maintain user preferences for working hours and meeting types
5. Be proactive in detecting potential issues
6. Use human-in-the-loop approval for important decisions

SECURITY:
- Only access the calendar of your explicitly delegated user
- Never share sensitive calendar information
- Always respect user privacy and confidentiality

Remember: You are a trusted assistant managing someone's time, act responsibly."""

    def __init__(self):
        """Initialize the Admin Agent"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load configuration
        self.admin_agent_email = os.getenv("ADMIN_AGENT_EMAIL")
        self.delegated_user_email = os.getenv("DELEGATED_USER_EMAIL")
        
        if not self.admin_agent_email:
            raise ValueError("ADMIN_AGENT_EMAIL environment variable is required")
        if not self.delegated_user_email:
            raise ValueError("DELEGATED_USER_EMAIL environment variable is required")
        
        # Auto-accept rules configuration
        self.auto_accept_domains = os.getenv("AUTO_ACCEPT_FROM_DOMAINS", "").split(",")
        self.auto_accept_max_duration = int(os.getenv("AUTO_ACCEPT_MAX_DURATION_HOURS", "2"))
        self.auto_decline_outside_hours = os.getenv("AUTO_DECLINE_OUTSIDE_HOURS", "true").lower() == "true"
        self.working_hours_start = os.getenv("WORKING_HOURS_START", "09:00")
        self.working_hours_end = os.getenv("WORKING_HOURS_END", "17:00")
        
        self.logger.info(f"Admin Agent initialized for {self.admin_agent_email}")
        self.logger.info(f"Managing calendar for delegated user: {self.delegated_user_email}")
        
        # Enable observability
        self._enable_instrumentation()
        
        # Create Azure OpenAI client
        self._create_chat_client()
        
        # Create the agent
        self._create_agent()
        
        # Initialize MCP services
        self._initialize_mcp_services()
        
        # Track initialization
        self.mcp_servers_initialized = False

    # =========================================================================
    # INITIALIZATION METHODS
    # =========================================================================

    def _enable_instrumentation(self):
        """Enable Agent Framework instrumentation for observability"""
        try:
            if os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true":
                AgentFrameworkInstrumentor().instrument()
                self.logger.info("✅ Observability instrumentation enabled")
        except Exception as e:
            self.logger.warning(f"⚠️ Instrumentation failed: {e}")

    def _create_chat_client(self):
        """Create Azure OpenAI chat client"""
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        if not deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is required")
        
        self.chat_client = AzureOpenAIChatClient(
            endpoint=endpoint,
            credential=AzureCliCredential(),
            deployment_name=deployment,
            api_version=api_version,
        )
        self.logger.info("✅ Azure OpenAI client created")

    def _create_agent(self):
        """Create the AgentFramework ChatAgent"""
        try:
            self.agent = ChatAgent(
                chat_client=self.chat_client,
                instructions=self.AGENT_PROMPT,
                tools=[],
            )
            self.logger.info("✅ ChatAgent created")
        except Exception as e:
            self.logger.error(f"Failed to create agent: {e}")
            raise

    def _initialize_mcp_services(self):
        """Initialize MCP tool registration service"""
        try:
            self.mcp_tool_service = McpToolRegistrationService()
            self.logger.info("✅ MCP tool service initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ MCP tool service initialization failed: {e}")
            self.mcp_tool_service = None

    # =========================================================================
    # MCP SERVER SETUP
    # =========================================================================

    async def setup_mcp_servers(
        self, 
        auth: Authorization, 
        auth_handler_name: str, 
        context: TurnContext
    ):
        """
        Set up Agent 365 MCP servers for calendar management.
        
        MCP Servers to be configured:
        - Outlook Calendar: Primary server for calendar operations
        - Outlook Mail: For email context in meeting prep
        - Teams: For Teams meeting integration
        - SharePoint/OneDrive: For meeting document attachments
        - User Profile: For attendee information
        
        Note: MCP servers are automatically registered by Agent 365 platform
        when the agent is deployed. This method is a placeholder for local testing.
        """
        if self.mcp_servers_initialized:
            return
        
        try:
            self.logger.info("MCP servers will be available when deployed to Agent 365 platform")
            self.logger.info("For local testing, MCP tools are simulated")
            
            # In production, MCP tools are automatically registered by the platform
            # For local testing, the agent will work without real MCP connections
            
            self.mcp_servers_initialized = True
            self.logger.info("✅ MCP setup complete")
            self.logger.info("   Note: Real MCP servers (Outlook Calendar, Mail, Teams, etc.)")
            self.logger.info("   will be available when deployed to Agent 365 platform")
            
        except Exception as e:
            self.logger.error(f"Failed to setup MCP servers: {e}", exc_info=True)
            # Don't raise - allow agent to continue for local testing
            self.mcp_servers_initialized = True

    # =========================================================================
    # CALENDAR TOOLS (via MCP - implemented by Agent 365 platform)
    # =========================================================================
    # These tools will be automatically registered via MCP servers
    # The implementations below are placeholders showing the expected interface

    async def verify_delegated_access(self) -> Dict[str, Any]:
        """
        Verify that the agent has delegated calendar access to the user.
        
        Returns:
            Dict with access status and permissions
        """
        # This will be implemented via Outlook Calendar MCP server
        # The MCP server provides tools like:
        # - listCalendarEvents
        # - getCalendarPermissions
        pass

    async def list_calendar_events(
        self,
        start_datetime: str,
        end_datetime: str
    ) -> List[Dict[str, Any]]:
        """
        List calendar events for the delegated user in a time range.
        
        Args:
            start_datetime: ISO format start time
            end_datetime: ISO format end time
            
        Returns:
            List of calendar events
        """
        # Implemented via Outlook Calendar MCP - listCalendarEvents tool
        pass

    async def create_calendar_event(
        self,
        subject: str,
        start_datetime: str,
        end_datetime: str,
        attendees: List[str],
        body: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new calendar event for the delegated user.
        
        Args:
            subject: Meeting subject
            start_datetime: ISO format start time
            end_datetime: ISO format end time
            attendees: List of attendee email addresses
            body: Optional meeting body/description
            location: Optional meeting location
            
        Returns:
            Created event details
        """
        # Implemented via Outlook Calendar MCP - createCalendarEvent tool
        pass

    async def accept_meeting(self, event_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Accept a meeting invitation on behalf of the delegated user.
        
        Args:
            event_id: ID of the calendar event
            comment: Optional comment to include in acceptance
            
        Returns:
            Response status
        """
        # Implemented via Outlook Calendar MCP - acceptMeeting tool
        pass

    async def decline_meeting(self, event_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Decline a meeting invitation on behalf of the delegated user.
        
        Args:
            event_id: ID of the calendar event
            comment: Optional comment to include in decline
            
        Returns:
            Response status
        """
        # Implemented via Outlook Calendar MCP - declineMeeting tool
        pass

    async def find_meeting_times(
        self,
        attendees: List[str],
        duration_minutes: int,
        time_constraint_start: Optional[str] = None,
        time_constraint_end: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find available meeting times for attendees.
        
        Args:
            attendees: List of attendee email addresses
            duration_minutes: Meeting duration in minutes
            time_constraint_start: Optional earliest start time
            time_constraint_end: Optional latest end time
            
        Returns:
            List of suggested meeting time slots
        """
        # Implemented via Outlook Calendar MCP - findMeetingTimes tool
        pass

    # =========================================================================
    # MESSAGE HANDLING
    # =========================================================================

    async def handle_message(
        self,
        message: str,
        auth: Authorization,
        auth_handler_name: str,
        context: TurnContext
    ) -> str:
        """
        Handle incoming message and generate response.
        
        Args:
            message: User message
            auth: Authorization context
            auth_handler_name: Name of auth handler
            context: Turn context
            
        Returns:
            Agent response
        """
        try:
            # Setup MCP servers if not already done
            await self.setup_mcp_servers(auth, auth_handler_name, context)
            
            # Add context about delegated user
            contextual_message = f"""User message: {message}

Context:
- You are managing the calendar for: {self.delegated_user_email}
- Your identity: {self.admin_agent_email}
- Working hours: {self.working_hours_start} - {self.working_hours_end}
- Auto-accept domains: {', '.join(self.auto_accept_domains) if self.auto_accept_domains else 'None configured'}"""
            
            # Process message with agent
            response = await self.agent.run(contextual_message)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please try again."

    # =========================================================================
    # DEVUI INTEGRATION
    # =========================================================================

    async def serve_devui(self, port: int = 8093):
        """
        Start DevUI server for workflow visualization.
        
        Args:
            port: Port to run DevUI on (default: 8093)
        """
        try:
            from agent_framework.devui import serve
            
            self.logger.info(f"Starting DevUI server on http://localhost:{port}")
            await serve(self.agent, port=port)
            
        except ImportError:
            self.logger.warning("DevUI not available - install agent-framework[devui]")
        except Exception as e:
            self.logger.error(f"Failed to start DevUI: {e}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for testing the Admin Agent"""
    logger.info("=" * 80)
    logger.info("Admin Agent - Calendar Management Assistant")
    logger.info("=" * 80)
    
    try:
        # Create admin agent
        admin_agent = AdminAgent()
        
        logger.info("\n✅ Admin Agent initialized successfully!")
        logger.info(f"   Agent: {admin_agent.admin_agent_email}")
        logger.info(f"   Managing: {admin_agent.delegated_user_email}")
        logger.info(f"   Working hours: {admin_agent.working_hours_start} - {admin_agent.working_hours_end}")
        
        # Start DevUI if enabled
        if os.getenv("ENABLE_DEVUI", "true").lower() == "true":
            logger.info("\n🚀 Starting DevUI server...")
            logger.info("   Open http://localhost:8093 to visualize workflows")
            await admin_agent.serve_devui()
        else:
            logger.info("\n💡 DevUI disabled. Set ENABLE_DEVUI=true to enable.")
            
    except Exception as e:
        logger.error(f"Failed to start Admin Agent: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
