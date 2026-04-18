# AI Employee — Architecture Documentation

## Overview
Gold Tier Personal AI Employee — Local-first autonomous agent.

## Components
- **Brain**: Claude Code via ralph_loop.py
- **Memory**: Obsidian vault (local Markdown)
- **Senses**: Python Watcher scripts (Gmail, WhatsApp, Filesystem)
- **Hands**: MCP Servers (Email, Browser, Filesystem)
- **Accounting**: Odoo Community (Docker, localhost:8069)
- **Social**: Facebook Graph API, Instagram Graph API, Twitter v2 API

## Data Flow
External Source → Watcher → /Needs_Action/ → Claude (Ralph Loop)
→ Plan.md created → /Pending_Approval/ (if sensitive)
→ Human approves → /Approved/ → Action executed → /Done/ → Logged

## Security
- All credentials in .env (never committed)
- DRY_RUN=true during development
- All financial actions require human approval
- Session files excluded from git
- Audit log retained 90 days
