# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Admin Agent Host Server
Minimal host for running Admin Agent with Agent 365 platform
"""

import logging
import os
from os import environ

from aiohttp.web import Application, Request, Response, json_response, run_app
from dotenv import load_dotenv

from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.aiohttp import (
    CloudAdapter,
    start_agent_process,
)
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    MemoryStorage,
    TurnContext,
    TurnState,
)

# Import the admin agent
from agent import AdminAgent

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
agents_sdk_config = load_configuration_from_env(environ)


class AdminAgentHost:
    """Host server for Admin Agent"""

    def __init__(self):
        self.auth_handler_name = "AGENTIC"
        self.admin_agent = None
        
        # Setup Agent 365 components
        self.storage = MemoryStorage()
        self.connection_manager = MsalConnectionManager(**agents_sdk_config)
        self.adapter = CloudAdapter(connection_manager=self.connection_manager)
        self.authorization = Authorization(
            self.storage, self.connection_manager, **agents_sdk_config
        )
        self.agent_app = AgentApplication[TurnState](
            storage=self.storage,
            adapter=self.adapter,
            authorization=self.authorization,
            **agents_sdk_config,
        )
        
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup message handlers"""
        handler = [self.auth_handler_name]

        @self.agent_app.activity("message", auth_handlers=handler)
        async def on_message(context: TurnContext, _: TurnState):
            try:
                if not self.admin_agent:
                    await context.send_activity("❌ Agent not initialized")
                    return

                user_message = context.activity.text or ""
                if not user_message.strip():
                    return

                logger.info(f"📨 Message received: {user_message}")
                
                # Process message with admin agent
                response = await self.admin_agent.handle_message(
                    user_message,
                    self.agent_app.auth,
                    self.auth_handler_name,
                    context
                )
                
                await context.send_activity(response)

            except Exception as e:
                logger.error(f"❌ Error processing message: {e}", exc_info=True)
                await context.send_activity(f"Sorry, I encountered an error: {str(e)}")

        @self.agent_app.conversation_update("membersAdded", auth_handlers=handler)
        async def on_members_added(context: TurnContext, _: TurnState):
            await context.send_activity(
                "👋 Hi! I'm Agent Atlas, your calendar management assistant. "
                "I can help you manage calendars, auto-accept meetings, find meeting times, "
                "and resolve scheduling conflicts."
            )

    async def initialize_agent(self):
        """Initialize the admin agent"""
        if self.admin_agent is None:
            logger.info("🤖 Initializing Admin Agent...")
            self.admin_agent = AdminAgent()
            logger.info("✅ Admin Agent initialized successfully")

    def start_server(self):
        """Start the host server"""
        async def entry_point(req: Request) -> Response:
            return await start_agent_process(
                req, req.app["agent_app"], req.app["adapter"]
            )

        async def health(_req: Request) -> Response:
            return json_response({
                "status": "ok",
                "agent": "Admin Agent",
                "initialized": self.admin_agent is not None
            })

        app = Application()
        
        # Register routes
        app.router.add_post("/api/messages", entry_point)
        app.router.add_get("/api/messages", lambda _: Response(status=200))
        app.router.add_get("/api/health", health)
        app.router.add_get("/health", health)
        
        # Store agent app and adapter
        app["agent_app"] = self.agent_app
        app["adapter"] = self.agent_app.adapter
        
        # Startup/shutdown hooks
        app.on_startup.append(lambda _: self.initialize_agent())
        
        port = int(environ.get("PORT", 8000))
        
        logger.info("=" * 80)
        logger.info("🏢 Admin Agent - Calendar Management Assistant")
        logger.info("=" * 80)
        logger.info(f"🚀 Server starting on port {port}")
        logger.info(f"📚 Endpoint: http://localhost:{port}/api/messages")
        logger.info(f"❤️  Health: http://localhost:{port}/health")
        logger.info("=" * 80)
        
        run_app(app, host="0.0.0.0", port=port)


def main():
    """Main entry point"""
    host = AdminAgentHost()
    host.start_server()


if __name__ == "__main__":
    main()
