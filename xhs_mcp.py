from mcp.server.fastmcp import FastMCP
import sys
import os
import time

# Add current directory to path so we can import local modules
sys.path.append(os.getcwd())

from upload_xiaohongshu import publish_single_post, publish_image_post, xiaohongshu_login
from liulanqi import get_driver

mcp = FastMCP("Xiaohongshu Publisher")

# Global driver instance
DRIVER = None

def get_or_create_driver():
    global DRIVER
    if DRIVER is None:
        print("Initializing Selenium Driver...")
        DRIVER = get_driver()
        # Initial login check
        # Reuse the login logic from upload_xiaohongshu
        xiaohongshu_login(DRIVER)
    return DRIVER

@mcp.tool(
    name='publish_note',
    description='Publishes a note (image or video) to Xiaohongshu.'
)
def publish_note(title: str, content: str, media_path: str, topics: list[str] = None) -> str:
    """
    Publishes a note to Xiaohongshu.
    
    Args:
        title: Title of the note
        content: Description/Content of the note
        media_path: Absolute path to the image or video file
        topics: List of hashtags (e.g. ["#Travel", "#China"])
    """
    driver = get_or_create_driver()
    
    try:
        # Determine content type
        ext = os.path.splitext(media_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.webp']:
            print(f"Detected image file: {media_path}. Using Image Publish flow.")
            publish_image_post(driver, media_path, title, content, topics)
        else:
            print(f"Detected video/other file: {media_path}. Using Video Publish flow.")
            publish_single_post(driver, media_path, title, content, topics)
        
        return "Successfully published note."
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Failed to publish note: {str(e)}"

if __name__ == "__main__":
    try:
        mcp.run()
    finally:
        if DRIVER:
            DRIVER.quit()
