# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Copilot Studio Relay Service
Relays messages between Agent 365 Bot Framework and Copilot Studio agents
"""

import os
import logging
import asyncio
from typing import Any, Dict
from aiohttp import web
from dotenv import load_dotenv

from microsoft_agents import Activity, TurnContext
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.authentication import AuthenticationConfiguration, SimpleCredentialProvider

from copilot_studio_client import CopilotStudioClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CopilotStudioRelay:
    """Relay service that forwards messages to Copilot Studio"""
    
    def __init__(self):
        self.copilot_client = CopilotStudioClient(
            connection_url=os.getenv("COPILOT_STUDIO_CONNECTION_URL"),
            client_id=os.getenv("AGENT_BLUEPRINT_CLIENT_ID"),
            client_secret=os.getenv("AGENT_BLUEPRINT_CLIENT_SECRET"),
            tenant_id=os.getenv("TENANT_ID")
        )
        logger.info("✅ Copilot Studio Relay initialized")
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming message from Bot Framework"""
        try:
            user_message = turn_context.activity.text
            logger.info(f"📨 Received message: {user_message}")
            
            # Send typing indicator
            await turn_context.send_activity(Activity(type="typing"))
            
            # Forward message to Copilot Studio
            logger.info("🔄 Forwarding to Copilot Studio...")
            response = await self.copilot_client.send_message(
                message=user_message,
                conversation_id=turn_context.activity.conversation.id,
                user_id=turn_context.activity.from_property.id
            )
            
            # Send response back to user
            logger.info(f"✅ Got response from Copilot Studio: {response[:100]}...")
            await turn_context.send_activity(response)
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {str(e)}", exc_info=True)
            await turn_context.send_activity(
                "Sorry, I encountered an error processing your request."
            )
    
    async def on_turn(self, turn_context: TurnContext):
        """Handle all turn activities"""
        if turn_context.activity.type == "message":
            await self.on_message_activity(turn_context)
        else:
            logger.info(f"ℹ️  Received activity type: {turn_context.activity.type}")


async def create_app() -> web.Application:
    """Create and configure the aiohttp application"""
    
    # Create credential provider
    credential_provider = SimpleCredentialProvider(
        app_id=os.getenv("AGENT_BLUEPRINT_CLIENT_ID"),
        password=os.getenv("AGENT_BLUEPRINT_CLIENT_SECRET")
    )
    
    # Create authentication configuration
    auth_config = AuthenticationConfiguration()
    
    # Create Bot Framework adapter
    adapter = CloudAdapter(auth_config, credential_provider)
    
    # Create relay service
    relay = CopilotStudioRelay()
    
    # Define routes
    async def messages_handler(request: web.Request):
        """Handle Bot Framework messages endpoint"""
        return await adapter.process(request, relay.on_turn)
    
    async def health_handler(request: web.Request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy"})
    
    # Create app
    app = web.Application()
    app.router.add_post("/api/messages", messages_handler)
    app.router.add_get("/health", health_handler)
    
    logger.info("=" * 80)
    logger.info("🔄 Copilot Studio Relay Service")
    logger.info("=" * 80)
    logger.info(f"📚 Endpoint: http://localhost:{os.getenv('PORT', 3978)}/api/messages")
    logger.info(f"❤️  Health: http://localhost:{os.getenv('PORT', 3978)}/health")
    logger.info("=" * 80)
    
    return app


def main():
    """Main entry point"""
    port = int(os.getenv("PORT", 3978))
    
    try:
        app = asyncio.run(create_app())
        web.run_app(app, host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
