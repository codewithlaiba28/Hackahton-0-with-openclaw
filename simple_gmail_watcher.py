#!/usr/bin/env python3
"""
Simple Gmail Watcher - Live Email Fetching
This script connects to your Gmail account to fetch unread emails
and creates action items in markdown files.
"""

import time
import logging
from pathlib import Path
from datetime import datetime
import os # For os.getenv

# Gmail API imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Base watcher class (redefined here for self-containment)
class BaseWatcher:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure needed directories exist
        self.needs_action.mkdir(exist_ok=True)

    def create_action_file(self, item_data) -> Path:
        """Creates a .md file in Needs_Action folder for processing."""
        raise NotImplementedError("Subclasses must implement create_action_file")

    def run(self):
        """Main watcher loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error in check_for_updates loop: {e}')
            time.sleep(self.check_interval)

class SimpleGmailWatcher(BaseWatcher):
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    def __init__(self, vault_path: str, check_interval: int = 300):
        super().__init__(vault_path, check_interval=check_interval)
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set() # To keep track of emails already processed
        self._initialize_processed_ids() # Load existing processed IDs if any

    def _get_credentials(self):
        """Gets valid user credentials from storage or prompts for new authorization."""
        creds = None
        if Path(self.TOKEN_FILE).exists():
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Failed to refresh token: {e}. Re-authenticating.")
                    creds = self._authenticate_user()
            else:
                creds = self._authenticate_user()
            
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return creds

    def _authenticate_user(self):
        """Handles the OAuth 2.0 authentication flow."""
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        if not Path(self.CREDENTIALS_FILE).exists():
            raise FileNotFoundError(f"Credentials file '{self.CREDENTIALS_FILE}' not found. Please download it from Google Cloud Console and place it in the same directory as this script.")

        flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
        creds = flow.run_local_server(port=0)
        return creds

    def _initialize_processed_ids(self):
        """
        Loads existing processed email IDs to avoid reprocessing.
        For simplicity in this example, IDs are reset each run.
        A robust solution would save/load processed IDs from a file.
        """
        self.processed_ids = set()
        self.logger.info("Initialized processed email IDs (session-based).")

    def check_for_updates(self) -> list:
        """Fetches unread and important emails from Gmail."""
        try:
            results = self.service.users().messages().list(
                userId='me', 
                q='is:unread in:inbox',
                maxResults=10 # Fetch up to 10 unread messages
            ).execute()
            
            messages = results.get('messages', [])
            
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]
            
            if not new_messages:
                self.logger.info("No new unread emails found.")
                return []
            
            self.logger.info(f"Found {len(new_messages)} new unread emails.")
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'An API error occurred: {error}')
            return []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while fetching emails: {e}")
            return []

    def get_email_details(self, message_id):
        """Fetches full email details for a given message ID."""
        try:
            msg = self.service.users().messages().get(userId='me', id=message_id).execute()
            return msg
        except HttpError as error:
            self.logger.error(f'An API error occurred while fetching message {message_id}: {error}')
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred fetching details for {message_id}: {e}")
            return None

    def create_action_file(self, message_data) -> Path:
        """Creates a markdown file for the email, extracting relevant info."""
        message_id = message_data['id']
        
        msg_details = self.get_email_details(message_id)
        if not msg_details:
            self.logger.error(f"Could not retrieve details for message ID: {message_id}")
            return None
            
        headers = {h['name'].lower(): h['value'] for h in msg_details['payload']['headers']}
        
        subject = headers.get('subject', 'No Subject')
        sender = headers.get('from', 'Unknown Sender')
        
        try:
            # Basic decoding for subject and sender
            decoded_subject, encoding = decode_header(subject)[0]
            if encoding and encoding != 'unknown':
                subject = decoded_subject.decode(encoding, errors='ignore')
            else:
                subject = str(decoded_subject)
        except Exception:
            pass

        try:
            decoded_sender, encoding = decode_header(sender)[0]
            if encoding and encoding != 'unknown':
                sender = decoded_sender.decode(encoding, errors='ignore')
            else:
                sender = str(decoded_sender)
        except Exception:
            pass

        snippet = msg_details.get('snippet', 'No content snippet available.')

        content = f"""---
type: email
id: {message_id}
from: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content Snippet

{snippet}

## Suggested Actions
- [ ] Process this email
- [ ] Reply to sender if needed
- [ ] Archive email after processing
"""
        
        filename = f"EMAIL_{message_id}.md"
        filepath = self.needs_action / filename
        
        try:
            filepath.write_text(content)
            self.processed_ids.add(message_id)
            self.logger.info(f"Created action file for email {message_id}: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to write action file {filepath}: {e}")
            return None

    def run(self):
        """Main watcher loop"""
        self.logger.info(f"Starting {self.__class__.__name__}")
        
        while True:
            try:
                emails = self.check_for_updates()
                for email_data in emails:
                    action_file = self.create_action_file(email_data)
                    if action_file:
                        try:
                            self.service.users().messages().modify(userId='me', id=email_data['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                            self.logger.info(f"Marked email {email_data['id']} as read.")
                        except Exception as e:
                            self.logger.error(f"Failed to mark email {email_data['id']} as read: {e}")
                    
                total_files = len(list(self.needs_action.glob("EMAIL_*.md")))
                self.logger.info(f"Total pending email action files: {total_files}")
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
            
            time.sleep(self.check_interval)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('gmail_watcher.log'),
            logging.StreamHandler()
        ]
    )
    
    vault_path = "."
    watcher = SimpleGmailWatcher(vault_path, check_interval=120) # Check every 2 minutes
    watcher.run()
