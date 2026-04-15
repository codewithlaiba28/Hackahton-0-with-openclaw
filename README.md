# 🤖 Personal AI Employee — Hackathon 0

> **Tier:** Bronze | **Engine:** Claude Code | **Memory:** Obsidian Vault (Local-First)

A fully autonomous Digital FTE (Full-Time Equivalent) that monitors your Gmail and filesystem, reasons about incoming tasks using Claude Code, and manages your life via an Obsidian vault — all locally, with human-in-the-loop safeguards.

---

## 🏗️ Architecture

```
External Sources (Gmail, File Drops)
         │
         ▼
 [Perception Layer]          Python Watcher Scripts
  gmail_watcher.py   ──┐
  filesystem_watcher.py ┤──▶  /Needs_Action/  (Obsidian Vault)
                        │
         ┌──────────────┘
         ▼
 [Reasoning Layer]           Claude Code
  Reads /Needs_Action/
  Creates Plan.md files
  Writes approval requests ──▶  /Pending_Approval/
         │
         ▼ (human approves)
 [Action Layer]              MCP Servers (future)
  Sends emails, logs, posts
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
pip install google-auth google-auth-oauthlib google-api-python-client watchdog

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
VAULT_PATH=.
```

Place your `credentials.json` (from Google Cloud Console OAuth2) in the project root.

### 3. Start the Orchestrator

```bash
python orchestrator.py
```

This will:
- Create all required vault folders
- Start the Gmail watcher (polls every 2 min)
- Start the filesystem watcher (monitors `/Uploads/`)
- Update `Dashboard.md` every 5 minutes

### 4. Drop Files to Process

Drop any file into the `/Uploads/` folder — the filesystem watcher will copy it to `/Needs_Action/` automatically.

### 5. Run Claude Code against the Vault

```bash
claude
```

Then use skills:
```
/process_needs_action
/update_dashboard
/log_action
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
| `/Rejected/` | Human-rejected → archived |
| `/Done/` | Completed tasks (never deleted) |
| `/Logs/` | Audit trail JSON logs |
| `/Skills/` | Agent Skill definitions for Claude Code |
| `/Uploads/` | Drop folder — filesystem watcher monitors this |

---

## 🧠 Agent Skills

All AI functionality is implemented as Claude Code Agent Skills in `/Skills/`:

| Skill | File | Description |
|---|---|---|
| `process_needs_action` | `Skills/process_needs_action/SKILL.md` | Process items in /Needs_Action |
| `gmail_watcher` | `Skills/gmail_watcher/SKILL.md` | Monitor Gmail inbox |
| `filesystem_watcher` | `Skills/filesystem_watcher/SKILL.md` | Monitor /Uploads drop folder |
| `update_dashboard` | `Skills/update_dashboard/SKILL.md` | Refresh Dashboard.md |
| `vault_read_write` | `Skills/vault_read_write/SKILL.md` | Safe vault file operations |
| `log_action` | `Skills/log_action/SKILL.md` | Append audit log entries |

---

## 🔒 Security

- Credentials stored in `.env` (never committed — see `.gitignore`)
- `credentials.json` and `token.json` are local-only
- All financial/sensitive actions require human approval via `/Pending_Approval/`
- Audit log retained for 90 days in `/Logs/`
- `DRY_RUN=true` mode available in all action scripts

---

## 🏆 Hackathon Tier: Bronze

### ✅ Completed Requirements
- [x] `Dashboard.md` — live status board
- [x] `Company_Handbook.md` — Rules of Engagement
- [x] Gmail Watcher (`simple_gmail_watcher.py`)
- [x] Filesystem Watcher (`filesystem_watcher.py`)
- [x] Claude Code reads/writes to vault (`orchestrator.py`)
- [x] Folder structure: `/Inbox`, `/Needs_Action`, `/Done` (+ more)
- [x] All AI functionality as Agent Skills (6 skills in `/Skills/`)

---

## 📜 Credential Disclosure

- No API keys are stored in source code or markdown files
- Gmail OAuth uses token-based auth; tokens stored locally in `token.json`
- `.env`, `token.json`, `credentials.json` are listed in `.gitignore`

---

*Built for Hackathon 0 — Personal AI Employee | Panaversity 2026*
