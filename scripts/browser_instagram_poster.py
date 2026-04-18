import os
import sys
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('InstagramBrowserPoster')

def post_to_instagram(image_path: str, caption: str):
    session_path = os.getenv('INSTAGRAM_SESSION_PATH', './instagram_session')
    session_path = str(Path(session_path).resolve())
    
    if not Path(image_path).exists():
        logger.error(f"Image not found at {image_path}")
        return False

    logger.info(f"Starting Instagram browser poster with session: {session_path}")

    try:
        with sync_playwright() as p:
            # Using headful mode for debugging/real-time visibility if possible, 
            # but usually headless=False is safer for stealth during complex interactions
            browser = p.chromium.launch_persistent_context(
                session_path,
                headless=False, # Show browser for "real-time" testing as requested
                args=[
                    "--disable-blink-features=AutomationControlled",
                ],
                ignore_default_args=["--enable-automation"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 800})

            logger.info("Navigating to Instagram...")
            page.goto("https://www.instagram.com/", wait_until="load", timeout=60000)
            time.sleep(5)

            # Step 1: Click "Create" button
            # Instagram's "Create" button often has aria-label="New post" or text "Create"
            logger.info("Locating 'Create' button...")
            create_btn = page.locator('svg[aria-label="New post"], svg[aria-label="Create"], [aria-label="New post"], [aria-label="Create"]').first
            create_btn.click()
            time.sleep(3)

            # Step 2: Upload image
            logger.info(f"Uploading image: {image_path}")
            # The file input is often hidden; we can use set_input_files on the input element
            file_input = page.locator('input[type="file"]').first
            file_input.set_input_files(image_path)
            time.sleep(5)

            # Step 3: Click "Next" (Crop screen)
            logger.info("Clicking 'Next' (Crop)...")
            next_btn = page.get_by_role("button", name="Next").first
            next_btn.click()
            time.sleep(2)

            # Step 4: Click "Next" (Filter screen)
            logger.info("Clicking 'Next' (Filter)...")
            next_btn = page.get_by_role("button", name="Next").first
            next_btn.click()
            time.sleep(2)

            # Step 5: Type caption
            logger.info("Entering caption...")
            caption_box = page.locator('div[aria-label="Write a caption..."], [role="textbox"]').first
            caption_box.click()
            page.keyboard.type(caption, delay=50)
            time.sleep(2)

            # Step 6: Click "Share"
            logger.info("Clicking 'Share'...")
            share_btn = page.get_by_role("button", name="Share").first
            share_btn.click()
            
            # Wait for completion (Success message "Your post has been shared")
            logger.info("Waiting for sharing to complete...")
            page.wait_for_selector('text="Your post has been shared"', timeout=60000)
            
            logger.info("✅ Instagram Post successful!")
            
            # Take a final screenshot for proof
            page.screenshot(path="instagram_post_success.png")
            
            time.sleep(5)
            browser.close()
            return True

    except Exception as e:
        logger.error(f"Failed to post to Instagram: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Instagram Browser Poster")
    parser.add_argument("--image", required=True, help="Path to the image to post")
    parser.add_argument("--caption", default="Real-time Gold Tier testing for AI Employee. #AI #Automation #Hackathon", help="Post caption")
    args = parser.parse_args()

    # Load .env if exists
    if Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    post_to_instagram(args.image, args.caption)
