import os
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_unread():
    session_path = './whatsapp_session'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(Path(session_path).resolve()), 
                headless=False
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://web.whatsapp.com')
            
            print("Looking for unread messages... (waiting for chat list to load)")
            try:
                page.wait_for_selector('#pane-side, div[aria-label*="list"], div[role="listbox"]', timeout=30000)
            except Exception as e:
                print(f"Timeout waiting for chat-list pane. Continuing anyway...")
                # In a real environment I'd save a screenshot, here I'll just try to proceed or fail gracefully
                page.screenshot(path="whatsapp_timeout_debug.png")
                raise e
            
            # Improved selectors for detecting unread chats/messages
            unread_indicators = page.query_selector_all('[aria-label*="unread"], [data-testid="icon-unread-count"], span[aria-label^="Unread message"], .unread-count')
            
            if unread_indicators:
                print(f"Found {len(unread_indicators)} potential unread indicators.")
                processed_contacts = set()
                for indicator in unread_indicators:
                    try:
                        # Go up to the chat row element
                        chat_row = page.evaluate_handle('el => el.closest("div[role=\'listitem\']")', indicator)
                        if not chat_row or chat_row.is_dispose():
                            continue
                            
                        chat_text = chat_row.evaluate('el => el.innerText')
                        # Attempt to extract contact name (usually the first part of the innerText)
                        lines = chat_text.split('\n')
                        contact_name = lines[0].strip() if lines else "Unknown Contact"
                        
                        if contact_name in processed_contacts:
                            continue
                        
                        processed_contacts.add(contact_name)
                        print(f"UNREAD_CONTACT: {contact_name}")
                        print(f"PREVIEW: {chat_text.replace('\n', ' | ')[:100]}...")
                    except Exception as e:
                        logging.debug(f"Skipping an unread indicator due to error: {e}")
            else:
                print("No unread messages found.")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_unread()
