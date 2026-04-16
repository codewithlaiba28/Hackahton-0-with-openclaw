# /mnt/c/Code-journy/Quator-4/Hackahton-0-with-openclaw/gmail_watcher.py

import time
import logging
from pathlib import Path
import os.path
import pickle
import mimetypes

# Google API imports
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define base path to the workspace
WORKSPACE_BASE_PATH = Path(os.getcwd())

# CREDENTIALS_PATH and TOKEN_PATH are now explicitly defined using the workspace path
CREDENTIALS_PATH = WORKSPACE_BASE_PATH / "credentials.json"
TOKEN_PATH = WORKSPACE_BASE_PATH / "token.json"
LOG_DIR = WORKSPACE_BASE_PATH / "Logs"
NEEDS_ACTION_DIR = WORKSPACE_BASE_PATH / "Needs_Action"
PROCESSED_EMAILS_LOG = LOG_DIR / "processed_emails.log" 

# --- Ensure directories exist ---
NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Ensure the processed emails log file exists
if not PROCESSED_EMAILS_LOG.exists():
    PROCESSED_EMAILS_LOG.touch()


from base_watcher import BaseWatcher

# --- Google API Authentication ---
# If modifying these scopes, delete the file token.json. (Added by AI)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# --- Load processed email IDs ---
def load_processed_emails():
    processed_ids = set()
    if PROCESSED_EMAILS_LOG.exists():
        with open(PROCESSED_EMAILS_LOG, "r") as f:
            for line in f:
                processed_ids.add(line.strip())
    return processed_ids

# --- Save processed email ID ---
def save_processed_email(email_id):
    with open(PROCESSED_EMAILS_LOG, "a") as f:
        f.write(f"{email_id}\n")

