#!/usr/bin/env python3
"""
test_camoufox_no_crash.py
Test Camoufox with disabled theming to prevent tab crashes
"""

import asyncio
from camoufox.async_api import AsyncCamoufox


async def test_with_disabled_theming():
    """Test navigation with disabled theming"""
    print("🧪 Testing Camoufox with disabled theming...")
    
    # Configuration that disables custom theming
    config = {
        'headless': False,
        'geoip': False,  # Disable GeoIP to reduce complexity
        'config': {
            'disableTheming': True,  # Use standard Firefox UI
            'showcursor': False,     # Disable the red cursor
        }
    }
    
    test_urls = [
        "https://example.com",
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.bing.com",
    ]
    
    try:
        async with AsyncCamoufox(**config) as browser:
            page = await browser.new_page()
            
            for url in test_urls:
                try:
                    print(f"→ Navigating to {url}...")
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await asyncio.sleep(3)  # Wait to check stability
                    
                    # Verify page is still responsive
                    title = await page.title()
                    print(f"  ✓ Success! Title: {title[:50]}...")
                    
                    # Try to interact with the page
                    await page.evaluate("() => document.body.innerHTML.length")
                    print(f"  ✓ Page is responsive")
                    
                except Exception as e:
                    print(f"  ❌ Failed: {type(e).__name__}: {str(e)}")
                    if page.is_closed():
                        print("  ⚠️  Tab crashed!")
                        # Create a new page if crashed
                        page = await browser.new_page()
            
            print("\n✅ Test completed successfully!")
            await asyncio.sleep(5)  # Keep browser open for observation
            
    except Exception as e:
        print(f"❌ Browser test failed: {type(e).__name__}: {str(e)}")


if __name__ == "__main__":
    print("🔍 Testing Camoufox with standard Firefox UI...\n")
    print("ℹ️  This test disables Camoufox's custom theming to prevent crashes.\n")
    asyncio.run(test_with_disabled_theming()) 