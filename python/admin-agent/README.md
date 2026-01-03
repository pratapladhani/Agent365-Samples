# Copyright (c) Microsoft Corporation.

# Licensed under the MIT License.

# Admin Agent - Calendar Management Assistant

A demo agent showcasing **Agent 365 platform capabilities** and **Agent Framework features** for intelligent calendar management using delegated access patterns.

## Demonstrates

This sample demonstrates:

### Agent 365 Platform Features

- **Multi-channel interactions**: Teams @mentions, email, documents
- **Premium MCP Server Integration**: Outlook Calendar, Mail, Teams, SharePoint/OneDrive, User Profile
- **Microsoft Entra ID Authentication**: Agentic authentication with delegated permissions
- **Agentic Behaviors**: Proactive monitoring, autonomous decision-making, human-in-the-loop approvals

### Agent Framework Features

- **Workflows**: Multi-step calendar management workflows with WorkflowBuilder
- **Tools**: @ai_function decorators for calendar operations
- **DevUI**: Visual workflow execution at http://localhost:8093
- **Observability**: Custom spans and telemetry for calendar operations
- **Multi-Agent Patterns**: Sub-agents for specialized tasks (placeholder)

## Architecture

The Admin Agent operates with **delegated calendar access**:

- Agent has its own identity (e.g., `adminagent@contoso.com`)
- Agent manages calendar for a delegated user through Microsoft Graph Calendar API
- Uses Outlook Calendar MCP server for all calendar operations
- Requires `Calendars.ReadWrite.Shared` permission

## Prerequisites

