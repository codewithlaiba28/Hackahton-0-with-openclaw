import os
import sys
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TwitterBrowserPoster')

def post_tweet(content: str, image_path: str = None):
    session_path = os.getenv('TWITTER_SESSION_PATH', './twitter_session')
    session_path = str(Path(session_path).resolve())
    
    logger.info(f"Starting Twitter browser poster with session: {session_path}")

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

            logger.info("Navigating to Twitter/X home...")
            page.goto("https://x.com/home", wait_until="load", timeout=60000)
            time.sleep(5)

            # Step 1: Locate the tweet input
            logger.info("Locating compose box...")
            try:
                # Target the "What is happening?!" editor
                editor = page.locator('[data-testid="tweetTextarea_0"], .public-DraftEditor-content').first
                editor.click()
                time.sleep(1)
                page.keyboard.type(content, delay=50)
            except Exception as e:
                logger.error(f"Failed to find or click editor: {e}")
                # Fallback: click the large "Post" button if it's there
                post_trigger = page.locator('[data-testid="SideNav_NewTweet_Button"]').first
                post_trigger.click()
                time.sleep(2)
                editor = page.locator('[data-testid="tweetTextarea_0"], .public-DraftEditor-content').first
                editor.click()
                page.keyboard.type(content, delay=50)

            # Step 2: Upload image if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                file_input = page.locator('input[data-testid="fileInput"]').first
                file_input.set_input_files(image_path)
                time.sleep(5)

            # Step 3: Click "Post"
            logger.info("Clicking 'Post'...")
            post_btn = page.locator('[data-testid="tweetButtonInline"], [data-testid="tweetButton"]').first
            post_btn.click(force=True)
            
            # Wait for success
            logger.info("Waiting for tweet to send...")
            time.sleep(5)
            
            logger.info("✅ Tweet successful!")
            
            # Take a final screenshot for proof
            page.screenshot(path="twitter_post_success.png")
            
            time.sleep(2)
            browser.close()
            return True

    except Exception as e:
        logger.error(f"Failed to post to Twitter: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Twitter Browser Poster")
    parser.add_argument("--content", required=True, help="Tweet content")
    parser.add_argument("--image", help="Optional path to image")
    args = parser.parse_args()

    # Load .env if exists
    if Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    post_tweet(args.content, args.image)
