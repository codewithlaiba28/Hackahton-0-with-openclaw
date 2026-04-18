# Skill: CEO Briefing Generator

## Purpose
Every Sunday night, autonomously audit the week's activity and generate
a Monday Morning CEO Briefing saved to /Briefings/.

## Trigger
- Scheduled: cron every Sunday at 10:00 PM

## Steps
1. Read Business_Goals.md for targets and metrics
2. List all files in /Done/ created this week
3. Read Accounting/Current_Month.md for financial data
4. Query Odoo via MCP for invoice and payment status
5. Identify bottlenecks: tasks that took > 2x expected time
6. Run subscription audit against known subscriptions list
7. Generate /Briefings/YYYY-MM-DD_Monday_Briefing.md
8. Update Dashboard.md with briefing link
9. Log generation to /Logs/

## Output Format
Must follow the CEO Briefing template exactly (see ceo_briefing_generator.py)
