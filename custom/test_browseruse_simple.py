#!/usr/bin/env python3
"""
Simple test to verify browser-use can connect to sword Chrome via CDP.
"""

import asyncio
from browser_use.browser.session import BrowserSession

async def test_simple_connection():
    """Test browser-use BrowserSession connection to sword Chrome via CDP."""
    
    print("Testing browser-use BrowserSession with sword Chrome via CDP...")
    
    try:
        # Create browser session that connects via CDP
        browser_session = BrowserSession(
            cdp_url="http://localhost:9222",
            # Don't set headless since we're connecting to existing browser
        )
        
        print("✓ BrowserSession instance created")
        
        # Start the browser session (should connect to existing Chrome)
        await browser_session.start()
        print("✓ BrowserSession connected via CDP")
        
        # Get a new tab/page
        page = await browser_session.create_new_tab()
        print("✓ New tab created")
        
        # Navigate to a test site
        await page.goto("https://httpbin.org/get")
        print("✓ Navigated to httpbin.org/get")
        
        # Get the page title
        title = await page.title()
        print(f"✓ Page title: {title}")
        
        # Get the page content to verify it loaded
        content = await page.content()
        if "httpbin" in content.lower():
            print("✓ Page content loaded correctly")
        else:
            print("⚠ Page content may not have loaded correctly")
        
        # Close the page
        await page.close()
        print("✓ Test page closed")
        
        # Close browser session
        await browser_session.close()
        print("✓ BrowserSession closed")
        
        print("\n🎉 All tests passed! Sword Chrome CDP connection is working!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        print("Make sure Chrome is running with: ~/bin/sword")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_simple_connection()) 