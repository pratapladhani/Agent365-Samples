# Admin Agent - Design Document

## Overview

**Agent Name:** Admin Agent  
**Purpose:** AI administrative assistant demonstrating Agent 365 platform capabilities through calendar management  
**Target Users:** Professionals needing administrative support + Developers learning Agent 365

**Architecture Model:**

- 🤖 **Agent has its own identity** - Dedicated mailbox (e.g., adminagent@domain.com)
- 🔑 **Delegated Access** - User grants calendar/mailbox permissions to the agent
- 📬 **Can act on behalf** - Accepts meetings, sends emails, manages calendar
- 👤 **Real administrative assistant model** - AI-powered with human-like delegation

---

## High-Level Goals

### Primary Goal: Demonstrate Agent 365 Platform

This sample showcases the **Agent 365 platform** and **Agent Framework** capabilities through a practical, relatable use case:

1. **Platform Integration** - Multi-channel interaction (Teams, Email, Documents)
2. **Premium MCP Servers** - Microsoft Graph, Planner, Power BI integration
3. **Agent Framework Features** - Workflows, patterns, DevUI, observability
4. **Enterprise Patterns** - Delegated access, authentication, security
5. **Developer Learning** - Clear, well-documented sample for others to learn from

### Secondary Goal: Useful Calendar Assistant

Build a functional calendar management agent that saves time and demonstrates real value.

---

## Agent 365 Features Showcased

### 1. **Multi-Channel Interactions**

- ✅ Teams @mentions (`@AdminAgent find time with Sarah`)
- ✅ Direct email to agent's mailbox
- ✅ Document collaboration (Word, collaborative docs)
- ✅ Proactive notifications back to user

### 2. **Premium MCP Server Integration**

- ✅ **Outlook Calendar MCP** - Create, list, update, delete events; accept/decline; resolve conflicts (primary)
- ✅ **Outlook Mail MCP** - Create, update, delete messages; reply; semantic search
- ✅ **SharePoint/OneDrive MCP** - Upload files, get metadata, search, manage lists
- ✅ **Teams MCP** - Create/update chat, add members, post messages, channel operations
- ✅ **User Profile MCP** - Get manager, direct reports, profile info, search users

### 3. **Authentication & Security**

- ✅ Delegated access model (agent as separate identity)
- ✅ Microsoft Entra ID authentication
- ✅ Graph API permissions (Calendars.ReadWrite.Shared, Mail.Read/Send)
- ✅ Token management and refresh

### 4. **Agentic Behaviors**

- ✅ Proactive monitoring (meeting conflicts, invitations)
- ✅ Autonomous decision-making (auto-accept with rules)
- ✅ Human-in-the-loop approvals (conflict resolution)
- ✅ Context-aware responses (user preferences, patterns)

---

## Agent Framework Features Showcased

### 1. **Workflows**

- ✅ Multi-step calendar workflows using WorkflowBuilder
- ✅ Sequential executors for meeting management
- ✅ Conditional branching (auto-accept vs. needs approval)
- ✅ Workflow checkpointing and resume
- ✅ Time-travel debugging for calendar operations

### 2. **Tool & Function Patterns**

- ✅ `@ai_function` decorator for calendar tools
- ✅ Tool approvals for sensitive operations
- ✅ Stateful tools for maintaining context
- ✅ Error handling and recovery patterns
- ✅ Invocation limits for cost control

### 3. **DevUI Integration**

- ✅ Interactive workflow visualization
- ✅ Real-time execution tracking
- ✅ State inspection and debugging
- ✅ Checkpoint navigation UI
- ✅ `serve()` function for http://localhost:8093

### 4. **Observability**

- ✅ Agent Framework instrumentation
- ✅ Custom spans for calendar operations
- ✅ Activity tracking with Activity.Current
- ✅ Performance metrics and telemetry
- ✅ Error tracking and logging

### 5. **Multi-Agent Patterns**

- ✅ Sub-agents for specialized tasks:
  - **CalendarAnalyzer** - Conflict detection
  - **MeetingScheduler** - Find optimal times
  - **PrepAgent** - Meeting preparation
