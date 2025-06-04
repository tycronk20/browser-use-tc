#!/usr/bin/env python3
"""
test_camoufox_tui.py
Test script to verify Camoufox TUI integration without launching full TUI
"""

import asyncio
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.cli import load_user_config, get_llm
from browser_use.controller.service import Controller


async def test_integration():
    """Test that all components can be initialized"""
    print("🧪 Testing Camoufox TUI integration...")
    
    try:
        # 1. Test config loading
        print("✓ Loading configuration...")
        config = load_user_config()
        
        # 2. Test LLM initialization
        print("✓ Initializing LLM...")
        llm = get_llm(config)
        model_name = getattr(llm, 'model_name', None) or getattr(llm, 'model', 'Unknown')
        print(f"  → LLM: {llm.__class__.__name__} ({model_name})")
        
        # 3. Test Controller initialization
        print("✓ Initializing Controller...")
        controller = Controller()
        
        # 4. Test CamoufoxBrowserSession initialization
        print("✓ Initializing CamoufoxBrowserSession...")
        profile = BrowserProfile(headless=False)
        browser_session = CamoufoxBrowserSession(browser_profile=profile)
        
        # 5. Test browser start
        print("✓ Starting Camoufox browser...")
        await browser_session.start()
        
        # 6. Test navigation
        page = await browser_session.get_current_page()
        print("✓ Navigating to test page...")
        await page.goto("https://example.com")
        print(f"  → Current URL: {page.url}")
        
        # 7. Close browser
        print("✓ Closing browser...")
        await browser_session.close()
        
        print("\n✅ All tests passed! Camoufox TUI integration is working.")
        print("\nYou can now run: ./custom/camoufox-tui")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1) 