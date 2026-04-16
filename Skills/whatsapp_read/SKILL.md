---
name: whatsapp_read
description: Read unread WhatsApp messages by executing the fetch_unread_whatsapp script and processing the output.
---

# Skill: WhatsApp Read

## Purpose
Allows Claude to retrieve unread messages from WhatsApp using the local Playwright-based watcher script. This skill is used as part of the perception layer to ingest new communications into the vault.

## When to Use This Skill
- When the user asks "Do I have any new WhatsApp messages?"
- During periodic audit checks to ensure all messages are captured
- When troubleshooting why a message wasn't automatically picked up by the background watcher

## How to Execute
1.  **Locate the Script**: The core script is at `scripts/fetch_unread_whatsapp.py`.
2.  **Run via Python**:
    ```bash
    python scripts/fetch_unread_whatsapp.py
    ```
3.  **Process Output**:
    - The script will print `UNREAD_CONTACT: <Name>` and `PREVIEW: <Text>` to stdout.
    - If unread messages are found, create a new .md file in the `/Needs_Action` folder following the `WHATSAPP_<contact>_<timestamp>.md` naming convention.
4.  **Action File Format**:
    ```yaml
    ---
    type: whatsapp_message
    contact: <Contact Name>
    received: <ISO Timestamp>
    priority: high
    status: pending
    ---

    ## Message Content
    <Message text found in preview/output>

    ## Suggested Actions
    - [ ] Reply to WhatsApp message for '<Contact Name>'
    - [ ] Log request in CRM/Accounting
    ```

## Safety Rules
- Do not attempt to log in if the session is expired; instead, alert the user that manual login via `scripts/login_manager.py` is required.
- Do not read messages that are already marked as "processed" in the `whatsapp_watcher.py` logs or session.
