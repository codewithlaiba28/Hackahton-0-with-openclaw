import sys
import os
sys.path.append(os.getcwd())
from scripts.whatsapp_reply import reply_to_whatsapp

if __name__ == "__main__":
    print("Testing WhatsApp Reply to 'yousufnoushadkhan'")
    # We saw this name exactly in the screenshot
    reply_to_whatsapp("yousufnoushadkhan", "Hello! This is Laiba's AI Employee responding autonomously. Setup successful!")
    print("Test Complete.")
