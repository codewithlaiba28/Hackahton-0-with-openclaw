---
name: whatsapp_reply
description: Send a reply to a WhatsApp contact by executing the whatsapp_reply script.
---

# Skill: WhatsApp Reply

## Purpose
Allows Claude to send outbound messages to WhatsApp contacts using the local Playwright-based automation.

## When to Use This Skill
- To reply to an inquiry in `/Needs_Action` after approval
- When the user explicitly asks to "Send a WhatsApp message to [Contact] saying [Message]"
- To send automated business updates or invoices (after human-in-the-loop approval)

## How to Execute
1.  **Locate the Script**: The core script is at `scripts/whatsapp_reply.py`.
2.  **Run via Python**:
    ```bash
    python scripts/whatsapp_reply.py "<Contact Name>" "<Message Content>"
    ```
3.  **Handle Success/Failure**:
    - If the script exits with code 0, mark the corresponding task as done in the vault.
    - If it fails, log the error and notify the user.

## Safety Rules
- **Human-in-the-Loop**: Always require approval for messages to new contacts or for payment-related replies.
- **Dry Run**: If the `.env` file has `DRY_RUN=true`, the script will only log the message without sending. Claude must inform the user if it's in dry-run mode.
- **Tone**: Always adhere to the tone and rules defined in `Company_Handbook.md`.

## Example Usage
"Reply to 'John Doe' confirming receipt of payment."
```bash
python scripts/whatsapp_reply.py "John Doe" "Hi John, I've received your payment. Thank you!"
```
