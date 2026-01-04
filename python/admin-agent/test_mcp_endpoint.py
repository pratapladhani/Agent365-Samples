# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Test MCP endpoint directly to verify bearer token works
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

async def test_mcp_endpoint():
    load_dotenv()
    
    bearer_token = os.getenv("BEARER_TOKEN")
    if not bearer_token:
        print("❌ BEARER_TOKEN not set in .env")
        return
    
    print(f"🔑 Using bearer token: {bearer_token[:20]}...")
    
    # Test CalendarTools MCP server
    url = "https://agent365.svc.cloud.microsoft/agents/servers/mcp_CalendarTools"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📡 Testing MCP endpoint: {url}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Try to list tools (standard MCP endpoint)
            response = await client.post(
                f"{url}/tools/list",
                headers=headers,
                json={}
            )
            
            print(f"✅ Response status: {response.status_code}")
            print(f"📦 Response body: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ Bearer token is valid and MCP server is accessible!")
            elif response.status_code == 401:
                print("❌ Bearer token is INVALID or EXPIRED")
            else:
                print(f"⚠️ Unexpected status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error calling MCP endpoint: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_endpoint())
