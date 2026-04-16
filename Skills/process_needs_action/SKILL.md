# Skill: Process Needs Action

## Purpose
Scan the /Needs_Action/ folder, reason about each item, create a Plan.md in /Plans/, create approval files for sensitive actions, update Dashboard.md, and move processed files to /Done/.

## Steps
1. List all .md files in /Needs_Action/
2. For each file, read its frontmatter and content
3. Determine the appropriate action based on Company_Handbook.md rules
4. **Create a `Plan.md` in `/Plans/`** documenting the intended reasoning and steps
5. **For sensitive actions** (e.g., payments, external posts), create an approval file in `/Pending_Approval/`
6. Update Dashboard.md with the item status
7. Append a log entry to /Logs/YYYY-MM-DD.json
8. Move the file from /Needs_Action/ to /Done/

## Output Format
- **Plan.md**: Detailed reasoning for the action.
- **Approval Files** (in `/Pending_Approval/`):
  - **Email**: Must include `action: email_send`, `to: <email>`, `subject: <subject>`, and a `## Content` section for the body.
  - **WhatsApp**: Must include `action: whatsapp_reply`, `contact: <name>`, and a `## Content` section for the reply.
  - **LinkedIn**: Must include `action: linkedin_post` and a `## Content` section for the post text.
- **Dashboard.md**:
  - [TIMESTAMP] ACTION_TAKEN — FILE_NAME
