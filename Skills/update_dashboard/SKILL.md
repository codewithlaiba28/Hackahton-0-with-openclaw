---
name: update_dashboard
description: Reads vault state and rewrites Dashboard.md with current system status, pending items, and recent activity
---

# Skill: Update Dashboard

## Purpose
Generate an up-to-date `Dashboard.md` that summarizes the current state of the AI Employee system including pending actions, completed tasks, active projects, and system health.

## When to Use This Skill
- After processing items from `/Needs_Action/`
- At the start of each work session
- When the user asks for a status report
- On a scheduled basis (e.g., every 5 minutes via orchestrator)

## Steps

### 1. Count Items in Each Folder
```
- /Needs_Action/*.md  → count as "Pending Actions"
- /Done/*.md          → count files modified today as "Completed Today"
- /Plans/*.md         → count as "Active Projects"
- /Pending_Approval/*.md → count as "Awaiting Approval"
```

### 2. Read Recent Activity
- List the 5 most recently modified files in `/Done/` (by `st_mtime`)
- Extract their names and timestamps

### 3. Read Alerts
- Any file in `/Pending_Approval/` older than 24 hours → flag as overdue
- Any `/Needs_Action/` file with `priority: high` frontmatter → flag as urgent

### 4. Write Dashboard.md
Overwrite `Dashboard.md` with the following structure:

```markdown
---
last_updated: <ISO-8601 timestamp>
status: active
---

# AI Employee Dashboard

## Status
- Pending Actions: <count>
- Completed Today: <count>
- Active Projects: <count>
- Awaiting Approval: <count>

## Recent Activity
- [<timestamp>] <action> — <filename>
...

## Alerts
- <alert description if any>

## System Health
- Gmail Watcher: <Active/Inactive>
- Filesystem Watcher: <Active/Inactive>
- Orchestrator: <Running>

---
*Last updated by AI Employee*
```

### 5. Output Confirmation
After writing, respond with:
`Dashboard updated at <timestamp>. X pending, Y completed today.`

## Notes
- Never delete existing activity log entries — always append
- If no activity exists, write `_No activity yet._` under Recent Activity
- Timestamps should use ISO-8601 format: `2026-01-07T10:30:00`
