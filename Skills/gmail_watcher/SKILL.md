---
name: gmail_watcher
description: Monitors Gmail for unread/important emails and writes action files to /Needs_Action/
---

# Skill: Gmail Watcher

## Purpose
Monitor the user's Gmail inbox for unread and important emails, then create structured `.md` action files in the `/Needs_Action/` folder so Claude Code can reason about and respond to them.

## When to Use This Skill
- When the user wants to start continuous Gmail monitoring
- When checking for new unread emails that need attention
- When the Gmail watcher process has stopped and needs restarting

## Steps

### 1. Verify Prerequisites
- Confirm `credentials.json` exists in the vault root (OAuth2 credentials from Google Cloud Console)
- Confirm `.env` contains required vars: `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`
- Confirm `gmail_watcher.py` (or `simple_gmail_watcher.py`) exists in the vault root

### 2. Start the Watcher
Run the watcher script in the background:
```bash
python simple_gmail_watcher.py
```
Or via the orchestrator which manages it automatically:
```bash
python orchestrator.py
```

### 3. Watcher Behaviour
- Polls Gmail every 120 seconds for `is:unread is:important` messages
- For each new message, creates a file at:
  `/Needs_Action/EMAIL_<id>.md`
  with frontmatter:
  ```yaml
  ---
  type: email
  from: <sender>
  subject: <subject>
  received: <iso-timestamp>
  priority: high
  status: pending
  ---
  ```
- Tracks processed message IDs to avoid duplicates (stored in `gmail_processed_ids.json`)

### 4. After Files Are Created
Invoke the `process_needs_action` skill so Claude can read, reason about, and respond to each email action file.

### 5. Logging
All watcher activity is logged to `gmail_watcher.log` in the vault root and to `/Logs/YYYY-MM-DD.json`.

## Security
- Never store Gmail credentials in plain text inside the vault
- Use `.env` file (excluded from git via `.gitignore`)
- OAuth tokens are stored in `token.json` — rotate every 90 days

## Error Recovery
- If Gmail API returns 403: re-run the OAuth flow (`python simple_gmail_watcher.py --reauth`)
- If watcher crashes: the `orchestrator.py` will auto-restart it within 60 seconds
- Exponential backoff is applied on transient network errors
