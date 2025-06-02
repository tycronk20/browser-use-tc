#!/usr/bin/env python3
"""
Test script to verify CDP connection to the sword Chrome profile works.
"""

import asyncio
from playwright.async_api import async_playwright

async def test_sword_connection():
    """Test connecting to the sword Chrome instance via CDP."""
    
    print("Testing connection to sword Chrome via CDP...")
    
    async with async_playwright() as pw:
        try:
            # Connect to existing Chrome instance
            browser = await pw.chromium.connect_over_cdp("http://localhost:9222")
            print("✓ Successfully connected to Chrome via CDP")
            
            # Get existing contexts
            contexts = browser.contexts
            print(f"✓ Found {len(contexts)} browser context(s)")
            
            if contexts:
                # Use the first context (should be the sword profile)
                ctx = contexts[0]
                print(f"✓ Using context with {len(ctx.pages)} page(s)")
                
                # Create a new page to test functionality
                page = await ctx.new_page()
                print("✓ Created new page")
                
                # Navigate to a test site
                await page.goto("https://example.com")
                print("✓ Successfully navigated to example.com")
                
                # Get the page title
                title = await page.title()
                print(f"✓ Page title: {title}")
                
                # Check if this is the sword profile by looking for profile-specific elements
                user_agent = await page.evaluate("navigator.userAgent")
                print(f"✓ User agent: {user_agent[:50]}...")
                
                # Close the test page
                await page.close()
                print("✓ Test page closed")
                
            await browser.close()
            print("✓ Connection test completed successfully!")
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            print("Make sure Chrome is running with: ~/bin/sword")
            return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_sword_connection()) 