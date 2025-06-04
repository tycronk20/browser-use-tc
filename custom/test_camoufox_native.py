#!/usr/bin/env python3
"""
test_camoufox_native.py
Test Camoufox browser using its native API
"""

import asyncio
from camoufox.async_api import AsyncCamoufox


async def test_camoufox_native():
    """Test Camoufox using its native async API"""
    
    print("🧪 Testing Camoufox with native API...")
    
    try:
        # Use Camoufox's native API
        async with AsyncCamoufox(
            headless=True,  # Run in headless mode for Docker
            # Add some stealth options
            geoip=True,  # Use GeoIP for location spoofing
        ) as browser:
            print("✅ Camoufox browser started successfully!")
            
            # Create a new page
            page = await browser.new_page()
            print("✅ New page created!")
            
            # Navigate to example.com
            print("📝 Navigating to example.com...")
            await page.goto("https://example.com")
            
            # Get page title
            title = await page.title()
            print(f"✅ Successfully navigated to example.com")
            print(f"📄 Page title: {title}")
            
            # Get some basic info about the page
            url = page.url
            print(f"🌐 Current URL: {url}")
            
            # Wait a bit
            print("⏳ Waiting 3 seconds...")
            await asyncio.sleep(3)
            
            print("✅ Test completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_camoufox_native())