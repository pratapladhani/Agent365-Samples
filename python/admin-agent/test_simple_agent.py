# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Test agent WITHOUT MCP tools to isolate the issue
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

async def test_simple_agent():
    # Load environment
    load_dotenv()
    
    # Create Azure OpenAI client
    print("🤖 Creating Azure OpenAI client...")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    
    chat_client = AzureOpenAIChatClient(
        endpoint=endpoint,
        credential=AzureCliCredential(),
        deployment_name=deployment,
        api_version=api_version,
    )
    
    # Create agent WITHOUT any tools
    print("🤖 Creating agent without tools...")
    agent = ChatAgent(
        chat_client=chat_client,
        instructions="You are a helpful assistant.",
        tools=[],  # No tools!
    )
    
    # Test simple message
    print("📤 Sending message: 'Hi there!'")
    result = await agent.run("Hi there!")
    
    print(f"✅ Got result: {result}")
    print(f"   Type: {type(result)}")
    
    # Extract response
    if hasattr(result, "contents"):
        response = str(result.contents)
    elif hasattr(result, "text"):
        response = str(result.text)
    else:
        response = str(result)
    
    print(f"📬 Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_simple_agent())