- ✅ `as_tool()` for hierarchical delegation
- ✅ Agent-to-agent communication patterns

### 6. **Context & Memory**

- ✅ Context providers for persistent preferences
- ✅ Meeting pattern learning
- ✅ User preference storage
- ✅ Cross-session memory (Mem0/Redis patterns)

### 7. **AG-UI Protocol Support**

- ✅ Web interface for testing
- ✅ State management for calendar view
- ✅ Predictive state updates
- ✅ Custom confirmation strategies
- ✅ Streaming responses

---

## Demo Scenarios (Quick Reference)

### Scenario 1: Setup Delegated Access

```
User grants Agent delegate permissions → Agent confirms access → Ready to manage calendar
```

### Scenario 2: Auto-Accept Meeting

```
Meeting invite arrives → Agent checks calendar + rules → Auto-accepts → Notifies user
```

### Scenario 3: Resolve Conflict

```
Conflicting meeting → Agent detects + analyzes priority → Suggests resolution → User approves → Agent executes
```

### Scenario 4: Find Meeting Time

```
@AdminAgent find time with Sarah → Agent queries calendars → Finds slots → Creates meeting → Confirms
```

### Scenario 5: Meeting Preparation

```
Agent detects upcoming meeting → Gathers context (emails, docs, tasks) → Sends prep brief to user
```

### Scenario 6: Calendar Optimization

```
@AdminAgent optimize my week → Agent analyzes calendar → Suggests improvements → User approves changes
```

---

## MVP Features (Phase 1) ⭐

**Focus: Calendar Management Core**

### 1. Delegated Calendar Access

- Setup agent identity with mailbox
- Grant delegate permissions via Graph API
- Verify and test calendar access
- **Showcases:** Authentication, Graph MCP, delegated access model

### 2. Auto-Accept/Decline Meetings

- Monitor for meeting invitations
- Apply rules (working hours, conflicts, sender)
- Auto-respond appropriately
- Send notifications to user
- **Showcases:** Workflows, proactive monitoring, tool execution

### 3. Find Meeting Time & Schedule

- Parse natural language requests (`@AdminAgent find time with...`)
- Query attendee availability via findMeetingTimes API
- Suggest optimal slots
- Create meeting on user's behalf
- **Showcases:** NLU, multi-step workflows, Graph API integration

### 4. Conflict Detection & Resolution

- Monitor for double-bookings
- Analyze meeting priority
- Suggest resolution strategies
- Execute with human-in-the-loop approval
- **Showcases:** Conditional logic, approvals, sub-agents

### 5. Meeting Preparation Brief

- Detect upcoming meetings (within 1 hour)
- Gather context: emails, documents, previous notes
- Generate prep brief with key points
- Proactively send to user
- **Showcases:** Multi-MCP integration, proactive behavior, context awareness

### 6. Calendar Analytics & Optimization

- Analyze calendar patterns
- Identify optimization opportunities
- Suggest improvements (decline, reschedule, buffer time)
- Apply changes with approval
- **Showcases:** Power BI MCP, analytics, batch operations

---

## Future Features (Phase 2+)

**Prioritized Backlog:**

- Email triage and management
- Task creation from meetings/emails
- Document collaboration (@mention in Word)
- Travel time and location intelligence
- Learning user preferences over time
- Team calendar coordination
- Weekly/daily briefings

---## Technical Implementation Notes

### Architecture

- **Agent Framework:** Python agent-framework with Azure OpenAI
- **Authentication:** Microsoft Entra ID with delegated permissions
- **MCP Integration:** Outlook Calendar, Outlook Mail, SharePoint/OneDrive, Teams, User Profile
- **Hosting:** aiohttp-based server (Agent 365 platform)
- **Observability:** Agent Framework instrumentation with custom spans

### Calendar Operations (via Outlook Calendar MCP)

- **List Events** - Get calendar events for delegated user
- **Create Event** - Schedule new meetings on user's calendar
- **Update Event** - Modify existing meeting details
- **Delete Event** - Remove events from calendar
- **Accept Meeting** - Accept incoming meeting invitations
- **Decline Meeting** - Decline meeting invitations
- **Find Meeting Times** - Query availability and suggest optimal slots
- **Resolve Conflicts** - Detect and resolve calendar conflicts

