import os
import sys
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FacebookBrowserPoster')

def post_to_facebook(content: str, image_path: str = None):
    session_path = os.getenv('FACEBOOK_SESSION_PATH', './facebook_session')
    session_path = str(Path(session_path).resolve())
    
    logger.info(f"Starting Facebook browser poster with session: {session_path}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                ],
                ignore_default_args=["--enable-automation"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 800})

            logger.info("Navigating to Facebook...")
            page.goto("https://www.facebook.com/", wait_until="load", timeout=60000)
            time.sleep(5)

            # Step 1: Click the "What's on your mind?" area
            logger.info("Locating compose trigger...")
            # More specific selector for the initial trigger
            trigger = page.locator('[role="button"]:has-text("on your mind"), [role="link"]:has-text("on your mind")').first
            trigger.click(force=True)
            time.sleep(3)

            # Step 2: Upload image if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                # Try to click the photo button if visible, otherwise just try to set input
                try:
                    photo_btn = page.locator('[aria-label="Photo/video"]').first
                    if photo_btn.is_visible(timeout=5000):
                        photo_btn.click(force=True)
                        time.sleep(2)
                except:
                    pass
                
                # Use a very specific locator for the file input
                file_input = page.locator('input[type="file"][accept*="image"], input[role="presentation"][type="file"]').first
                file_input.set_input_files(image_path)
                time.sleep(5)

            # Step 3: Type content
            logger.info("Entering text content...")
            # Find the editor div
            editor = page.locator('div[role="textbox"]').first
            
            # Use evaluate to click and focus without scrolling if possible
            editor.evaluate("el => el.focus()")
            editor.click(force=True)
            time.sleep(1)
            
            # Clear if needed and type
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type(content, delay=30)
            time.sleep(2)

            # Step 4: Click "Post"
            logger.info("Submitting post via keyboard shortcut and click fallback...")
            # Often Control+Enter works on Facebook to submit a post
            page.keyboard.press("Control+Enter")
            time.sleep(2)
            
            # The submit button in the modal (click with force as backup)
            post_btn = page.locator('[aria-label="Post"], [role="button"]:has-text("Post")').first
            if post_btn.is_visible():
                post_btn.click(force=True)
            
            # Wait for completion (Modal closes or success message)
            logger.info("Waiting for post to finish...")
            time.sleep(8)
            
            logger.info("✅ Facebook Post successful!")
            
            # Take a final screenshot for proof
            page.screenshot(path="facebook_post_success.png")
            
            time.sleep(2)
            browser.close()
            return True

    except Exception as e:
        logger.error(f"Failed to post to Facebook: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Facebook Browser Poster")
    parser.add_argument("--content", required=True, help="Post content")
    parser.add_argument("--image", help="Optional path to image")
    args = parser.parse_args()

    # Load .env if exists
    if Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    post_to_facebook(args.content, args.image)
