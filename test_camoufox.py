# test_camoufox.py
from camoufox.sync_api import Camoufox
import logging # Optional: for more detailed output

# Optional: Configure logging for Camoufox/Playwright
# logging.basicConfig(level=logging.DEBUG) # Uncomment for very verbose logs
# logging.getLogger("playwright").setLevel(logging.DEBUG) # For Playwright specific logs

print("Attempting to launch Camoufox...")
try:
    with Camoufox(headless=False) as browser: # Try headless=True if UI is an issue
        print("Camoufox launched. Opening new page...")
        page = browser.new_page()
        print("Page opened. Navigating to example.com...")
        page.goto("https://example.com") # A lightweight page for testing
        print("Navigated to example.com. Page title:", page.title())
        input("Press Enter to quit.")
    print("Camoufox closed successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc() # Print full traceback for debugging
