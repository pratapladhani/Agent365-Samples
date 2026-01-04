# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Client for communicating with Copilot Studio agents via their connection URL
"""

import logging
import asyncio
from typing import Optional, Dict, Any
import aiohttp
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class CopilotStudioClient:
    """Client for Copilot Studio agent communication"""
    
    def __init__(
        self,
        connection_url: str,
        client_id: str,
        client_secret: str,
        tenant_id: str
    ):
        self.connection_url = connection_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        
        # Create MSAL client for authentication
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.msal_client = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority
        )
        
        # Parse connection URL to extract endpoint and conversation ID
        self._parse_connection_url()
        
        logger.info(f"✅ Copilot Studio client initialized")
        logger.info(f"   Endpoint: {self.endpoint}")
    
    def _parse_connection_url(self):
        """Parse Copilot Studio connection string"""
        # Connection URL format from Copilot Studio looks like:
        # https://powerva.microsoft.com/conversations/{botId}?conversationId={convId}
        # Or direct endpoint format
        
        self.endpoint = self.connection_url
        # You may need to adjust parsing based on actual format
        logger.info(f"   Using connection URL: {self.connection_url[:50]}...")
    
    async def _get_access_token(self) -> str:
        """Get access token for Copilot Studio API"""
        try:
            # Copilot Studio uses Power Platform API scope
            scopes = ["8578e004-a5c6-46e7-913e-12f58912df43/.default"]
            
            result = self.msal_client.acquire_token_for_client(scopes=scopes)
            
            if "access_token" in result:
                logger.debug("✅ Acquired access token for Copilot Studio")
                return result["access_token"]
            else:
                error = result.get("error_description", "Unknown error")
                raise Exception(f"Failed to acquire token: {error}")
                
        except Exception as e:
            logger.error(f"❌ Error getting access token: {str(e)}")
            raise
    
    async def send_message(
        self,
        message: str,
        conversation_id: str,
        user_id: str
    ) -> str:
        """Send message to Copilot Studio agent and get response"""
        try:
            token = await self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "type": "message",
                "text": message,
                "from": {
                    "id": user_id
                },
                "conversation": {
                    "id": conversation_id
                }
            }
            
            logger.info(f"📤 Sending to Copilot Studio: {message[:100]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract response text from Copilot Studio response
                        response_text = self._extract_response(data)
                        logger.info(f"📬 Copilot Studio response: {response_text[:100]}...")
                        return response_text
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Copilot Studio error ({response.status}): {error_text}")
                        return f"Sorry, I couldn't process that request (Error: {response.status})"
                        
        except asyncio.TimeoutError:
            logger.error("⏱️  Timeout connecting to Copilot Studio")
            return "Sorry, the request timed out. Please try again."
        except Exception as e:
            logger.error(f"❌ Error sending message to Copilot Studio: {str(e)}", exc_info=True)
            return "Sorry, I encountered an error processing your request."
    
    def _extract_response(self, data: Dict[str, Any]) -> str:
        """Extract response text from Copilot Studio response"""
        try:
            # Copilot Studio response format may vary
            # Adjust based on actual response structure
            
            if isinstance(data, dict):
                # Try common response fields
                if "text" in data:
                    return data["text"]
                elif "activities" in data and len(data["activities"]) > 0:
                    return data["activities"][0].get("text", "No response text")
                elif "message" in data:
                    return data["message"]
            
            # Fallback
            return str(data)
            
        except Exception as e:
            logger.error(f"Error extracting response: {str(e)}")
            return "Received response but couldn't parse it."
