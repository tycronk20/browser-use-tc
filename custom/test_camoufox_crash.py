#!/usr/bin/env python3
"""
test_camoufox_crash.py
Minimal test to diagnose Camoufox tab crashes
"""

import asyncio
from camoufox.async_api import AsyncCamoufox


async def test_basic_navigation():
    """Test basic navigation without browser-use"""
    print("🧪 Testing Camoufox navigation...")
    
    # Test with different configurations
    configs = [
        {"headless": False, "geoip": True},
        {"headless": False, "geoip": False},
        {"headless": False, "geoip": False, "humanize": False},
    ]
    
    test_urls = [
        "https://example.com",
        "https://www.google.com",
        "https://www.bing.com",
        "https://duckduckgo.com",
    ]
    
    for i, config in enumerate(configs):
        print(f"\n📋 Test configuration {i+1}: {config}")
        
        try:
            async with AsyncCamoufox(**config) as browser:
                page = await browser.new_page()
                
                for url in test_urls:
                    try:
                        print(f"  → Navigating to {url}...")
                        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(2)  # Wait to see if tab crashes
                        
                        # Check if page is still responsive
                        title = await page.title()
                        print(f"    ✓ Success! Title: {title}")
                        
                    except Exception as e:
                        print(f"    ❌ Failed: {type(e).__name__}: {str(e)}")
                        
                        # Try to diagnose the crash
                        try:
                            # Check if page is closed
                            if page.is_closed():
                                print("    ⚠️  Tab crashed/closed!")
                            else:
                                # Try to get console logs
                                page.on("console", lambda msg: print(f"    Console: {msg.text}"))
                                page.on("pageerror", lambda err: print(f"    Error: {err}"))
                        except:
                            pass
                
                await browser.close()
                
        except Exception as e:
            print(f"  ❌ Browser initialization failed: {type(e).__name__}: {str(e)}")
    
    print("\n📊 Test complete!")


async def test_with_playwright_direct():
    """Test using Playwright directly to compare"""
    print("\n🎭 Testing with Playwright directly (Firefox)...")
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("  → Navigating to Google...")
            await page.goto("https://www.google.com")
            title = await page.title()
            print(f"  ✓ Success with plain Firefox! Title: {title}")
        except Exception as e:
            print(f"  ❌ Failed with plain Firefox: {e}")
        
        await browser.close()


if __name__ == "__main__":
    print("🔍 Diagnosing Camoufox tab crashes...\n")
    asyncio.run(test_basic_navigation())
    asyncio.run(test_with_playwright_direct()) 