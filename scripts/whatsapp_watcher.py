import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

# Add project root to sys.path to allow importing base_watcher
PROJECT_ROOT = Path(os.getcwd())
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from base_watcher import BaseWatcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WhatsAppWatcher')

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=60)
        self.session_path = Path(session_path)
        # Keywords that trigger an action file
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'order']
        self.processed_messages = set()

    def check_for_updates(self) -> list:
        new_messages = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path), 
                    headless=False
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com')
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector('#pane-side, div[aria-label*="list"], div[role="listbox"]', timeout=30000)
                except:
                    logger.warning("WhatsApp Web took too long to load or needs login. Continuing anyway...")

                # Find unread message badges or chats with unread indicators
                # Improved selectors for detecting unread chats/messages
                unread_indicators = page.query_selector_all('[aria-label*="unread"], [data-testid="icon-unread-count"], span[aria-label^="Unread message"]')
                
                # Use a set of unique chats to avoid processing the same chat multiple times in one run
                processed_in_this_run = set()

                for indicator in unread_indicators:
                    try:
                        # Go up to the chat row element - handle WhatsApp DOM changes
                        chat_row = page.evaluate_handle('el => el.closest("div[role=\'listitem\']") || el.closest("div[role=\'row\']") || el.parentElement.parentElement.parentElement.parentElement', indicator)
                        if not chat_row or chat_row.is_dispose():
                            continue
                            
                        chat_text = chat_row.evaluate('el => el.innerText')
                        if not chat_text:
                            continue
                        # Attempt to extract contact name (usually the first part of the innerText)
                        lines = chat_text.split('\n')
                        contact_name = lines[0].strip() if lines else "Unknown Contact"
                        
                        chat_id = chat_row.evaluate('el => el.getAttribute("data-testid")') or contact_name
                        
                        if chat_id in processed_in_this_run:
                            continue
                        
                        processed_in_this_run.add(chat_id)

                        if any(kw in chat_text.lower() for kw in self.keywords):
                            unique_id = f"{chat_id}_{datetime.now().strftime('%Y%m%d')}"
                            if unique_id not in self.processed_messages:
                                new_messages.append({
                                    'text': chat_text, 
                                    'raw': chat_text,
                                    'contact': contact_name
                                })
                                self.processed_messages.add(unique_id)
                                logger.info(f"Found unread chat from '{contact_name}' with relevant context.")
                    except Exception as e:
                        logger.debug(f"Skipping an unread indicator due to error: {e}")
                        continue
                
                browser.close()
        except Exception as e:
            logger.error(f"WhatsApp check error: {e}")
        return new_messages

    def create_action_file(self, message) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        content = f'''---
type: whatsapp_message
contact: {message.get('contact', 'Unknown')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Message Content
{message["raw"]}

## Suggested Actions
- [ ] Reply to WhatsApp message for '{message.get('contact', 'Unknown')}'
- [ ] Log request in CRM/Accounting
'''
        filepath = self.needs_action / f'WHATSAPP_{timestamp}.md'
        try:
            filepath.write_text(content)
            logger.info(f"WhatsApp action file created: {filepath.name}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to write WhatsApp action file: {e}")
            return None

if __name__ == '__main__':
    # Load env vars
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
    
    watcher = WhatsAppWatcher(vault_path, session_path)
    watcher.run()
