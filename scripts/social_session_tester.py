import os
import sys
import logging
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SocialSessionTester')

# Configuration
PLATFORMS = {
    "linkedin": {
        "url": "https://www.linkedin.com/feed/",
        "session_env": "LINKEDIN_SESSION_PATH",
        "default_session": "./linkedin_session",
        "success_selector": "section.core-rail, [data-test-global-nav-link-my-network]",
        "login_selector": "form.login__form, [data-test-id='login-form']"
    },
    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "session_env": "WHATSAPP_SESSION_PATH",
        "default_session": "./whatsapp_session",
        "success_selector": "[data-testid='chat-list']",
        "login_selector": "canvas" # The QR code canvas
    },
    "twitter": {
        "url": "https://x.com/home",
        "session_env": "TWITTER_SESSION_PATH",
        "default_session": "./twitter_session",
        "success_selector": "[data-testid='SideNav_Account_Button'], [aria-label='Home']",
        "login_selector": "[data-testid='loginButton']"
    },
    "facebook": {
        "url": "https://www.facebook.com/",
        "session_env": "FACEBOOK_SESSION_PATH",
        "default_session": "./facebook_session",
        "success_selector": "[role='navigation'], [aria-label='Facebook']",
        "login_selector": "input[name='login']"
    },
    "instagram": {
        "url": "https://www.instagram.com/",
        "session_env": "INSTAGRAM_SESSION_PATH",
        "default_session": "./instagram_session",
        "success_selector": "[aria-label='Home'], svg[aria-label='Home']",
        "login_selector": "form#loginForm"
    }
}

def test_session(platform_name: str):
    if platform_name not in PLATFORMS:
        logger.error(f"Unsupported platform: {platform_name}")
        return False

    config = PLATFORMS[platform_name]
    session_path = os.getenv(config["session_env"], config["default_session"])
    session_path = str(Path(session_path).resolve())

    if not Path(session_path).exists():
        logger.error(f"Session directory not found for {platform_name} at {session_path}")
        return False

    logger.info(f"Testing session for {platform_name} using path: {session_path}")

    try:
        with sync_playwright() as p:
            # Using headless=True for background testing
            # Adding stealth arguments to bypass automation detection
            browser = p.chromium.launch_persistent_context(
                session_path,
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
                ignore_default_args=["--enable-automation"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Set a standard viewport
            page.set_viewport_size({"width": 1280, "height": 800})
            
            logger.info(f"Navigating to {config['url']}...")
            # Increased timeout and wait_until to handle slower social media loads
            page.goto(config["url"], wait_until="load", timeout=90000)
            
            # Wait a few seconds for any redirects or dynamic content
            page.wait_for_timeout(5000)

            # Check for success selector
            is_logged_in = False
            try:
                page.wait_for_selector(config["success_selector"], timeout=10000)
                logger.info(f"✅ Success selector found for {platform_name}!")
                is_logged_in = True
            except:
                logger.warning(f"Could not find success selector for {platform_name}.")

            # Check for login selector (negative check)
            try:
                if page.is_visible(config["login_selector"], timeout=2000):
                    logger.error(f"❌ Login element detected for {platform_name}. Session may have expired.")
                    is_logged_in = False
            except:
                pass

            # Final result
            if is_logged_in:
                logger.info(f"RESULT: {platform_name.upper()} session IS ACTIVE.")
            else:
                logger.error(f"RESULT: {platform_name.upper()} session IS NOT ACTIVE or could not be verified.")
                # Take a screenshot for debugging
                debug_path = f"debug_{platform_name}_fail.png"
                page.screenshot(path=debug_path)
                logger.info(f"Debug screenshot saved to {debug_path}")

            browser.close()
            return is_logged_in

    except Exception as e:
        logger.error(f"An error occurred while testing {platform_name}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Social Media Session Tester")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()) + ["all"], default="all", help="Platform to test")
    args = parser.parse_args()

    # Load .env if exists
    if Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    if args.platform == "all":
        results = {}
        for p in PLATFORMS.keys():
            results[p] = test_session(p)
        
        print("\n" + "="*30)
        print("SESSION TEST SUMMARY")
        print("="*30)
        for p, status in results.items():
            icon = "✅ ACTIVE" if status else "❌ INACTIVE/ERROR"
            print(f"{p.capitalize():<12}: {icon}")
        print("="*30)
    else:
        test_session(args.platform)
