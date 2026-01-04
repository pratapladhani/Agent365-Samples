# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Admin Agent - Calendar Management Assistant

A minimal agent implementation using Azure OpenAI and Agent 365 platform.
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
    """Admin Agent for calendar management."""

    AGENT_PROMPT = """You are Atlas Agent, an expert calendar management assistant for busy executives and administrators.

Your capabilities include:
- Managing calendar events (create, update, delete, list)
- Finding optimal meeting times across multiple calendars
- Accepting and declining meeting invitations
- Resolving calendar conflicts
- Searching for user information and availability
- Sending email notifications about meetings

Always be professional, proactive, and help users organize their time efficiently. When scheduling meetings, consider time zones, working hours, and existing commitments."""

    def __init__(self):
        """Initialize the Admin Agent"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Admin Agent initialized")
        
        # Initialize MCP tool service
        self.mcp_tool_service = McpToolRegistrationService()
        self.tools_registered = False
        
        # Enable observability
        self._enable_instrumentation()
        
        # Create Azure OpenAI client
        self._create_chat_client()
        
        # Create the agent (tools will be added later when handling messages)
        self._create_agent()

    # =========================================================================
    # INITIALIZATION METHODS
    # =========================================================================

    def _enable_instrumentation(self):
        """Enable Agent Framework instrumentation for observability"""
        try:
            if os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true":
                # Import observability configuration
                from microsoft_agents_a365.observability.core import config
                
                # Configure observability BEFORE instrumenting
                config.configure(
                    service_name="atlas-admin-agent",
                    service_namespace="ai.agents.admin",
                )
                
                # Now enable instrumentation
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
        Process incoming message with the agent.
        
        Args:
            message: User's message
            auth: Authorization object
            auth_handler_name: Name of auth handler
            context: Turn context
            
        Returns:
            Agent response
        """
        try:
            # Register MCP tools if not already done
            if not self.tools_registered:
                self.logger.info("🔧 Registering MCP tools...")
                await self._setup_mcp_tools(auth, auth_handler_name, context)
                self.logger.info(f"🔧 Tools registered: {self.tools_registered}, Agent: {self.agent is not None}")
            
            # Process message with agent
            if self.agent:
                self.logger.info(f"🤖 Running agent with message: {message[:50]}...")
                result = await self.agent.run(message)
                self.logger.info(f"✅ Agent run completed, result type: {type(result)}")
                response = self._extract_result(result) or "I couldn't process your request at this time."
                self.logger.info(f"📤 Sending response: {response[:100]}...")
                return response
            else:
                self.logger.error("❌ Agent is None after tool setup!")
                return "Agent is not properly initialized. Please try again."
            
        except Exception as e:
            self.logger.error(f"❌ Error handling message: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please try again."

    async def _setup_mcp_tools(self, auth: Authorization, auth_handler_name: str, context: TurnContext):
        """
        Set up MCP tool servers for the agent.
        
        Args:
            auth: Authorization object
            auth_handler_name: Name of auth handler
            context: Turn context
        """
        try:
            self.logger.info("Setting up MCP tool servers...")
            
            # Get agent instance ID from context
            agentic_app_id = getattr(context.activity, 'from_property', None)
            if agentic_app_id and hasattr(agentic_app_id, 'aad_object_id'):
                agentic_app_id = agentic_app_id.aad_object_id
            else:
                # Fallback to a default or extract from elsewhere
                agentic_app_id = None
            
            # Register tools with the agent
            use_agentic_auth = os.getenv("USE_AGENTIC_AUTH", "true").lower() == "true"
            
            if use_agentic_auth:
                self.agent = await self.mcp_tool_service.add_tool_servers_to_agent(
                    chat_client=self.chat_client,
                    agent_instructions=self.AGENT_PROMPT,
                    initial_tools=[],
                    auth=auth,
                    auth_handler_name=auth_handler_name,
                    turn_context=context,
                )
            else:
                # For bearer token auth (development only)
                auth_token = os.getenv("BEARER_TOKEN")
                self.agent = await self.mcp_tool_service.add_tool_servers_to_agent(
                    chat_client=self.chat_client,
                    agent_instructions=self.AGENT_PROMPT,
                    initial_tools=[],
                    auth=auth,
                    auth_handler_name=auth_handler_name,
                    auth_token=auth_token,
                    turn_context=context,
                )
            
            self.tools_registered = True
            self.logger.info("✅ MCP tool servers registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup MCP tools: {e}", exc_info=True)
            # Continue without tools rather than failing completely
            self.tools_registered = False

    # =========================================================================
    # CONTEXT HELPERS
    # =========================================================================

    def _get_user_email(self, context: TurnContext) -> str:
        """Extract user email from conversation context"""
        try:
            # Try to get from AAD claims first
            if hasattr(context.activity, 'from_property') and context.activity.from_property:
                if hasattr(context.activity.from_property, 'aad_object_id'):
                    # In production, you'd look up email from AAD object ID
                    return context.activity.from_property.id or "user@example.com"
                return context.activity.from_property.id or "user@example.com"
            return "user@example.com"
        except Exception as e:
            self.logger.warning(f"Could not extract user email: {e}")
            return "user@example.com"

    def _get_user_name(self, context: TurnContext) -> str:
        """Extract user name from conversation context"""
        try:
            if hasattr(context.activity, 'from_property') and context.activity.from_property:
                return context.activity.from_property.name or "User"
            return "User"
        except Exception as e:
            self.logger.warning(f"Could not extract user name: {e}")
            return "User"

    def _extract_result(self, result) -> str:
        """Extract text content from agent result"""
        if not result:
            return ""
        if hasattr(result, "contents"):
            return str(result.contents)
        elif hasattr(result, "text"):
            return str(result.text)
        elif hasattr(result, "content"):
            return str(result.content)
        else:
            return str(result)

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
            from agent_framework.devui import serve  # type: ignore
            
            self.logger.info(f"Starting DevUI server on http://localhost:{port}")
            await serve(self.agent, port=port)
            
        except ImportError:
            self.logger.warning("DevUI not available - install agent-framework[devui]")
        except Exception as e:
            self.logger.error(f"Failed to start DevUI: {e}")


# =============================================================================
# NOTE: For local testing, use test_agent.py
# For production deployment, use host_server.py
# =============================================================================
