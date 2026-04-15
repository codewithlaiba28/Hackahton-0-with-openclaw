---
name: log_action
description: Append a structured JSON audit log entry to /Logs/YYYY-MM-DD.json for every action taken by the AI Employee
---

# Skill: Log Action

## Purpose
Maintain a tamper-evident, chronological audit trail of every action the AI Employee takes. This is required for security compliance, debugging, and the weekly CEO Briefing generation.

## When to Use This Skill
- After every action Claude takes (email draft, file move, plan creation, approval request, etc.)
- After every human approval or rejection event
- When a watcher creates a new Needs_Action file

## Log File Location
```
/Logs/YYYY-MM-DD.json
```
One file per calendar day. If the file does not exist, create it with an empty JSON array `[]`.

## Log Entry Format
Each entry is a JSON object appended to the array:

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "<see Action Types below>",
  "actor": "claude_code",
  "source_file": "<path to trigger file, if any>",
  "target": "<email, filename, URL, or description>",
  "parameters": {},
  "approval_status": "<not_required|pending|approved|rejected>",
  "approved_by": "<human|auto>",
  "result": "<success|failure|pending>",
  "notes": "<optional free text>"
}
```

## Action Types
| `action_type` | Description |
|---|---|
| `file_created` | New file written to vault |
| `file_moved` | File moved between folders |
| `email_drafted` | Email draft created |
| `email_sent` | Email sent via MCP |
| `plan_created` | PLAN_*.md file created |
| `approval_requested` | File written to /Pending_Approval/ |
| `approval_granted` | Human moved file to /Approved/ |
| `approval_rejected` | Human moved file to /Rejected/ |
| `dashboard_updated` | Dashboard.md rewritten |
| `watcher_started` | Watcher process launched |
| `watcher_restarted` | Watcher process restarted after crash |
| `error` | Any caught exception |

## Steps

### 1. Determine Today's Log File Path
```
log_path = /Logs/<YYYY-MM-DD>.json
```

### 2. Read Existing Log
- If file exists: parse the JSON array
- If file does not exist: start with `[]`

### 3. Append New Entry
Build the entry object using the format above and append it to the array.

### 4. Write Back
Overwrite the log file with the updated array (pretty-printed with 2-space indent).

### 5. Confirm
Output: `Logged: <action_type> → <target> at <timestamp>`

## Example Entry
```json
{
  "timestamp": "2026-01-07T10:45:00Z",
  "action_type": "file_moved",
  "actor": "claude_code",
  "source_file": "Needs_Action/EMAIL_msg123_2026-01-07.md",
  "target": "Done/EMAIL_msg123_2026-01-07.md",
  "parameters": {},
  "approval_status": "not_required",
  "approved_by": "auto",
  "result": "success",
  "notes": "Email reviewed and classified as informational, no reply needed."
}
```

## Retention Policy
- Keep logs for a minimum of **90 days**
- Do not delete log files without explicit human approval