# --- Gmail Watcher Implementation ---
class GmailWatcher(BaseWatcher):
    def __init__(self, credentials_file_path: Path, token_file_path: Path, vault_path: Path):
        super().__init__(vault_path, check_interval=120) # Check every 120 seconds (2 minutes)
        self.creds = None
        self.credentials_file_path = credentials_file_path
        self.token_file_path = token_file_path
        self.service = None
        self.processed_emails = load_processed_emails()

    def authenticate_gmail(self):
        if self.token_file_path.exists():
            import json
            from google.oauth2.credentials import Credentials
            self.creds = Credentials.from_authorized_user_file(str(self.token_file_path), SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Error refreshing token: {e}")
                    # If refresh fails, we need to re-authenticate
                    self.creds = None
            else:
                # Check if credentials file exists using the explicit path
                if not self.credentials_file_path.exists():
                    # Ensure the error message reflects the exact path being checked
                    error_msg = f"Credentials file not found at {self.credentials_file_path}. Please download it from Google Cloud Console and place it there."
                    self.logger.error(error_msg)
                    raise FileNotFoundError(error_msg)

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file_path), SCOPES) # Ensure path is string
                    # Run local server flow - this will open a browser for authentication
                    # The port=0 tells it to find an available port
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.logger.error(f"Error during OAuth flow: {e}", exc_info=True)
                    raise

            # Save the credentials for the next run to the explicit token path
            with open(self.token_file_path, 'w') as token:
                token.write(self.creds.to_json())
                self.logger.info(f"Token saved to {self.token_file_path}")

        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
            self.logger.info("Successfully authenticated and built Gmail service.")
        except HttpError as error:
            self.logger.error(f"An HttpError occurred when building service: {error}", exc_info=True)
            self.creds = None # Clear creds if service build fails
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during service build: {e}", exc_info=True)
            raise

    def get_email_snippet(self, message_id):
        try:
            msg = self.service.users().messages().get(userId='me', id=message_id, format='metadata', metadataHeaders=['Subject', 'From', 'Date']).execute()
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            snippet = msg.get('snippet', 'No snippet available.')
            return headers.get('From', 'Unknown Sender'), headers.get('Subject', 'No Subject'), snippet
        except HttpError as error:
            self.logger.error(f"An HttpError occurred when getting email snippet for {message_id}: {error}", exc_info=True)
            return None, None, None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred getting email snippet for {message_id}: {e}", exc_info=True)
            return None, None, None

    def check_for_updates(self) -> list:
        if not self.service:
            try:
                self.authenticate_gmail()
            except Exception as e:
                self.logger.error(f"Failed to authenticate Gmail: {e}. Will retry later.")
                return [] # Return empty if authentication fails

        try:
            # Query for unread and important emails from the last 7 days (adjust query as needed)
            # The query 'in:unread,important' should target the desired emails.
            # We might need to add a date filter if we don't want to re-process old unread emails.
            # For simplicity, let's initially fetch unread/important and rely on processed_emails log.
            results = self.service.users().messages().list(userId='me', labelIds=['UNREAD', 'IMPORTANT'], maxResults=10).execute()
            messages = results.get('messages', [])
            
            new_messages_to_process = []
            for message in messages:
                msg_id = message['id']
                if msg_id not in self.processed_emails:
                    new_messages_to_process.append(msg_id)
                    self.processed_emails.add(msg_id) # Mark as processed immediately to avoid duplicates if script restarts
                    save_processed_email(msg_id) # Save to log file

            self.logger.info(f"Found {len(new_messages_to_process)} new unread/important emails to process.")
            return new_messages_to_process

        except HttpError as error:
            self.logger.error(f"An HttpError occurred when listing messages: {error}", exc_info=True)
            # Handle specific errors like token expiry if needed
            if error.resp.status == 401:
                self.logger.warning("Token might be expired. Will attempt re-authentication.")
                self.creds = None # Force re-authentication on next check
            return []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred when listing messages: {e}", exc_info=True)
            return []

    def create_action_file(self, message_id) -> Path:
        from_addr, subject, snippet = self.get_email_snippet(message_id)

        if from_addr is None: # Skip if there was an error fetching details
            self.logger.warning(f"Could not fetch details for email {message_id}. Skipping file creation.")
            return None

        from datetime import datetime
        timestamp = datetime.now().isoformat()

        # Building the content string line by line
        content_lines = []
        content_lines.append("---")
        content_lines.append(f"type: email")
        content_lines.append(f"from: {from_addr}")
        content_lines.append(f"subject: {subject}")
        content_lines.append(f"received: {timestamp}")
        content_lines.append(f"priority: high")
        content_lines.append(f"status: pending")
        content_lines.append("---")
        content_lines.append("\n## Email Content")
        content_lines.append(snippet)
        content_lines.append("\n## Suggested Actions")
        content_lines.append("- [ ] Review and reply")
        content_lines.append("- [ ] Forward if needed")
        content_lines.append("- [ ] Archive after processing")
        
        content = "\n".join(content_lines)

        filepath = NEEDS_ACTION_DIR / f'EMAIL_{message_id}.md'
        try:
            filepath.write_text(content)
            self.logger.info(f"Created action file: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error writing action file {filepath}: {e}", exc_info=True)
            return None

    def run(self):
        self.logger.info("Starting GmailWatcher.")
        if not self.service: # Try initial authentication
            try:
                self.authenticate_gmail()
            except Exception as e:
                self.logger.error(f"Failed to authenticate Gmail on startup: {e}. Watcher may not function correctly.")
                # Proceed, but expect issues if service is not available.

        while True:
            try:
                new_email_ids = self.check_for_updates()
                for email_id in new_email_ids:
                    self.create_action_file(email_id)

                # Log summary of current state
                self.logger.info(f"Current processed email count: {len(self.processed_emails)}")

            except Exception as e:
                self.logger.error(f"An error occurred during the watcher loop: {e}", exc_info=True)
            
            time.sleep(self.check_interval)

if __name__ == '__main__':
    # Use the explicit Path objects for credentials and token
    # Ensure the vault_path is correctly passed as a string
    watcher = GmailWatcher(
        credentials_file_path=CREDENTIALS_PATH,
        token_file_path=TOKEN_PATH,
        vault_path=str(WORKSPACE_BASE_PATH)
    )
    
    try:
        watcher.run()
    except FileNotFoundError as fnf_error:
        logging.error(f"Initialization error: {fnf_error}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
