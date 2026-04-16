import os
import base64
from email.mime.text import MIMEText
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Initialize FastMCP server
mcp = FastMCP("Gmail_Dispatcher")

def get_gmail_service():
    """Helper to get a Gmail API service instance."""
    # Look in project root for token.json
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(root_dir, 'token.json')
    
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"token.json not found at {token_path}")
        
    creds = Credentials.from_authorized_user_file(token_path)
    return build('gmail', 'v1', credentials=creds)

@mcp.tool()
def send_gmail_message(to: str, subject: str, body: str) -> str:
    """
    Sends an email using the authorized Gmail account.
    
    Args:
        to: The recipient's email address.
        subject: The email subject line.
        body: The main content of the email.
    """
    try:
        service = get_gmail_service()
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message to base64url
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send via API
        send_result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"✅ Email sent successfully to {to}. Message ID: {send_result['id']}"
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

@mcp.tool()
def draft_gmail_message(to: str, subject: str, body: str) -> str:
    """
    Creates a draft in Gmail for review.
    
    Args:
        to: The recipient's email address.
        subject: The email subject line.
        body: The main content of the email.
    """
    try:
        service = get_gmail_service()
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()
        
        return f"📝 Draft created successfully for {to}. Draft ID: {draft['id']}"
    except Exception as e:
        return f"❌ Error creating draft: {str(e)}"

if __name__ == "__main__":
    mcp.run()
