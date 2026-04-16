import subprocess, json, logging, os, time, sys
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ApprovalWatcher')

# Use the project's root directory for vault and session paths
PROJECT_ROOT = Path(os.getcwd())
VAULT_PATH = PROJECT_ROOT / os.getenv('VAULT_PATH', 'AI_Employee_Vault')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

class ApprovalHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('ApprovalWatcher')
        self.approved_folder = VAULT_PATH / 'Approved'
        self.done_folder = VAULT_PATH / 'Done'
        self.logger.info(f"Monitoring approvals in: {self.approved_folder}")

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path).resolve()
        approved_folder_resolved = self.approved_folder.resolve()
        
        self.logger.info(f"File created: {filepath}. Checking if in {approved_folder_resolved}")
        
        # Process only markdown files appearing in the Approved folder
        if filepath.suffix == '.md' and (filepath.parent == approved_folder_resolved or str(filepath.parent) == str(approved_folder_resolved)):
            self.logger.info(f'Approval match! Processing: {filepath.name}')
            self.process_approval(filepath)
        else:
            self.logger.debug(f"Ignoring file: {filepath.name} in {filepath.parent}")

    def process_approval(self, filepath: Path):
        try:
            content = filepath.read_text()
            action_type = self.extract_frontmatter_value(content, 'action')
            self.logger.info(f"Processing action: '{action_type}' for file: {filepath.name}")

            if action_type == 'email_send':
                to_addr = self.extract_frontmatter_value(content, 'to')
                subject = self.extract_frontmatter_value(content, 'subject')
                body = self.extract_post_content(content) # Reuse logic to extract body text
                
                if to_addr and subject and body:
                    if DRY_RUN:
                        self.logger.info(f'[DRY RUN] Would send email to {to_addr}: {subject}')
                        self.log_action(action_type, filepath.name, 'dry_run_executed')
                    else:
                        gmail_sender_path = PROJECT_ROOT / 'scripts' / 'gmail_sender.py'
                        cmd = ['python', str(gmail_sender_path), to_addr, subject, body]
                        self.logger.info(f"Executing command: {' '.join(cmd)}")
                        try:
                            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                            self.logger.info(f"Email send stdout: {result.stdout}")
                            self.log_action(action_type, filepath.name, 'executed')
                        except subprocess.CalledProcessError as e:
                            self.logger.error(f"Gmail sender script failed: {e.stderr}")
                            self.log_action(action_type, filepath.name, 'failed')
                else:
                    self.logger.warning(f"Missing email details in {filepath.name}")
                    self.log_action(action_type, filepath.name, 'missing_details')
            
            elif action_type == 'whatsapp_reply':
                contact = self.extract_frontmatter_value(content, 'contact')
                reply_text = self.extract_post_content(content)
                
                if contact and reply_text:
                    if DRY_RUN:
                        self.logger.info(f'[DRY RUN] Would reply to WhatsApp contact {contact}')
                        self.log_action(action_type, filepath.name, 'dry_run_executed')
                    else:
                        whatsapp_reply_path = PROJECT_ROOT / 'scripts' / 'whatsapp_reply.py'
                        cmd = ['python', str(whatsapp_reply_path), contact, reply_text]
                        self.logger.info(f"Executing command: {' '.join(cmd)}")
                        try:
                            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                            self.logger.info(f"WhatsApp reply stdout: {result.stdout}")
                            self.log_action(action_type, filepath.name, 'executed')
                        except subprocess.CalledProcessError as e:
                            self.logger.error(f"WhatsApp reply script failed: {e.stderr}")
                            self.log_action(action_type, filepath.name, 'failed')
                else:
                    self.logger.warning(f"Missing WhatsApp reply details in {filepath.name}")
                    self.log_action(action_type, filepath.name, 'missing_details')
            
            elif action_type == 'linkedin_post':
                post_content = self.extract_post_content(content)
                if post_content:
                    if DRY_RUN:
                        self.logger.info(f'[DRY RUN] Would post to LinkedIn: {post_content[:80]}...')
                        self.log_action(action_type, filepath.name, 'dry_run_executed')
                    else:
                        # Ensure linkedin_poster.py is at the project root
                        linkedin_poster_path = PROJECT_ROOT / 'scripts' / 'linkedin_poster.py'
                        # Pass the filepath instead of the content string
                        cmd = ['python', str(linkedin_poster_path), str(filepath)]
                        self.logger.info(f"Executing command: {' '.join(cmd)}")
                        try:
                            # Use check=True to raise an exception if the command fails
                            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                            self.logger.info(f"LinkedIn post stdout: {result.stdout}")
                            self.logger.info(f"LinkedIn post stderr: {result.stderr}")
                            self.log_action(action_type, filepath.name, 'executed')
                        except subprocess.CalledProcessError as e:
                            self.logger.error(f"LinkedIn posting script failed with exit code {e.returncode}")
                            self.logger.error(f"Error output: {e.stderr}")
                            self.log_action(action_type, filepath.name, 'failed')
                        except FileNotFoundError:
                            self.logger.error(f"LinkedIn poster script not found at {linkedin_poster_path}")
                            self.log_action(action_type, filepath.name, 'script_not_found')
                else:
                    self.logger.warning(f"No content found for LinkedIn post in {filepath.name}")
                    self.log_action(action_type, filepath.name, 'no_content')

            elif action_type == 'payment':
                self.logger.warning(f'Payment approval detected — payments require manual handling. File: {filepath.name}')
                self.log_action(action_type, filepath.name, 'manual_required')
            
            else:
                self.logger.warning(f"Unknown action type '{action_type}' in {filepath.name}")
                self.log_action(action_type, filepath.name, 'unknown_action_type')

            # Move the processed file to the Done folder
            final_done_path = self.done_folder / filepath.name
            filepath.rename(final_done_path)
            self.logger.info(f'Moved processed approval file to Done: {filepath.name}')

        except FileNotFoundError:
            self.logger.error(f"Approval file not found: {filepath}. It may have been moved already.")
        except Exception as e:
            self.logger.error(f"Error processing approval file {filepath.name}: {e}")
            # Optionally move to a temporary error folder or log more details

    def extract_frontmatter_value(self, content: str, key: str) -> str:
        for line in content.split('\n'):
            if line.startswith(f'{key}:'):
                return line.split(':', 1)[1].strip()
        return ''

    def extract_post_content(self, content: str) -> str:
        lines = content.split('\n')
        in_content = False
        result = []
        for line in lines:
            # Look for common keys indicating the start of content for posting
            if '**Content**:' in line or 'content:' in line.lower() or '## content' in line.lower(): 
                in_content = True
                continue # Skip the header line itself
            if in_content and line.startswith('##'): # Stop if we hit another section header
                break
            if in_content:
                result.append(line)
        return '\n'.join(result).strip()

    def log_action(self, action_type: str, filename: str, result: str):
        log_file = VAULT_PATH / 'Logs' / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'approval_watcher',
            'file': filename,
            'result': result,
            'dry_run': DRY_RUN
        }
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                self.logger.error(f"Could not decode JSON from log file: {log_file}")
                logs = [] # Start fresh if log is corrupt
        
        logs.append(log_entry)
        
        try:
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to write to log file {log_file}: {e}")


if __name__ == '__main__':
    # Ensure directories exist before starting the observer
    approval_folder = VAULT_PATH / 'Approved'
    done_folder = VAULT_PATH / 'Done'
    approval_folder.mkdir(parents=True, exist_ok=True)
    done_folder.mkdir(parents=True, exist_ok=True)

    handler = ApprovalHandler()
    observer = Observer()
    # Recursive=False means it only watches the top level of the approved_folder
    observer.schedule(handler, str(approval_folder), recursive=False) 
    
    observer.start()
    logger.info(f'Approval watcher started. Monitoring {approval_folder}')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Approval watcher stopped.")
    observer.join()
