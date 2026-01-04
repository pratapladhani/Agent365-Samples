# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Simple test to verify agent.run() works locally
"""

import asyncio
from dotenv import load_dotenv
from agent import AdminAgent

async def test_agent():
    # Load environment
    load_dotenv()
    
    # Create agent
    print("🤖 Initializing Admin Agent...")
    agent = AdminAgent()
    print("✅ Agent initialized\n")
    
    # Test message
    test_message = "Hi there, can you help me?"
    print(f"📨 Testing with message: '{test_message}'")
    print(f"🤖 Calling agent.run() directly...")
    
    try:
        # Test if agent.run() hangs
        result = await asyncio.wait_for(agent.agent.run(test_message), timeout=30.0)
        print(f"✅ agent.run() completed!")
        print(f"📤 Result type: {type(result)}")
        print(f"📤 Result: {result}")
        
        # Test extract_result
        extracted = agent._extract_result(result)
        print(f"\n✅ Extracted response: {extracted}")
        
    except asyncio.TimeoutError:
        print("❌ TIMEOUT: agent.run() hung for 30+ seconds!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
