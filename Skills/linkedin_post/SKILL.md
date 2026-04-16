---
name: linkedin_post
description: Post a status update or business message to LinkedIn by executing the linkedin_poster script.
---

# Skill: LinkedIn Post

## Purpose
Enables the AI Employee to share business updates, marketing content, or sales-related posts to LinkedIn autonomously or after approval.

## When to Use This Skill
- To post a daily business update as defined in the scheduling rules
- When generating sales leads through social media presence
- When the user asks "Post this to my LinkedIn: [Content]"

## How to Execute
1.  **Locate the Script**: The core script is at `scripts/linkedin_poster.py`.
2.  **Run via Python**:
    ```bash
    python scripts/linkedin_poster.py --content "<Post Content>"
    ```
3.  **Handle Success/Failure**:
    - verify that the post was successful by checking the script output.
    - Log completion in `Logs/` and update `Dashboard.md`.

## Safety Rules
- **Approval required**: All LinkedIn posts must be approved by the human supervisor (HITL) unless explicitly marked for auto-post in `LinkedIn_Strategy.md`.
- **Media**: Currently only supports text posts. If media is required, notify the user.
- **Session**: Ensure `linkedin_session` is active. If common login issues occur, execute `scripts/login_manager.py`.

## Example Usage
"Post a greeting for the new week."
```bash
python scripts/linkedin_poster.py --content "Happy Monday everyone! Excited for another productive week of building AI Employees."
```