### Workflows Design

```python
# Example: Auto-Accept Workflow
workflow = (
    WorkflowBuilder()
    .register_executor(ReceiveMeetingInvite, name="receive")
    .register_executor(CheckCalendarAvailability, name="check_availability")
    .register_executor(ApplyRules, name="apply_rules")
    .register_executor(SendResponse, name="respond")
    .register_executor(NotifyUser, name="notify")
    .add_edge("receive", "check_availability")
    .add_edge("check_availability", "apply_rules")
    .add_edge("apply_rules", "respond")
    .add_edge("respond", "notify")
    .set_start_executor("receive")
    .build()
)
```

---

## Demo Script (5 Minutes)

### Setup (30 seconds)

1. Show agent mailbox: `adminagent@contoso.com`
2. Confirm delegate permissions in Graph Explorer
3. Open DevUI: `http://localhost:8093`

### Demo Flow (4 minutes)

1. **Auto-Accept** - Send meeting invite → Agent auto-accepts → User notified
2. **Conflict Resolution** - Create conflict → Agent detects → Suggests resolution → User approves
3. **Find Time** - `@AdminAgent find time with Sarah` → Agent finds slots → Creates meeting
4. **Meeting Prep** - Show proactive brief 30 min before meeting with context
5. **Workflow Visualization** - Show DevUI with real-time workflow execution
6. **Observability** - Demonstrate custom spans and telemetry

### Talking Points

- ✅ **Agent 365 Platform** - Multi-channel, MCP servers, authentication
- ✅ **Agent Framework** - Workflows, DevUI, observability, patterns
- ✅ **Real-World Value** - Saves 1-2 hours/day, reduces calendar stress
- ✅ **Enterprise-Ready** - Delegated access, security, scalability

---

## Development Roadmap

### Sprint 1 (Week 1-2): Foundation

- [ ] Setup agent infrastructure (agent.py, pyproject.toml)
- [ ] Configure Graph MCP with delegation
- [ ] Implement delegated access verification
- [ ] Create basic calendar query tools

### Sprint 2 (Week 3-4): Core Workflows

- [ ] Auto-accept/decline workflow
- [ ] Conflict detection workflow
- [ ] Find meeting time workflow
- [ ] DevUI integration

### Sprint 3 (Week 5-6): Advanced Features

- [ ] Meeting preparation workflow
- [ ] Calendar analytics
- [ ] Multi-agent patterns (sub-agents)
- [ ] Observability & telemetry

### Sprint 4 (Week 7-8): Polish & Demo

- [ ] AG-UI integration
- [ ] Checkpoint & resume support
- [ ] Context provider setup
- [ ] Demo preparation & testing

---

## Success Criteria

### Technical

- ✅ All 6 MVP features implemented
- ✅ Agent Framework features demonstrated (workflows, DevUI, observability)
- ✅ Graph MCP integration working with delegated access
- ✅ DevUI shows workflow execution visually
- ✅ Observability spans captured correctly

### Demo Quality

- ✅ 5-minute demo runs smoothly
- ✅ Showcases Agent 365 platform value
- ✅ Highlights Agent Framework capabilities
- ✅ Audience can imagine using it themselves
- ✅ Code is well-documented for learning

### Documentation

- ✅ Comprehensive README with setup instructions
- ✅ Code comments explain Agent Framework patterns
- ✅ Architecture diagrams show workflows
- ✅ Passes Agent 365 sample validation (Rules 1-3)

---

## Resources & References

- [Agent 365 Documentation](https://aka.ms/agent365)
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Agent Framework DevUI](https://github.com/microsoft/agent-framework/tree/main/python/packages/devui)
- [Microsoft Graph API - Calendar](https://learn.microsoft.com/graph/api/resources/calendar)
- [Agent Framework Sample](../agent-framework/sample-agent/)

---

_Last Updated: January 2, 2026_  
_Version: 0.2 - Simplified with Agent Framework showcase focus_
