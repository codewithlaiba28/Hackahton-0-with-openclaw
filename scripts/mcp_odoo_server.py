import os
import xmlrpc.client
from mcp.server.fastmcp import FastMCP
from pathlib import Path

# Initialize FastMCP server
mcp = FastMCP("Odoo_Accounting")

def get_odoo_config():
    """Load Odoo configuration from .env"""
    config = {}
    env_path = Path('.env')
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                config[k.strip()] = v.strip()
    return config

def get_odoo_connection():
    """Establish connection to Odoo XML-RPC API"""
    config = get_odoo_config()
    url = config.get('ODOO_URL', 'http://localhost:8069')
    db = config.get('ODOO_DB', 'hackathon')
    username = config.get('ODOO_USER')
    password = config.get('ODOO_PASSWORD')

    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        raise Exception("Odoo Authentication failed. Check credentials in .env.")
        
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return db, uid, password, models

@mcp.tool()
def odoo_list_partners(name_query: str = "") -> str:
    """
    Search for customers or partners in Odoo.
    
    Args:
        name_query: Partial name to search for.
    """
    try:
        db, uid, password, models = get_odoo_connection()
        domain = [('name', 'ilike', name_query)] if name_query else []
        partners = models.execute_kw(db, uid, password, 'res.partner', 'search_read', 
                                    [domain], {'fields': ['id', 'name', 'email', 'phone'], 'limit': 10})
        
        if not partners:
            return "No partners found matching your query."
            
        output = "📋 **Odoo Partners:**\n"
        for p in partners:
            output += f"- {p['name']} (ID: {p['id']}, Email: {p.get('email')})\n"
        return output
    except Exception as e:
        return f"❌ Error listing partners: {str(e)}"

@mcp.tool()
def odoo_create_invoice(partner_id: int, lines: list) -> str:
    """
    Creates a draft invoice in Odoo.
    
    Args:
        partner_id: The ID of the customer (partner).
        lines: A list of dicts with 'name', 'quantity', 'price_unit'.
    """
    try:
        db, uid, password, models = get_odoo_connection()
        
        # Create invoice lines
        invoice_line_ids = []
        for line in lines:
            invoice_line_ids.append((0, 0, {
                'name': line['name'],
                'quantity': line.get('quantity', 1),
                'price_unit': line['price_unit']
            }))
            
        # Create the invoice (account.move)
        invoice_id = models.execute_kw(db, uid, password, 'account.move', 'create', [{
            'partner_id': partner_id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_line_ids
        }])
        
        return f"✅ Draft invoice created successfully! ID: {invoice_id}. View it at {get_odoo_config().get('ODOO_URL')}/web#id={invoice_id}&model=account.move&view_type=form"
    except Exception as e:
        return f"❌ Error creating invoice: {str(e)}"

@mcp.tool()
def odoo_get_accounting_summary() -> str:
    """
    Retrieves a high-level summary of accounting (revenue and pending invoices).
    """
    try:
        db, uid, password, models = get_odoo_connection()
        
        # Count draft vs posted invoices
        draft_count = models.execute_kw(db, uid, password, 'account.move', 'search_count', [[('state', '=', 'draft'), ('move_type', '=', 'out_invoice')]])
        posted_count = models.execute_kw(db, uid, password, 'account.move', 'search_count', [[('state', '=', 'posted'), ('move_type', '=', 'out_invoice')]])
        
        # Calculate total revenue from posted invoices
        invoices = models.execute_kw(db, uid, password, 'account.move', 'search_read', 
                                    [[('state', '=', 'posted'), ('move_type', '=', 'out_invoice')]], 
                                    {'fields': ['amount_total']})
        total_revenue = sum(inv['amount_total'] for inv in invoices)
        
        return f'''📊 **Odoo Accounting Summary:**
- **Total Revenue (Confirmed)**: ${total_revenue:,.2f}
- **Posted Invoices**: {posted_count}
- **Draft Invoices**: {draft_count}
'''
    except Exception as e:
        return f"❌ Error getting summary: {str(e)}"

if __name__ == "__main__":
    mcp.run()
