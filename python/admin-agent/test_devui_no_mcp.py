# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Test DevUI WITHOUT MCP tools to verify basic functionality
"""

import os
from dotenv import load_dotenv
from agent import AdminAgent

def main():
    # Load environment
    load_dotenv()
    
    # Create agent WITHOUT MCP tools
    print("🤖 Initializing Admin Agent (WITHOUT MCP tools)...")
    admin_agent = AdminAgent()
    
    # Use the base agent (before MCP tools are registered)
    agent = admin_agent.agent
    
    print(f"✅ Agent created: {type(agent)}")
    
    # Start DevUI
    print("🌐 Starting DevUI on http://localhost:8093")
    print("📝 Open your browser to test the agent locally")
    print("⚠️  NOTE: MCP tools are NOT registered (testing base agent only)")
    print("Press Ctrl+C to stop the server")
    
    from agent_framework_devui import serve
    
    # serve() handles its own event loop
    serve(entities=[agent], port=8093, host="127.0.0.1", auto_open=True)

if __name__ == "__main__":
    main()
