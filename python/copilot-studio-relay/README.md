# Copyright (c) Microsoft Corporation.

# Licensed under the MIT License.

# Copilot Studio Relay Service

This service acts as a relay between Agent 365 instances and Copilot Studio agents, allowing you to leverage Copilot Studio's MCP tools and orchestration capabilities.

## Architecture

```
Microsoft Teams → Agent 365 Bot → This Relay Service → Copilot Studio Agent → MCP Tools
```

## Prerequisites

- Python 3.11+
- Agent Blueprint created and configured
- Azure Bot Service configured
- Copilot Studio agent created and shared with agent user
- Agent User created with appropriate licenses

## Setup

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Agent Blueprint Configuration
AGENT_BLUEPRINT_CLIENT_ID=<your-agent-blueprint-app-id>
AGENT_BLUEPRINT_CLIENT_SECRET=<your-client-secret>
TENANT_ID=<your-tenant-id>

# Copilot Studio Connection
COPILOT_STUDIO_CONNECTION_URL=<connection-string-from-copilot-studio>

# Server Configuration
PORT=3978
```

### 3. Run the Service

```bash
python app.py
```

## Deployment to Azure

```bash
a365 deploy app
```

## Testing

### Local Testing with Dev Tunnel

1. Install dev tunnels:

```bash
devtunnel user login
```

2. Host tunnel:

```bash
devtunnel host -p 3978 --allow-anonymous
```

3. Update Azure Bot messaging endpoint with tunnel URL:
   - Go to Azure Portal → Your Bot Resource → Configuration
   - Update Messaging endpoint: `https://<tunnel-url>/api/messages`

### Test in Teams

1. Open Microsoft Teams
2. Start a chat with your agent user
3. Send a message to test the relay

## Troubleshooting

See main [README](../../README.md) for common issues and solutions.
