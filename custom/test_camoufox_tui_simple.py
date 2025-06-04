#!/usr/bin/env python3
"""
test_camoufox_tui_simple.py
Simple test to verify Camoufox TUI integration works
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.cli import load_user_config
from browser_use.agent.service import Agent
from browser_use.controller.service import Controller


async def test_simple_camoufox_tui():
    """Simple test of Camoufox with browser-use components"""
    
    print("\n🧪 Testing Camoufox TUI Integration")
    print("=" * 50)
    
    try:
        # 1. Create browser session
        print("\n1. Creating Camoufox browser session...")
        # Don't set viewport to let browser use full window
        profile = BrowserProfile(
            headless=False,
            viewport=None  # Let browser use natural viewport
        )
        browser_session = CamoufoxBrowserSession(browser_profile=profile)
        print("✅ Browser session created")
        
        # 2. Start browser
        print("\n2. Starting browser...")
        await browser_session.start()
        print("✅ Browser started")
        
        # 3. Test navigation
        print("\n3. Testing navigation...")
        page = await browser_session.get_current_page()
        await page.goto("https://www.example.com")
        title = await page.title()
        print(f"✅ Navigated to: {title}")
        
        # 4. Test browser state
        print("\n4. Getting browser state...")
        state = await browser_session.get_state_summary(cache_clickable_elements_hashes=False)
        print(f"✅ Current URL: {state.url}")
        
        # Remove any highlights that were created during state summary
        await browser_session.remove_highlights()
        
        # 5. Keep browser open for manual inspection
        print("\n5. Browser is ready for manual testing")
        print("   Press Enter to close browser and exit...")
        input()
        
        # 6. Cleanup
        print("\n6. Closing browser...")
        await browser_session.close()
        print("✅ Browser closed")
        
        print("\n✅ All tests passed! Camoufox integration is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tui_components():
    """Test that all TUI components can be initialized"""
    
    print("\n🧪 Testing TUI Component Initialization")
    print("=" * 50)
    
    try:
        # Load config
        print("\n1. Loading config...")
        config = load_user_config()
        print("✅ Config loaded")
        
        # Create controller
        print("\n2. Creating controller...")
        controller = Controller()
        print("✅ Controller created")
        
        # Import and test the custom app
        print("\n3. Testing CamoufoxBrowserUseApp import...")
        from camoufox_tui import CamoufoxBrowserUseApp
        print("✅ CamoufoxBrowserUseApp imported successfully")
        
        print("\n✅ All TUI components can be initialized")
        return True
        
    except Exception as e:
        print(f"\n❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    
    # Test 1: Basic Camoufox functionality
    test1_passed = await test_simple_camoufox_tui()
    
    # Test 2: TUI components
    if test1_passed:
        test2_passed = await test_tui_components()
    else:
        test2_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  Basic Camoufox: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  TUI Components: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✅ All tests passed!")
        print("\n📝 Next steps:")
        print("1. Run the enhanced debug script to check agent execution:")
        print("   python custom/debug_camoufox_tui_enhanced.py")
        print("\n2. If that passes, run the TUI with debug logging:")
        print("   BROWSER_USE_LOGGING_LEVEL=debug ./custom/camoufox-tui")
    
    return test1_passed and test2_passed


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 