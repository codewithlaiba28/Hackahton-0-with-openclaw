import os
import sys
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WhatsAppReply')

def reply_to_whatsapp(contact_name: str, message_text: str):
    session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    if dry_run:
        logger.info(f"[DRY RUN] Replying to WhatsApp contact '{contact_name}':\n{message_text}")
        return True

    try:
        logger.info(f"Starting Playwright to reply to {contact_name}...")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(Path(session_path).resolve()), 
                headless=False
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://web.whatsapp.com', wait_until="networkidle")
            
            # Wait for chat list (longer timeout)
            logger.info("Waiting for WhatsApp Web to load...")
            try:
                page.wait_for_selector('#pane-side, div[aria-label*="list"], div[role="listbox"]', timeout=60000)
            except:
                logger.warning("WhatsApp Web too long to load list. Continuing anyway...")

            # Search for the contact
            logger.info(f"Searching for contact: {contact_name}")
            try:
                # Use standard, more robust search strategies instead of CSS
                search_box = page.get_by_placeholder("Search or start a new chat")
                if not search_box.is_visible():
                    search_box = page.get_by_title("Search input textbox", exact=True)
                
                search_box.click()
                search_box.fill("") # Clear first
                search_box.type(contact_name)
                time.sleep(5) # Wait for search results to filter
                
                # Try multiple ways to find the contact in search results
                selectors = [
                    f'span[title="{contact_name}"]',                               # Exact title match
                    f'div[role="listitem"] span:has-text("{contact_name}")',       # Within list item
                    f'#pane-side span:has-text("{contact_name}")'                  # Within chat list pane
                ]
                
                contact_found = False
                for selector in selectors:
                    try:
                        if page.query_selector(selector):
                            logger.info(f"Contact found with selector: {selector}")
                            page.click(selector)
                            contact_found = True
                            break
                    except:
                        continue
                
                if not contact_found:
                    logger.error(f"Contact '{contact_name}' not found in search results after trying multiple selectors.")
                    # Take a screenshot for debugging if possible (if we had a tool for it)
                    browser.close()
                    return False
            except Exception as e:
                logger.error(f"Error during contact search: {e}")
                browser.close()
                return False
            
            # Wait for chat input to appear
            input_selector = 'footer div[contenteditable="true"]'
            page.wait_for_selector(input_selector, timeout=15000)
            
            # Type message
            logger.info("Typing message...")
            page.fill(input_selector, message_text)
            time.sleep(1)
            
            # Press Enter to send
            page.keyboard.press('Enter')
            logger.info("Enter pressed. Waiting for confirmation...")
            
            # Wait for the "Sent" status or just a bit of time to ensure it leaves the outbox
            time.sleep(5) 
            
            browser.close()
            logger.info(f"Reply to {contact_name} finished successfully.")
            return True

    except Exception as e:
        logger.error(f"Failed to reply to WhatsApp: {e}")
        if 'browser' in locals(): browser.close()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python whatsapp_reply.py \"Contact Name\" \"Message\"")
        sys.exit(1)
    
    success = reply_to_whatsapp(sys.argv[1], sys.argv[2])
    if not success:
        sys.exit(1)
