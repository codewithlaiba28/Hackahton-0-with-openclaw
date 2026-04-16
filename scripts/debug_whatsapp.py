import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def debug_whatsapp():
    session_path = './whatsapp_session'
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(Path(session_path).resolve()), 
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto('https://web.whatsapp.com')
        
        print("Waiting for page load...")
        print("Dumping HTML...")
        with open('whatsapp_html_dump.txt', 'w', encoding='utf-8') as f:
            f.write(page.content())
        print("HTML dumped to whatsapp_html_dump.txt")
        
        browser.close()

if __name__ == "__main__":
    debug_whatsapp()
