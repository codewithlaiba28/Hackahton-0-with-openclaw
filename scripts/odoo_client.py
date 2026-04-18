import xmlrpc.client
import os
import logging
from retry_handler import with_retry

logger = logging.getLogger('OdooClient')

ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USER = os.getenv('ODOO_USER', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

class OdooClient:
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.uid = None
        self._authenticate()

    @with_retry(max_attempts=3)
    def _authenticate(self):
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, ODOO_USER, ODOO_PASSWORD, {})
        if not self.uid:
            raise Exception('Odoo authentication failed')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        logger.info(f'Authenticated to Odoo as uid={self.uid}')

    @with_retry(max_attempts=3)
    def get_invoices(self, state='draft', limit=20):
        return self.models.execute_kw(
            self.db, self.uid, ODOO_PASSWORD,
            'account.move', 'search_read',
            [[['move_type', '=', 'out_invoice'], ['state', '=', state]]],
            {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'state'], 'limit': limit}
        )

    @with_retry(max_attempts=3)
    def create_draft_invoice(self, partner_name: str, amount: float, description: str):
        if DRY_RUN:
            logger.info(f'[DRY RUN] Would create Odoo draft invoice: {partner_name} — ${amount}')
            return {'id': 'DRY_RUN', 'name': 'DRY_RUN_INVOICE'}
        partner_ids = self.models.execute_kw(
            self.db, self.uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['name', 'ilike', partner_name]]]
        )
        if not partner_ids:
            logger.warning(f'Partner not found: {partner_name}')
            return None
        invoice_id = self.models.execute_kw(
            self.db, self.uid, ODOO_PASSWORD,
            'account.move', 'create',
            [{
                'move_type': 'out_invoice',
                'partner_id': partner_ids[0],
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }]
        )
        logger.info(f'Created draft invoice ID: {invoice_id}')
        return invoice_id

    @with_retry(max_attempts=3)
    def get_expenses(self, limit=20):
        return self.models.execute_kw(
            self.db, self.uid, ODOO_PASSWORD,
            'account.move', 'search_read',
            [[['move_type', '=', 'in_invoice']]],
            {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'state'], 'limit': limit}
        )

if __name__ == '__main__':
    client = OdooClient()
    invoices = client.get_invoices()
    print(f'Found {len(invoices)} draft invoices')
    for inv in invoices:
        print(f' - {inv["name"]}: ${inv["amount_total"]}')