---
name: vault_read_write
description: Safely read from and write to the Obsidian vault following the established folder structure and naming conventions
---

# Skill: Vault Read / Write

## Purpose
Provide a consistent, safe interface for all Claude Code read and write operations against the Obsidian vault. Enforces folder conventions, naming standards, and audit logging for every operation.

## When to Use This Skill
- Any time Claude needs to read a file from the vault
- Any time Claude needs to create or update a file in the vault
- When moving files between vault folders (e.g., Needs_Action → Done)
- When creating Plan files, approval requests, or log entries

## Vault Folder Structure
```
/Vault/
├── Inbox/                  ← New unprocessed items (raw drops)
├── Needs_Action/           ← Items requiring AI reasoning
├── Done/                   ← Completed items (never delete)
├── Plans/                  ← PLAN_*.md files created by Claude
├── Pending_Approval/       ← Approval request files
├── Approved/               ← Human-approved items (triggers MCP action)
├── Rejected/               ← Human-rejected items
├── Logs/                   ← YYYY-MM-DD.json audit logs
├── Dashboard.md            ← Live status board
└── Company_Handbook.md     ← Rules of Engagement
```

## Read Operations

### Reading a file
1. Use the filesystem MCP or built-in file tools to read the file
2. Parse YAML frontmatter if present (between `---` delimiters)
3. Apply rules from `Company_Handbook.md` when reasoning about content

### Listing a folder
```
List all .md files in /Needs_Action/ ordered by modification time (newest first)
```

## Write Operations

### Creating a new action file in /Needs_Action/
Naming convention: `<TYPE>_<identifier>_<YYYY-MM-DD>.md`
Examples:
- `EMAIL_client_a_2026-01-07.md`
- `FILE_report_q1_2026-01-07.md`
- `WHATSAPP_lead_inquiry_2026-01-07.md`

Required frontmatter:
```yaml
---
type: <email|file_drop|whatsapp|manual>
source: <origin description>
received: <ISO-8601>
priority: <high|medium|low>
status: pending
---
```

### Creating a Plan file in /Plans/
Naming convention: `PLAN_<description>_<YYYY-MM-DD>.md`

### Creating an Approval Request in /Pending_Approval/
Naming convention: `APPROVAL_<action>_<YYYY-MM-DD>.md`

Required frontmatter:
```yaml
---
type: approval_request
action: <action type>
created: <ISO-8601>
expires: <ISO-8601 — 24 hours after created>
status: pending
---
```

## Moving Files (Completing Tasks)
When a task is done:
1. Move file from `/Needs_Action/` (or `/Plans/`) → `/Done/`
2. Update `Dashboard.md` via the `update_dashboard` skill
3. Append an entry to `/Logs/YYYY-MM-DD.json` via the `log_action` skill

## Safety Rules
- **Never delete files** — only move them to `/Done/` or `/Rejected/`
- **Never write outside the vault root** without explicit human approval
- **Never overwrite** existing `/Done/` files
- **Sensitive files** (`.env`, `credentials.json`, `token.json`) must never be read or modified by Claude
