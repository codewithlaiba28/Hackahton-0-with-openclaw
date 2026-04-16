import sys
import os
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def login(platform: str):
    session_path = ""
    target_url = ""
    
    if platform == "linkedin":
        session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
        target_url = "https://www.linkedin.com/login"
        print(f"Opening LinkedIn for login. Session will be saved to: {session_path}")
    elif platform == "whatsapp":
        session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
        target_url = "https://web.whatsapp.com"
        print(f"Opening WhatsApp Web. Please scan the QR code. Session will be saved to: {session_path}")
    else:
        print(f"Unsupported platform: {platform}")
        return

    # Ensure session path is absolute or correct relative to execution root
    session_path = str(Path(session_path).resolve())

    with sync_playwright() as p:
        # Launching in HEADFUL mode (headless=False) so the user can interact
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(target_url)
        
        print("\n" + "="*50)
        print(f"A browser window has opened for {platform.capitalize()}.")
        print("1. Please complete the login process manually.")
        print("2. Once you are logged in and see your feed/messages,")
        print("3. Close the browser window OR press Enter here to finish.")
        print("="*50)
        
        input("\nPress Enter when you have successfully logged in and want to close the browser...")
        browser.close()
        print(f"\nLogin session for {platform} saved successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Employee Login Manager")
    parser.add_argument("--platform", choices=["linkedin", "whatsapp"], required=True, help="Platform to log in to")
    args = parser.parse_args()
    
    # Load .env variables if available (primitive loader)
    if Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k] = v

    login(args.platform)
