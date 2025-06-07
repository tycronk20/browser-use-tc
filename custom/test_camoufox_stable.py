#!/usr/bin/env python3
"""
test_camoufox_stable.py
Crash-resistant test for Camoufox with browser-use integration
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_camoufox_stable():
    """Test Camoufox with maximum stability settings"""
    
    print("🦊 Testing Camoufox with Enhanced Stability Settings...")
    print("📋 Configuration: Non-headless, Software rendering, Minimal processes")
    
    # Create browser profile with maximum stability settings
    profile = BrowserProfile(
        headless=False,  # GUI mode - more stable than headless
        user_data_dir=None,  # Use default profile to avoid conflicts
        viewport={"width": 1280, "height": 720},  # Standard resolution
    )
    
    # Create browser session with ultra-stable configuration
    browser_session = CamoufoxBrowserSession(
        browser_profile=profile,
        geoip=True,  # Enable GeoIP
        # Maximum stability Firefox preferences
        firefox_user_prefs={
            # Software rendering (most stable)
            "gfx.webrender.software": True,
            "gfx.webrender.enabled": False,
            "layers.acceleration.disabled": True,
            "gfx.canvas.accelerated": False,
            
            # Process management (reduce crashes)
            "fission.autostart": False,
            "dom.ipc.processCount": 1,
            "browser.tabs.remote.autostart": False,
            "extensions.webextensions.remote": False,
            
            # Disable problematic features
            "media.hardware-video-decoding.enabled": False,
            "media.ffmpeg.vaapi.enabled": False,
            "media.navigator.mediadatadecoder_vpx_enabled": False,
            
            # Memory management
            "browser.cache.memory.enable": False,
            "browser.sessionhistory.max_total_viewers": 0,
            "browser.tabs.animate": False,
            
            # Disable unnecessary features
            "browser.newtabpage.enabled": False,
            "browser.startup.homepage": "about:blank",
            "browser.newtab.url": "about:blank",
        },
        # Conservative launch arguments
        args=[
            "--disable-gpu",
            "--disable-gpu-compositing", 
            "--disable-gpu-rasterization",
            "--disable-gpu-sandbox",
            "--disable-software-rasterizer",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI,VizDisplayCompositor",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--memory-pressure-off",
            "--max_old_space_size=4096",
        ]
    )
    
    try:
        # Start the browser
        print("\n🚀 Starting Camoufox browser with stability configuration...")
        await browser_session.start()
        print("✅ Browser started successfully!")
        
        # Get current page
        page = await browser_session.get_current_page()
        print(f"📄 Current page URL: {page.url}")
        
        # Test basic navigation to a simple, stable site
        print("\n🌐 Testing navigation to httpbin.org (simple, stable site)...")
        await page.goto("https://httpbin.org/html", wait_until="domcontentloaded", timeout=30000)
        print("✅ Navigation successful!")
        
        # Get page title
        title = await page.title()
        print(f"📄 Page title: {title}")
        
        # Test basic page interaction
        print("\n🔍 Testing basic page interaction...")
        html_content = await page.content()
        print(f"📊 Page content length: {len(html_content)} characters")
        
        # Check for basic browser functionality
        user_agent = await page.evaluate("navigator.userAgent")
        print(f"🕵️ User Agent: {user_agent}")
        
        # Check webdriver detection bypass
        webdriver_detected = await page.evaluate("navigator.webdriver")
        print(f"🔒 WebDriver detected: {webdriver_detected} (should be False)")
        
        # Wait a moment to observe the browser
        print("\n⏱️ Waiting 5 seconds to observe browser stability...")
        await asyncio.sleep(5)
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Browser appears stable with current configuration")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error("Test failed", exc_info=True)
        return False
    
    finally:
        print("\n🔄 Closing browser...")
        try:
            await browser_session.close()
            print("✅ Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Warning during browser close: {e}")
    
    return True

async def main():
    """Main test function"""
    try:
        success = await test_camoufox_stable()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🔚 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.error("Unexpected error", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())