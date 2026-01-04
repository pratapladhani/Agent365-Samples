# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Quick test script to run Admin Agent with DevUI for local testing
"""

import asyncio
import os
from dotenv import load_dotenv
from agent import AdminAgent

async def setup_agent_with_tools():
    """Set up agent with MCP tools for local testing"""
    # Load environment
    load_dotenv()
    
    # Create agent
    print("🤖 Initializing Admin Agent...")
    admin_agent = AdminAgent()
    
    # Import MCP service
    from microsoft_agents_a365.tooling.extensions.agentframework.services.mcp_tool_registration_service import (
        McpToolRegistrationService,
    )
    
    mcp_service = McpToolRegistrationService()
    
    # Get bearer token from environment for local testing
    bearer_token = os.getenv("BEARER_TOKEN")
    
    if not bearer_token:
        print("❌ BEARER_TOKEN not found in environment")
        print("   Run: a365 develop get-token")
        return admin_agent.agent
    
    print("🔧 Registering MCP tools with bearer token...")
    print(f"   Token expires: ~2026-01-03 20:09:51 (check .env for exact time)")
    
    # Register tools with bearer token (no TurnContext needed)
    agent_with_tools = await mcp_service.add_tool_servers_to_agent(
        chat_client=admin_agent.chat_client,
        agent_instructions=admin_agent.AGENT_PROMPT,
        initial_tools=[],
        auth=None,
        auth_handler_name=None,
        auth_token=bearer_token,  # Pass bearer token directly
        turn_context=None,  # Not needed for bearer token auth
    )
    
    print("✅ MCP tools registered")
    print(f"   Agent type: {type(agent_with_tools)}")
    if hasattr(agent_with_tools, 'tools'):
        print(f"   Number of tools: {len(agent_with_tools.tools) if agent_with_tools.tools else 0}")
    
    return agent_with_tools

def main():
    # Set up agent with tools
    agent_with_tools = asyncio.run(setup_agent_with_tools())
    
    # Start DevUI with the tool-enabled agent
    print("🌐 Starting DevUI on http://localhost:8093")
    print("📝 Open your browser to test the agent locally")
    print("Press Ctrl+C to stop the server")
    
    from agent_framework_devui import serve
    
    # serve() handles its own event loop
    serve(entities=[agent_with_tools], port=8093, host="127.0.0.1", auto_open=True)

if __name__ == "__main__":
    main()
