import os
import sys
import logging
import base64
import json
from pathlib import Path
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('EmailSender')

# Scopes required for sending
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']

def send_email(to: str, subject: str, body: str):
    workspace_root = Path(os.getcwd())
    token_path = workspace_root / "token.json"
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    if dry_run:
        logger.info(f"[DRY RUN] Sending email to '{to}':\nSubject: {subject}\nBody: {body}")
        return True

    if not token_path.exists():
        logger.error(f"Gmail token not found at {token_path}. Please run gmail_watcher.py first to authenticate.")
        return False

    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.error("Invalid credentials. Re-authentication required.")
                return False

        service = build('gmail', 'v1', credentials=creds)

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        send_result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        logger.info(f"Email sent successfully. Message ID: {send_result['id']}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python gmail_sender.py <to> <subject> <body>")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subj = sys.argv[2]
    content = sys.argv[3]
    
    success = send_email(to_email, subj, content)
    if not success:
        sys.exit(1)
