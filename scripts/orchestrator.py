import subprocess
import time
import logging
import os
import schedule
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Orchestrator')
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

WATCHERS = {
    'gmail_watcher': ['python', 'gmail_watcher.py'],
    'filesystem_watcher': ['python', 'filesystem_watcher.py'],
    'whatsapp_watcher': ['python', 'whatsapp_watcher.py'],
    'approval_watcher': ['python', 'approval_watcher.py'],
}

processes = {}

def start_watcher(name, cmd):
    logger.info(f'Starting {name}')
    proc = subprocess.Popen(cmd)
    processes[name] = proc

def check_and_restart():
    for name, cmd in WATCHERS.items():
        proc = processes.get(name)
        if proc is None or proc.poll() is not None:
            logger.warning(f'{name} crashed — restarting')
            start_watcher(name, cmd)

def trigger_claude_processing():
    items = list((VAULT_PATH / 'Needs_Action').glob('*.md'))
    if items:
        logger.info(f'Triggering Claude for {len(items)} items')
        subprocess.run([
            'python', 'ralph_loop.py',
            'Process all files in /Needs_Action/. For each: create a Plan.md in /Plans/, '
            'create approval files in /Pending_Approval/ for sensitive actions, '
            'update Dashboard.md. Move processed files to /Done/.'
        ])

def run_ceo_briefing():
    logger.info('Running weekly CEO Briefing')
    subprocess.run(['python', 'ceo_briefing_generator.py'])

def run_accounting_sync():
    logger.info('Running Odoo accounting sync')
    subprocess.run([
        'python', 'ralph_loop.py',
        'Sync accounting data: read Accounting/Current_Month.md, '
        'connect to Odoo and fetch invoices and expenses, '
        'update the accounting file, flag anything over $500 for approval.'
    ])

def main():
    logger.info('Gold Tier Orchestrator started')

    for name, cmd in WATCHERS.items():
        start_watcher(name, cmd)

    # Scheduling
    schedule.every(5).minutes.do(trigger_claude_processing)
    schedule.every().sunday.at('22:00').do(run_ceo_briefing)
    schedule.every().day.at('08:00').do(run_accounting_sync)

    while True:
        check_and_restart()
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()
