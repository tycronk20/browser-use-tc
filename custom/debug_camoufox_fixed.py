#!/usr/bin/env python3
"""
Fixed debug script for Camoufox TUI with crash prevention measures
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import subprocess

# Add parent directory to path so we can import from browser_use
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("debug_camoufox_fixed")

# Increase memory limits on macOS
if sys.platform == "darwin":
    try:
        subprocess.run(["launchctl", "limit", "maxproc", "2048", "2048"], check=False)
        logger.info("✓ Increased maxproc limit on macOS")
    except Exception as e:
        logger.warning(f"Could not increase maxproc limit: {e}")

# Set environment variable to disable content sandbox (helps with memory issues)
os.environ["MOZ_DISABLE_CONTENT_SANDBOX"] = "1"
logger.info("✓ Disabled content sandbox for Firefox")

async def debug_camoufox_fixed():
    """Run fixed debug version with crash prevention"""
    from browser_use.browser.profile import BrowserProfile
    from custom.camoufox_browser_session import CamoufoxBrowserSession
    from browser_use import Agent, Controller
    from browser_use.cli import load_user_config, get_llm
    
    try:
        logger.info("Step 1: Loading configuration...")
        config = load_user_config()
        logger.info("✓ Config loaded successfully")
        
        logger.info("Step 2: Initializing LLM...")
        llm = get_llm(config)
        logger.info(f"✓ LLM initialized: {type(llm).__name__}")
        
        logger.info("Step 3: Initializing Controller...")
        controller = Controller()
        logger.info("✓ Controller initialized")
        
        logger.info("Step 4: Creating browser profile with crash prevention...")
        browser_profile = BrowserProfile(
            headless=False,
            disable_security=True,
            browser_args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        logger.info("✓ Browser profile created")
        
        logger.info("Step 5: Initializing CamoufoxBrowserSession with crash prevention...")
        # Add aggressive crash prevention options
        browser_session = CamoufoxBrowserSession(
            browser_profile=browser_profile,
            # Additional Firefox preferences for extreme stability
            firefox_user_prefs={
                "gfx.webrender.software": True,
                "fission.autostart": False,
                "dom.ipc.processCount": 2,  # Even more conservative
                "browser.tabs.remote.autostart": False,  # Disable e10s
                "browser.tabs.remote.autostart.2": False,
                "media.hardware-video-decoding.enabled": False,
                "media.gpu-process-decoder": False,
                "layers.acceleration.disabled": True,  # Disable all acceleration
                "gfx.canvas.accelerated": False,
            },
            # More aggressive GPU disabling
            args=[
                "--disable-gpu",
                "--disable-webgl", 
                "--disable-webassembly",
                "--safe-mode",  # Firefox safe mode
            ]
        )
        logger.info("✓ CamoufoxBrowserSession created with enhanced crash prevention")
        
        logger.info("Step 6: Starting browser...")
        await browser_session.start()
        logger.info("✓ Browser started")
        
        logger.info("Step 7: Testing navigation to various sites...")
        page = await browser_session.get_current_page()
        
        # Test sites in order of complexity
        test_sites = [
            ("https://example.com", "Simple site"),
            ("https://httpbin.org", "API test site"),
            ("https://www.wikipedia.org", "Wikipedia"),
            ("https://duckduckgo.com", "DuckDuckGo"),
            ("https://www.google.com", "Google"),
            ("https://www.youtube.com", "YouTube"),
        ]
        
        for url, name in test_sites:
            try:
                logger.info(f"Testing {name} ({url})...")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)  # Give it time to potentially crash
                logger.info(f"✅ Successfully loaded {name}")
            except Exception as e:
                logger.error(f"❌ Failed to load {name}: {e}")
                if "crashed" in str(e).lower():
                    logger.info("Detected crash - trying fallback options...")
                    
                    # Try with even more conservative settings
                    logger.info("Attempting with minimal features...")
                    await page.goto("about:blank")
                    await page.evaluate("""
                        // Disable as many features as possible via JavaScript
                        if (window.navigator && window.navigator.gpu) {
                            window.navigator.gpu = undefined;
                        }
                    """)
                    
                    # Try again with network idle
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=10000)
                        logger.info(f"✅ Successfully loaded {name} with fallback")
                    except:
                        logger.error(f"❌ Still failed with fallback")
        
        logger.info("\n✨ Debug completed! Check the logs above for crash information.")
        
    except Exception as e:
        logger.error(f"\n❌ Debug failed: {e}", exc_info=True)
    finally:
        if 'browser_session' in locals():
            logger.info("Closing browser...")
            await browser_session.close()
            logger.info("✓ Browser closed")

if __name__ == "__main__":
    print("🔍 Running fixed Camoufox debug script with crash prevention...")
    print("=" * 50)
    asyncio.run(debug_camoufox_fixed()) 