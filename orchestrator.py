import subprocess
import time
import logging
import os
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Orchestrator')

# Define project root and vault path based on execution context or environment variables
PROJECT_ROOT = Path(os.getcwd())
VAULT_PATH = PROJECT_ROOT / os.getenv('VAULT_PATH', 'AI_Employee_Vault')

WATCHERS = {
    'gmail_watcher': ['python', str(PROJECT_ROOT / 'gmail_watcher.py')],
    'filesystem_watcher': ['python', str(PROJECT_ROOT / 'filesystem_watcher.py')],
    'whatsapp_watcher': ['python', str(PROJECT_ROOT / 'scripts' / 'whatsapp_watcher.py')],
    'linkedin_watcher': ['python', str(PROJECT_ROOT / 'scripts' / 'linkedin_watcher.py')],
    'approval_watcher': ['python', str(PROJECT_ROOT / 'scripts' / 'approval_watcher.py')],
}

processes = {}

def start_watcher(name: str, cmd: list):
    logger.info(f'Starting watcher: {name} with command: {" ".join(cmd)}')
    try:
        # Using Popen to start processes asynchronously
        # Note: Direct execution of Python scripts like this assumes they are well-behaved background processes.
        # For production, a more robust process manager like PM2 or systemd would be recommended.
        proc = subprocess.Popen(cmd)
        processes[name] = proc
        logger.info(f'{name} started with PID: {proc.pid}')
    except FileNotFoundError:
        logger.error(f"Error: The script '{cmd[1]}' was not found. Ensure it's in the correct path.")
    except Exception as e:
        logger.error(f"Failed to start watcher {name}: {e}")

def check_and_restart():
    for name, cmd in WATCHERS.items():
        proc = processes.get(name)
        # Check if process is not running (None) or has terminated (poll() returns non-None)
        if proc is None or proc.poll() is not None:
            logger.warning(f'{name} is not running (PID: {proc.pid if proc else "N/A"}). Attempting to restart...')
            start_watcher(name, cmd)

def trigger_claude_processing():
    # This function assumes 'claude' CLI is in the PATH and configured to use the vault
    needs_action_path = VAULT_PATH / 'Needs_Action'
    if not needs_action_path.exists():
        logger.debug(f"Needs_Action folder not found at {needs_action_path}, skipping Claude trigger.")
        return

    items = list(needs_action_path.glob('*.md'))
    if items:
        logger.info(f'Found {len(items)} items in Needs_Action. Triggering Claude for processing...')
        # The --cwd flag is crucial for Claude to operate within the correct directory context
        claude_command = [
            'claude', '-p',
            'Read all files in /Needs_Action/, create a Plan.md in /Plans/ for each, '
            'create approval files in /Pending_Approval/ for any sensitive actions, '
            'then update Dashboard.md with current status.',
            '--cwd', str(VAULT_PATH) # Ensure Claude operates within the vault directory
        ]
        try:
            # Use subprocess.run for a blocking call that waits for Claude to finish its processing prompt
            # Added timeout to prevent indefinite hanging if Claude gets stuck. Adjust as needed.
            result = subprocess.run(claude_command, capture_output=True, text=True, check=True, timeout=300) 
            logger.info("Claude processing initiated successfully.")
            logger.debug(f"Claude output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Claude stderr: {result.stderr}")
        except FileNotFoundError:
            logger.error("Claude CLI command not found. Ensure 'claude' is installed and in your PATH.")
        except subprocess.TimeoutExpired:
            logger.error("Claude processing timed out.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Claude processing failed with error code {e.returncode}: {e.stderr}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during Claude processing: {e}")
    else:
        logger.debug("No items found in Needs_Action. Skipping Claude trigger.")


def main():
    logger.info(f'Orchestrator started. Working directory: {PROJECT_ROOT}')
    
    # Ensure main vault directories exist
    VAULT_PATH.mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Needs_Action').mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Plans').mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Pending_Approval').mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Approved').mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Rejected').mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Done').mkdir(parents=True, exist_ok=True)
    (VAULT_PATH / 'Logs').mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / 'scripts').mkdir(parents=True, exist_ok=True) # Ensure scripts folder exists

    # Start all defined watchers
    for name, cmd in WATCHERS.items():
        start_watcher(name, cmd)

    last_claude_run = 0
    # Claude processing interval: run every 5 minutes (300 seconds) if there are items
    # Consider making this more dynamic based on queue activity or a separate trigger
    CLAUDE_INTERVAL = 300 

    logger.info(f"Starting main loop. Claude processing will be triggered roughly every {CLAUDE_INTERVAL} seconds.")
    while True:
        check_and_restart() # Ensure all watchers are running
        now = time.time()
        
        # Trigger Claude processing periodically if there are items in Needs_Action
        if now - last_claude_run > CLAUDE_INTERVAL:
            trigger_claude_processing()
            last_claude_run = now
            
        time.sleep(60) # Sleep for 60 seconds before next loop iteration

if __name__ == '__main__':
    main()
