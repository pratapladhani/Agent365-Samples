# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Admin Agent - Local Test Script

This script provides an interactive command-line interface for testing the Admin Agent
locally without requiring full Agent 365 platform deployment.

## Features

- Interactive chat interface with the agent
- Mock authentication and context objects for local testing
- Azure OpenAI integration for intelligent responses
- Graceful error handling and logging

## Usage

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run the test script
python test_agent.py
```

## Example Interactions

- "What can you help me with?"
- "Tell me about calendar management capabilities"
- "How do you handle meeting conflicts?"
- "Explain your auto-accept rules"

## Note

This is for local testing only. MCP server calls will be simulated.
For full functionality with Microsoft 365 integration, deploy to Agent 365 platform.

## Requirements

- Configured .env file with Azure OpenAI credentials
- Virtual environment with all dependencies installed
- Python 3.11 or higher
"""

import asyncio
import logging
from agent import AdminAgent
from unittest.mock import Mock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_agent():
    """Test the agent with sample messages"""
    
    # Initialize agent
    agent = AdminAgent()
    
    # Create mock objects for required parameters
    mock_auth = Mock()
    mock_auth.access_token = "mock_token"
    mock_context = Mock()
    mock_context.activity = Mock()
    mock_context.activity.from_property = Mock()
    mock_context.activity.from_property.id = "test-user"
    
    print("\n" + "="*80)
    print("Admin Agent Test - Interactive Mode")
    print("="*80)
    print("Type your messages below (or 'quit' to exit):\n")
    print("Note: This is a local test without real Microsoft 365 integration.")
    print("MCP server calls will be simulated.\n")
    
    while True:
        # Get user input
        try:
            user_message = input("\nYou: ").strip()
            
            if not user_message:
                continue
                
            if user_message.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye!")
                break
            
            # Send message to agent with mock auth parameters
            print("\nAgent: ", end="", flush=True)
            response = await agent.handle_message(
                user_message, 
                mock_auth,
                "mock_handler",
                mock_context
            )
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(test_agent())
