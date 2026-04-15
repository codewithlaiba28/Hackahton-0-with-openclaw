---
name: filesystem_watcher
description: Monitors the /Uploads/ drop folder for new files and creates action entries in /Needs_Action/
---

# Skill: Filesystem Watcher

## Purpose
Monitor a designated local drop folder (`/Uploads/`) for any newly created files. When a file appears, copy it to `/Needs_Action/` and create a companion `.md` metadata file so Claude Code can process it.

## When to Use This Skill
- When the user wants to start monitoring a folder for file drops
- When the user drags a document into the Uploads folder for AI processing
- When the filesystem watcher process has stopped and needs restarting

## Steps

### 1. Verify Prerequisites
- Confirm `filesystem_watcher.py` exists in the vault root
- Confirm the `Uploads/` watch directory exists (it will be created automatically if not)
- Confirm `watchdog` Python library is installed: `pip install watchdog`

### 2. Start the Watcher
```bash
python filesystem_watcher.py
```
Or via the orchestrator (recommended — handles auto-restart):
```bash
python orchestrator.py
```

### 3. Watcher Behaviour
- Uses `watchdog` library to listen for `FileCreatedEvent` in the `/Uploads/` directory
- On new file detection:
  1. Copies the file to `/Needs_Action/FILE_<filename>`
  2. Creates a metadata file at `/Needs_Action/FILE_<filename>.md`:
     ```yaml
     ---
     type: file_drop
     original_name: <filename>
     size: <bytes>
     copied_timestamp: <unix-timestamp>
     ---
     A new file '<filename>' was detected and copied for processing.
     ```

### 4. After Files Are Created
Invoke the `process_needs_action` skill to have Claude reason about and act on the dropped file.

### 5. Supported Use Cases
| File Type | Suggested Action |
|-----------|-----------------|
| `.pdf` / `.docx` | Summarize and extract key info |
| `.csv` / `.xlsx` | Analyze data and log to Accounting |
| `.txt` | Read and create action plan |
| Image files | Describe and categorize |

## Error Recovery
- If watch directory is missing: will be auto-created on next run
- If file copy fails: error is logged, no metadata file created, file stays in Uploads
- Watcher is non-recursive (only watches top-level of Uploads folder)
