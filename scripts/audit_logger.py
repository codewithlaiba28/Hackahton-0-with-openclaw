import json
import logging
import os
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

class AuditLogger:
    def __init__(self):
        self.log_dir = VAULT_PATH / 'Logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, action_type: str, actor: str, target: str,
            parameters: dict, approval_status: str, result: str,
            approved_by: str = 'system'):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'parameters': parameters,
            'approval_status': approval_status,
            'approved_by': approved_by,
            'result': result
        }
        log_file = self.log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except Exception:
                logs = []
        logs.append(entry)
        log_file.write_text(json.dumps(logs, indent=2))
        logging.getLogger('AuditLogger').info(f'[{action_type}] {actor} → {target}: {result}')

audit = AuditLogger()