import xmlrpc.client
import os
from pathlib import Path

def test_odoo_connection():
    # Load .env
    env_path = Path('.env')
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

    url = os.getenv('ODOO_URL', 'http://localhost:8069')
    db = os.getenv('ODOO_DB', 'odoo')
    username = os.getenv('ODOO_USER')
    password = os.getenv('ODOO_PASSWORD')

    print(f"Connecting to Odoo at {url} (DB: {db}, User: {username})...")

    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        version = common.version()
        print(f"Odoo Version: {version.get('server_version')}")

        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"✅ Successfully authenticated! UID: {uid}")
            
            # Check for Invoicing module (account.move)
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            has_invoicing = models.execute_kw(db, uid, password, 'ir.model', 'search_count', [[['model', '=', 'account.move']]])
            if has_invoicing:
                print("✅ Invoicing (account.move) module found.")
            else:
                print("⚠️ Invoicing module NOT found. Please install 'Invoicing' in Odoo Apps.")
            
            return True
        else:
            print("❌ Authentication failed. Please check your credentials in .env.")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_odoo_connection()