- **Python**: 3.11 or higher
- **Azure OpenAI**: API key and endpoint
- **Microsoft 365 Account**: With admin privileges to create app registration
- **Agent 365 Access**: Frontier preview program membership ([Sign up](https://adoption.microsoft.com/copilot/frontier-program/))
- **Azure CLI**: For authentication (`az login`)

## Configuration

### 1. Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations**
2. Create new registration for Admin Agent
3. Note the **Client ID**, **Tenant ID**
4. Create a **Client Secret** under "Certificates & secrets"
5. Add API permissions:
   - **Microsoft Graph** → **Application permissions**:
     - `Calendars.ReadWrite` (or `Calendars.ReadWrite.Shared`)
     - `Mail.Read` (for meeting prep)
     - `Mail.Send` (for notifications)
   - Grant admin consent

### 2. Configure Delegated Access

The delegated user must grant calendar access to the admin agent:

**Option A: Via Outlook** (recommended)

1. Open Outlook → Calendar
2. Right-click calendar → **Properties** → **Permissions**
3. Add admin agent email (`adminagent@contoso.com`)
4. Set permission level: **Editor** or **Delegate**

**Option B: Via PowerShell**

```powershell
Add-MailboxFolderPermission -Identity "user@contoso.com:\Calendar" -User "adminagent@contoso.com" -AccessRights Editor
```

### 3. Environment Setup

1. **Copy environment template:**

   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` file** with your configuration:

   ```bash
   # Azure OpenAI
   AZURE_OPENAI_API_KEY=<<YOUR_API_KEY>>
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   AZURE_OPENAI_API_VERSION=2024-10-21

   # Agent 365 Authentication
   CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<<YOUR_CLIENT_ID>>
   CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=<<YOUR_CLIENT_SECRET>>
   CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<<YOUR_TENANT_ID>>

   # Admin Agent Configuration
   ADMIN_AGENT_EMAIL=adminagent@contoso.com
   DELEGATED_USER_EMAIL=user@contoso.com

   # Auto-accept rules (optional)
   AUTO_ACCEPT_FROM_DOMAINS=contoso.com,microsoft.com
   AUTO_ACCEPT_MAX_DURATION_HOURS=2
   WORKING_HOURS_START=09:00
   WORKING_HOURS_END=17:00
   ```

3. **Create virtual environment** (recommended):

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies:**

   ```bash
   pip install -e .
   ```

   Or with requirements:

   ```bash
   pip install -r requirements.txt  # If you create one from pyproject.toml
   ```

## How to Run This Sample

### Local Testing with DevUI

1. **Start the agent with DevUI:**

   ```bash
   python agent.py
   ```

2. **Open DevUI** in browser:

   ```
   http://localhost:8093
   ```

3. **Test workflows** through DevUI interface:
   - Visualize workflow execution in real-time
   - Inspect executor states
   - Monitor MCP tool calls
   - View observability spans

### Testing with Agent 365 Platform

#### Option 1: Test with Microsoft 365 Agents Playground

1. **Deploy agent** following [Agent 365 deployment guide](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/deployment)

2. **Register agent** in Agents Playground

3. **Test via Teams:**
   - @mention the agent: `@AdminAgent verify my delegated access`
   - Request actions: `@AdminAgent find time with sarah@contoso.com tomorrow`
   - Test auto-accept: Send a meeting invite to delegated user

#### Option 2: Test via WebChat

See [Configure Agent Testing](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/testing?tabs=python) for WebChat setup instructions.

#### Option 3: Test via Microsoft Teams

1. Create app package using [appManifest/](./appManifest/) folder
2. Upload to Teams
3. Interact with agent in Teams chat

## Demo Scenarios

### 1. Verify Delegated Access

```
@AdminAgent verify I have access to manage John's calendar
```

**Expected**: Agent checks and confirms delegated permissions

### 2. Auto-Accept Meeting

Send a meeting invitation to delegated user from a trusted domain.

**Expected**: Agent auto-accepts based on rules and notifies user

### 3. Find Meeting Time

```
@AdminAgent find time with sarah@contoso.com and mike@contoso.com for 1 hour this week
```

**Expected**: Agent suggests 3 optimal time slots and creates meeting after selection

### 4. Detect and Resolve Conflicts

Create two overlapping meetings on delegated user's calendar.

**Expected**: Agent detects conflict, analyzes priority, suggests resolution

### 5. Meeting Preparation

Have a meeting scheduled within next hour.

**Expected**: Agent proactively sends prep brief with context

## Workflows

The agent implements four main workflows (see [workflows/](./workflows/) directory):

### 1. **Delegated Access Verification** ([delegated_access.py](./workflows/delegated_access.py))

- Verifies agent has calendar permissions
- Checks permission levels
- Generates access report

### 2. **Auto-Accept/Decline** ([auto_accept.py](./workflows/auto_accept.py))

- Receives meeting invitations
- Checks calendar availability
- Applies configurable rules
- Requests approval for complex cases
- Sends acceptance/decline via MCP

### 3. **Find Meeting Time** ([find_meeting_time.py](./workflows/find_meeting_time.py))

- Parses natural language requests
- Queries availability via Outlook Calendar MCP
- Ranks optimal time slots
- Creates meeting after user confirmation

### 4. **Conflict Resolution** ([conflict_resolution.py](./workflows/conflict_resolution.py))

- Scans calendar for conflicts
- Analyzes meeting priorities
- Generates resolution strategies
- Requests approval
- Executes approved resolution

## Agent 365 MCP Servers Used

This agent integrates with official Agent 365 MCP servers:

- **Outlook Calendar MCP**: Calendar operations (primary)

  - List events
  - Create/update/delete events
  - Accept/decline meetings
  - Find meeting times
  - Resolve conflicts

- **Outlook Mail MCP**: Email context for meeting prep

  - Read emails
  - Send notifications
  - Semantic search

- **Teams MCP**: Teams integration

  - Create/manage chats
  - Post messages
  - Channel operations

- **SharePoint/OneDrive MCP**: Document management

  - Upload/download files
  - File metadata
  - Search documents

- **User Profile MCP**: User information
  - Get manager/reports
  - Profile details
  - User search

Learn more: [Agent 365 Tooling Servers](https://learn.microsoft.com/en-us/microsoft-agent-365/tooling-servers-overview)

## Observability

The agent includes comprehensive observability:

### Automatic Instrumentation

- Agent Framework automatic instrumentation via `AgentFrameworkInstrumentor()`
- Captures LLM calls, tool executions, workflow steps

### Custom Spans

Custom spans for calendar operations (see [telemetry/observability.py](./telemetry/observability.py)):

```python
@trace_calendar_operation("accept_meeting")
async def accept_meeting(self, event_id: str):
    # Traced automatically with custom attributes
    pass
```

### Viewing Traces

- **Local**: Check console logs and telemetry exports
- **Production**: View in Microsoft Defender Advanced Hunting
- **Agent 365 Portal**: View agent execution traces

## Project Structure

```
admin-agent/
├── agent.py                    # Main AdminAgent class
├── pyproject.toml              # Python dependencies
├── .env.template               # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── DESIGN.md                   # Design specification
├── workflows/                  # Agent Framework workflows
│   ├── __init__.py
│   ├── delegated_access.py     # Access verification workflow
│   ├── auto_accept.py          # Auto-accept/decline workflow
│   ├── find_meeting_time.py    # Find meeting time workflow
│   └── conflict_resolution.py  # Conflict resolution workflow
├── telemetry/                  # Custom observability
│   ├── __init__.py
│   └── observability.py        # Custom span decorators
└── appManifest/                # Teams app manifest (to be created)
    ├── manifest.json
    ├── color.png
    └── outline.png
```

## Troubleshooting

### Issue: "Delegated access verification failed"

**Solution**:

1. Verify delegated user granted calendar permissions
2. Check app registration has `Calendars.ReadWrite.Shared` permission
3. Ensure admin consent was granted
4. Confirm `ADMIN_AGENT_EMAIL` and `DELEGATED_USER_EMAIL` are correct

### Issue: "MCP server connection failed"

**Solution**:

1. Verify `MCP_SERVER_HOST` is set correctly
2. Check Agent 365 platform access (Frontier program)
3. Ensure authentication credentials are valid
4. Check network connectivity to Agent 365 platform

### Issue: "Azure OpenAI API error"

**Solution**:

1. Verify `AZURE_OPENAI_API_KEY` is valid
2. Check endpoint URL format
3. Confirm deployment name exists
4. Verify API version compatibility

### Issue: "DevUI not starting"

**Solution**:

1. Install DevUI dependencies: `pip install agent-framework[devui]`
2. Check port 8093 is not in use
3. Set `ENABLE_DEVUI=true` in `.env`

### Issue: "Auto-accept not working"

**Solution**:

1. Verify `AUTO_ACCEPT_FROM_DOMAINS` is configured
2. Check meeting invite comes from trusted domain
3. Confirm meeting duration is within `AUTO_ACCEPT_MAX_DURATION_HOURS`
4. Verify working hours configuration if `AUTO_DECLINE_OUTSIDE_HOURS=true`

## Security Considerations

- **Never commit** `.env` file with secrets to source control
- Use **Azure Key Vault** for production secrets
- Grant **minimum required permissions** to app registration
- Regularly **rotate client secrets**
- Monitor **agent actions** via Microsoft Defender
- Enable **DLP policies** for sensitive calendar data

## Additional Resources

- [Microsoft Agent 365 Documentation](https://learn.microsoft.com/en-us/microsoft-agent-365/)
- [Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [Agent 365 MCP Servers Reference](https://learn.microsoft.com/en-us/microsoft-agent-365/mcp-server-reference)
- [Agent Testing Guide](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/testing?tabs=python)
- [Agent Deployment Guide](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/deployment)

## Support

For issues, questions, or feedback:

- **Issues**: [GitHub Issues](https://github.com/microsoft/Agent365-Samples/issues)
- **Documentation**: [Microsoft Agent 365 Developer Docs](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/)
- **Community**: [Agent 365 Discussions](https://github.com/microsoft/Agent365-Samples/discussions)

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

## License

Copyright (c) Microsoft Corporation. All rights reserved.

Licensed under the MIT License - see [LICENSE](../../LICENSE.md) for details.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
