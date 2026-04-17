# 🤖 Personal AI Employee — Hackathon 0

> **Tier:** ✅ Gold | **Engine:** Claude Code | **Memory:** Obsidian Vault (Local-First)

A fully autonomous Digital FTE (Full-Time Equivalent) that monitors Gmail, WhatsApp, LinkedIn, Instagram, Twitter, Facebook, and filesystem, reasons about tasks using Claude Code, manages accounting via Odoo 19, and generates weekly CEO briefings — all locally, with human-in-the-loop safeguards.

---

## 🏗️ Architecture

```
External Sources (Gmail, WhatsApp, LinkedIn, Instagram, Twitter, Facebook, File Drops)
         │
         ▼
 [Perception Layer]          Python Watcher Scripts
  gmail_watcher.py   ──┐
  whatsapp_watcher.py  ├──┐
  linkedin_watcher.py  ├──┤
  filesystem_watcher.py┘  │
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
 [Action Layer]              MCP Servers + Browser Automation
  mcp_gmail_server.py      ──┐
  mcp_odoo_server.py      ──┤
  browser_instagram_poster.py ├──┤
  browser_twitter_poster.py  ├──┤
  browser_facebook_poster.py ├──┤
  linkedin_poster.py      ──┤
  whatsapp_reply.py        ──┘
         │
         ▼
      /Done/  +  /Logs/  +  /Briefings/
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.13+
python --version

# Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client watchdog playwright fastmcp xmlrpc

# Install Playwright browsers
playwright install chromium

# Node.js 24+ (for Claude Code)
node --version
claude --version
```

### 2. Configure Credentials

```bash
# Copy template and fill in your credentials
cp .env.example .env
```

Edit `.env` with your API keys (Gmail, Odoo URL/DB/User/Password, social media sessions).

### 3. Authenticate Browser Sessions

```bash
# Authenticate each platform (a browser window will open — log in manually)
python scripts/login_manager.py --platform twitter
python scripts/login_manager.py --platform instagram
python scripts/login_manager.py --platform facebook
python scripts/login_manager.py --platform linkedin
python scripts/login_manager.py --platform whatsapp
```

### 4. Start the Orchestrator

```bash
python orchestrator.py
```

---

## 📁 Folder Structure

| Folder | Purpose |
|---|---|
| `/Inbox/` | Raw incoming items |
| `/Needs_Action/` | Items pending AI reasoning |
| `/Plans/` | PLAN_*.md files from Claude |
| `/Pending_Approval/` | Awaiting human sign-off |
| `/Approved/` | Human-approved → triggers action |
| `/Done/` | Completed tasks (never deleted) |
| `/Logs/` | Audit trail JSON logs |
| `/Briefings/` | Weekly CEO Audit reports |
| `/Skills/` | Agent Skill definitions for Claude Code |

---

## 🏆 Hackathon Tier Status: GOLD ✅

### ✅ Bronze Tier (Foundation) — COMPLETE
- [x] **Obsidian Vault**: `Dashboard.md`, `Company_Handbook.md`, and full folder structure
- [x] **Watcher Script**: Gmail and Filesystem monitoring active
- [x] **Claude Code Integration**: Reads from and writes to the vault
- [x] **Agent Skills**: 9 skills in `/Skills/` (all AI functionality as Agent Skills)

### ✅ Silver Tier (Functional Assistant) — COMPLETE
- [x] **Multi-Watcher System**: Gmail + WhatsApp + LinkedIn watchers running
- [x] **LinkedIn Automation**: Automated business posting to generate sales
- [x] **Claude Reasoning Loop**: Creates `Plan.md` files for every task
- [x] **MCP Server**: `mcp_gmail_server.py` for standard email actions
- [x] **Human-in-the-Loop**: Full approval workflow via `/Pending_Approval/`
- [x] **Basic Scheduling**: Orchestrator polls on schedule

### ✅ Gold Tier (Autonomous Employee) — COMPLETE
- [x] **Full Cross-Domain Integration**: Personal (Gmail, WhatsApp) + Business (Social Media, Accounting)
- [x] **Odoo 19 Accounting Integration**: `mcp_odoo_server.py` via JSON-RPC — create invoices, list partners, get revenue summary
- [x] **Instagram Automation**: Real-time browser-based posting with image support
- [x] **Twitter (X) Automation**: Real-time browser-based posting
- [x] **Facebook Automation**: Real-time browser-based posting
- [x] **Multiple MCP Servers**: Gmail MCP + Odoo MCP
- [x] **Weekly CEO Briefing**: `ceo_briefing_auditor.py` — cross-domain audit with financial + social summary
- [x] **Error Recovery**: Graceful degradation with stealth browser args and retry logic
- [x] **Comprehensive Audit Logging**: All actions logged to `/Logs/YYYY-MM-DD.json`
- [x] **Architecture Documentation**: Full lessons-learned documented here
- [x] **All AI Functionality as Agent Skills**: All capabilities wrapped as SKILL.md

---

## 🔑 Key Scripts

| Script | Purpose |
|---|---|
| `orchestrator.py` | Master process: starts all watchers, runs scheduling |
| `scripts/login_manager.py` | Authenticate browser sessions for all platforms |
| `scripts/mcp_gmail_server.py` | MCP server: send/draft Gmail |
| `scripts/mcp_odoo_server.py` | MCP server: Odoo accounting (invoices, partners, revenue) |
| `scripts/browser_instagram_poster.py` | Real-time Instagram posts via browser session |
| `scripts/browser_twitter_poster.py` | Real-time Twitter posts via browser session |
| `scripts/browser_facebook_poster.py` | Real-time Facebook posts via browser session |
| `scripts/linkedin_poster.py` | LinkedIn posts via browser session |
| `scripts/whatsapp_reply.py` | WhatsApp message replies via browser session |
| `scripts/ceo_briefing_auditor.py` | Generates weekly CEO Briefing from Odoo + social logs |

---

## 🛡️ Security
- All credentials stored in `.env` (gitignored — never committed)
- Browser sessions saved locally (never synced to cloud)
- All financial/sensitive actions require human approval via `/Pending_Approval/`
- Audit log retained for 90 days in `/Logs/`

---

## 🧠 Agent Skills (9 Total)

| Skill | Purpose |
|---|---|
| `process_needs_action` | Scan /Needs_Action, reason, move to /Done |
| `gmail_watcher` | Monitor Gmail for important emails |
| `filesystem_watcher` | Watch /Uploads for new file drops |
| `update_dashboard` | Refresh Dashboard.md |
| `vault_read_write` | Safe read/write to vault with naming conventions |
| `log_action` | Append entries to /Logs/YYYY-MM-DD.json |
| `whatsapp_read` | Fetch unread messages from WhatsApp |
| `whatsapp_reply` | Send messages to WhatsApp contacts |
| `linkedin_post` | Post business updates to LinkedIn |

---

*Built for Hackathon 0 — Personal AI Employee | Panaversity 2026*
*Gold Tier Achieved — 2026-04-17*
