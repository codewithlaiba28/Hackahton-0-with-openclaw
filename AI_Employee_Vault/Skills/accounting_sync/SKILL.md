# Skill: Accounting Sync

## Purpose
Sync financial data between the vault and Odoo.
Read transactions, create draft invoices, flag anomalies.

## Steps
1. Read Accounting/Current_Month.md
2. Connect to Odoo via MCP to fetch invoices and payments
3. Compare vault records with Odoo records
4. For new transactions not in Odoo: create draft invoice/expense in Odoo
 (draft only — never post without approval)
5. Flag any transaction over $500 in /Pending_Approval/
6. Update Accounting/Current_Month.md with latest data
7. Log sync to /Logs/

## Rules
- Never post (confirm) invoices in Odoo without approval
- Never initiate payments — read-only on bank data
- Flag any duplicate transactions
