# Skill: Process Needs Action

## Purpose
Scan the /Needs_Action/ folder, reason about each item, update Dashboard.md, and move processed files to /Done/.

## Steps
1. List all .md files in /Needs_Action/
2. For each file, read its frontmatter and content
3. Determine the appropriate action based on Company_Handbook.md rules
4. Update Dashboard.md with the item status
5. Append a log entry to /Logs/YYYY-MM-DD.json
6. Move the file to /Done/

## Output Format
For each item processed, write a brief summary line in Dashboard.md under "Recent Activity":
- [TIMESTAMP] ACTION_TAKEN — FILE_NAME
