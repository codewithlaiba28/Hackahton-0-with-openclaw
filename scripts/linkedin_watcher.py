import os
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

# Add project root to sys.path to allow importing base_watcher from within scripts/
PROJECT_ROOT = Path(os.getcwd())
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from base_watcher import BaseWatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LinkedInWatcher')

class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=60) # Check every 60 seconds
        self.session_path = Path(session_path)
        self.keywords = ['job', 'opportunity', 'hiring', 'post', 'article', 'insight'] # Keywords to monitor
        self.processed_notifications = set() # To avoid reprocessing

    def check_for_updates(self) -> list:
        messages = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path), headless=True
                )
                page = browser.new_page() if not browser.pages else browser.pages[0]
                page.goto('https://www.linkedin.com/feed/')
                # Wait for the main feed or a known element to ensure the page is loaded
                page.wait_for_selector('section.core-rail', timeout=20000) 
                logger.info("LinkedIn feed loaded. Checking for notifications.")

                # This is a simplified check. LinkedIn's notification system is complex and dynamic.
                # A more robust solution would involve inspecting network requests or using specific notification selectors if available.
                # For this example, we'll look for common notification indicators or recent feed activity.
                
                # Placeholder: Check for unread notification badges or recent relevant feed items.
                # This requires more intricate selectors and logic for actual production use.
                # For now, let's simulate finding potential items to process.
                
                # Example: Look for elements that might indicate new activity.
                # These selectors are highly subject to change by LinkedIn.
                potential_items = page.query_selector_all('[data-test-live-stream-card], [data-test-article-content-viewer]')

                for item in potential_items:
                    text_content = item.inner_text().lower()
                    raw_text = item.inner_text()
                    
                    if any(kw in text_content for kw in self.keywords):
                        unique_key = text_content[:150] # Create a unique key for this notification
                        if unique_key not in self.processed_notifications:
                            messages.append({'text': text_content, 'raw': raw_text})
                            self.processed_notifications.add(unique_key)
                            logger.info(f"Found potential item matching keywords: {unique_key[:50]}...")

                browser.close()
        except Exception as e:
            logger.error(f'LinkedIn watch error: {e}')
        return messages

    def create_action_file(self, message) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a markdown file in Needs_Action for potential follow-up
        content = f'''---
type: linkedin_activity
received: {datetime.now().isoformat()}
priority: medium
status: pending
keywords_matched: true
---

## LinkedIn Activity Preview
{message["raw"]}

## Suggested Actions
- [ ] Review LinkedIn activity/notification
- [ ] Draft a response or relevant post (REQUIRES APPROVAL if sensitive)
'''
        filepath = self.needs_action / f'LINKEDIN_{timestamp}.md'
        try:
            filepath.write_text(content)
            self.logger.info(f'LinkedIn action file created: {filepath.name}')
        except Exception as e:
            self.logger.error(f"Failed to write action file {filepath.name}: {e}")
        return filepath

if __name__ == '__main__':
    logger.info("Starting LinkedIn Watcher...")
    watcher = LinkedInWatcher(
        vault_path=os.getenv('VAULT_PATH', './AI_Employee_Vault'),
        session_path=os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session') # Ensure this path is correct for Playwright sessions
    )
    watcher.run()
