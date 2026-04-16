# 🤖 Personal AI Employee — Hackathon 0

> **Tier:** Silver | **Engine:** Claude Code | **Memory:** Obsidian Vault (Local-First)

A fully autonomous Digital FTE (Full-Time Equivalent) that monitors your Gmail, WhatsApp, LinkedIn, and filesystem, reasons about tasks using Claude Code, and manages your life via an Obsidian vault — all locally, with human-in-the-loop safeguards.

---

## 🏗️ Architecture

```
External Sources (Gmail, WhatsApp, LinkedIn, File Drops)
         │
         ▼
 [Perception Layer]          Python Watcher Scripts
  gmail_watcher.py   ──┐
  whatsapp_watcher.py  ├──┐
  linkedin_watcher.py  ├──┤
  filesystem_watcher.py ┘  │
                           ▼
 [Core Management]         /Needs_Action/  (Obsidian Vault)
                           │
         ┌─────────────────┘
         ▼
 [Reasoning Layer]           Claude Code
  Reads /Needs_Action/
  Creates Plan.md files
  Writes approval requests ──▶  /Pending_Approval/
         │
         ▼ (human approves)
 [Action Layer]              MCP Servers + Agent Skills
  mcp_gmail_server.py  ──┐
  linkedin_poster.py   ──┤
  whatsapp_reply.py    ──┘
         │
         ▼
      /Done/  +  /Logs/
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.13+
python --version

# Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client watchdog playwright fastmcp

# Node.js 24+ (for Claude Code)
node --version
claude --version
```

### 2. Configure Credentials

```bash
# Copy and fill in your credentials
cp .env.example .env
```

Edit `.env`:
```
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
VAULT_PATH=AI_Employee_Vault
```

Place your `credentials.json` (from Google Cloud Console OAuth2) in the project root.

### 3. Start the Orchestrator

```bash
python orchestrator.py
```

This will:
- Create all required vault folders
- Start all Watchers (Gmail, WhatsApp, LinkedIn, Filesystem, Approval)
- Update `Dashboard.md` every 5 minutes
- Trigger Claude processing loop

---

## 📁 Folder Structure

| Folder | Purpose |
|---|---|
| `/Inbox/` | Raw incoming items |
| `/Needs_Action/` | Items pending AI reasoning |
| `/Plans/` | PLAN_*.md files from Claude |
| `/Pending_Approval/` | Awaiting human sign-off |
| `/Approved/` | Human-approved → triggers action |
| `/Logs/` | Audit trail JSON logs |
| `/Skills/` | Agent Skill definitions for Claude Code |

---

## 🏆 Hackathon Tier: Silver

### ✅ Completed Requirements
- [x] **Obsidian Vault**: Dashboard.md, Company_Handbook.md, and folder structure.
- [x] **Multi-Watcher System**: Gmail, WhatsApp, LinkedIn, and Filesystem monitoring.
- [x] **Automated Business Posting**: Reliable LinkedIn status updates.
- [x] **MCP Server**: Working `mcp_gmail_server.py` for standard external actions.
- [x] **Human-in-the-Loop**: Approval workflow for sensitive actions.
- [x] **Agent Skills**: 9 optimized skills in `/Skills/`.
- [x] **Orchestration**: Automated reasoning loop via `orchestrator.py`.

---

## 🛡️ Security
- Credentials stored in `.env` (never committed).
- All financial/sensitive actions require human approval via `/Pending_Approval/`.
- Audit log retained for 90 days.

---

*Built for Hackathon 0 — Personal AI Employee | Panaversity 2026*

