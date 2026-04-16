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
logger = logging.getLogger('LinkedInPoster')

def post_to_linkedin(content_file_path: str):
    session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    if not Path(content_file_path).exists():
        logger.error(f"Content file not found: {content_file_path}")
        return False

    try:
        file_content = Path(content_file_path).read_text()
        # Simplified extraction logic: assume everything after '## Content' or 'content:' is the post
        post_text = ""
        lines = file_content.split('\n')
        in_content = False
        for line in lines:
            if '**Content**:' in line or 'content:' in line.lower() or '## Content' in line:
                in_content = True
                continue
            if in_content and line.startswith('---'):
                break
            if in_content:
                post_text += line + "\n"
        
        post_text = post_text.strip()
        if not post_text:
            logger.error("No post content extracted from file.")
            return False

        if dry_run:
            logger.info(f"[DRY RUN] Posting to LinkedIn:\n{post_text}")
            return True

        logger.info("Starting Playwright to post to LinkedIn...")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                session_path,
                headless=False
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            # Step 1: Navigate and Wait
            logger.info("Navigating to LinkedIn feed...")
            page.goto('https://www.linkedin.com/feed/')
            time.sleep(12) # Wait for page and UI components to settle
            
            # Step 2: Trigger 'Start a post'
            logger.info("Clicking 'Start a post' trigger...")
            try:
                # Use standard accessible button name
                trigger = page.get_by_role("button", name="Start a post").first
                if not trigger.is_visible(timeout=10000):
                    trigger = page.locator('.share-box-feed-entry__trigger').first
                
                trigger.scroll_into_view_if_needed()
                trigger.click(force=True, delay=200)
            except Exception as e:
                logger.error(f"Failed to click trigger: {e}")
                page.screenshot(path="linkedin_trigger_failed.png")
                browser.close()
                return False

            # Step 3: Wait for the Post Creation modal SPECIFICALLY
            # This filters out any open Messaging/Chat windows by requiring specific text
            logger.info("Waiting for Post Creation modal...")
            try:
                page.wait_for_selector('.share-creation-state, .artdeco-modal:has-text("Create a post")', timeout=20000)
                modal = page.locator('.share-creation-state, .artdeco-modal:has-text("Create a post")').first
                logger.info("Post Creation modal identified.")
            except Exception as e:
                logger.error(f"Post Creation modal not found: {e}")
                page.screenshot(path="linkedin_modal_failed.png")
                browser.close()
                return False

            # Step 4: Type content inside modal
            logger.info("Entering text content...")
            try:
                # Find the editor specifically inside this modal
                editor = modal.locator('.ql-editor, [role="textbox"], [contenteditable="true"]').first
                editor.click()
                time.sleep(1)
                
                # Use fill for reliability to avoid ghost typing issues
                editor.fill(post_text)
                time.sleep(1)
                
                # Final check and small interaction to ensure 'Post' button enables
                inner_text = editor.inner_text()
                if not inner_text.strip() or len(inner_text.strip()) < 10:
                    logger.warning("Fill didn't stick, typing manually to ensure focus...")
                    editor.click()
                    page.keyboard.type(post_text, delay=30)
                else:
                    # Ensure the cursor is at the end and press space to trigger event listeners
                    editor.click()
                    page.keyboard.press("End")
                    page.keyboard.type(" ")

                logger.info("Text content successfully entered.")
            except Exception as e:
                logger.error(f"Failed to type content: {e}")
                page.screenshot(path="linkedin_typing_error.png")
                browser.close()
                return False

            # Step 5: Click Post
            logger.info("Submitting post...")
            try:
                # Find the Post button specifically within this modal's actions
                post_btn = modal.locator('button:has-text("Post"), .share-actions__primary-action, .share-actions__post-button').first
                if post_btn.is_visible(timeout=5000):
                    post_btn.click()
                    logger.info("Post button clicked successfully.")
                else:
                    logger.info("Post button not found via selector, using Control+Enter fallback.")
                    page.keyboard.press("Control+Enter")
            except Exception as e:
                logger.error(f"Failed to final click Post: {e}")
                browser.close()
                return False

            logger.info("LinkedIn Post successful!")
            time.sleep(5) # Allow time for post to finalize
            browser.close()
            return True
    except Exception as e:
        logger.error(f"Error in post_to_linkedin: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python linkedin_poster.py <path_to_approval_file>")
        sys.exit(1)
    
    success = post_to_linkedin(sys.argv[1])
    if not success:
        sys.exit(1)
