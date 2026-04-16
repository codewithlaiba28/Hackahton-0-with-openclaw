import sys
import os
sys.path.append(os.getcwd())
from scripts.linkedin_poster import post_to_linkedin

if __name__ == "__main__":
    print("Testing LinkedIn poster...")
    success = post_to_linkedin("./test_linkedin_post.md")
    print(f"Post success: {success}")
