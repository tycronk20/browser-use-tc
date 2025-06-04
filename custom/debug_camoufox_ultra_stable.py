#!/usr/bin/env python3
"""
Ultra-stable debug script for Camoufox with maximum crash prevention
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
logger = logging.getLogger("debug_camoufox_ultra")

# Set multiple environment variables for stability
os.environ["MOZ_DISABLE_CONTENT_SANDBOX"] = "1"
os.environ["MOZ_FORCE_DISABLE_E10S"] = "1"
os.environ["MOZ_X11_EGL"] = "0"  # Disable EGL on X11
os.environ["MOZ_WEBRENDER"] = "0"  # Disable WebRender completely
logger.info("✓ Set environment variables for maximum stability")

async def test_ultra_stable():
    """Test with ultra-stable configuration"""
    from browser_use.browser.profile import BrowserProfile
    from custom.camoufox_browser_session import CamoufoxBrowserSession
    
    configs = [
        {
            "name": "Headless Mode (Most Stable)",
            "headless": True,
            "prefs": {
                "gfx.webrender.software": True,
                "fission.autostart": False,
                "dom.ipc.processCount": 1,
                "browser.tabs.remote.autostart": False,
                "layers.acceleration.disabled": True,
            }
        },
        {
            "name": "Minimal Features Mode",
            "headless": False,
            "prefs": {
                "gfx.webrender.software": True,
                "fission.autostart": False,
                "dom.ipc.processCount": 1,
                "browser.tabs.remote.autostart": False,
                "browser.tabs.remote.autostart.2": False,
                "media.hardware-video-decoding.enabled": False,
                "media.gpu-process-decoder": False,
                "layers.acceleration.disabled": True,
                "gfx.canvas.accelerated": False,
                "javascript.enabled": True,  # Keep JS enabled
                "permissions.default.image": 2,  # Block images
                "media.autoplay.default": 5,  # Block all media
                "webgl.disabled": True,
                "dom.webgpu.enabled": False,
                "gfx.direct2d.disabled": True,
                "layers.offmainthreadcomposition.enabled": False,
            }
        }
    ]
    
    test_sites = [
        ("https://example.com", "Simple site"),
        ("https://httpbin.org", "API test site"),
        ("https://www.wikipedia.org", "Wikipedia"),
        ("https://duckduckgo.com", "DuckDuckGo"),
        ("https://www.google.com", "Google"),
    ]
    
    for config in configs:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing with config: {config['name']}")
        logger.info(f"{'='*60}")
        
        browser_profile = BrowserProfile(
            headless=config["headless"],
            disable_security=True,
            browser_args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        
        browser_session = CamoufoxBrowserSession(
            browser_profile=browser_profile,
            firefox_user_prefs=config["prefs"],
            args=[
                "--disable-gpu",
                "--disable-webgl",
                "--disable-webassembly",
                "--safe-mode",
            ],
            # Additional Camoufox options for stability
            block_webgl=True,
            block_webrtc=True,
            disable_coop=True,
        )
        
        try:
            await browser_session.start()
            logger.info("✓ Browser started successfully")
            
            page = await browser_session.get_current_page()
            
            for url, name in test_sites:
                try:
                    logger.info(f"Testing {name} ({url})...")
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(1)
                    logger.info(f"✅ {name} loaded successfully")
                except Exception as e:
                    if "crashed" in str(e).lower():
                        logger.error(f"❌ {name} CRASHED: {e}")
                        # Try to recover
                        try:
                            page = await browser_session.get_current_page()
                        except:
                            logger.error("Failed to recover page after crash")
                            break
                    else:
                        logger.error(f"❌ {name} failed: {e}")
            
        except Exception as e:
            logger.error(f"Browser session failed: {e}")
        finally:
            try:
                await browser_session.close()
                logger.info("✓ Browser closed")
            except:
                pass
            
        await asyncio.sleep(2)  # Brief pause between configs
    
    logger.info("\n✨ Ultra-stable testing completed!")

if __name__ == "__main__":
    print("🔍 Running ultra-stable Camoufox debug script...")
    print("=" * 60)
    asyncio.run(test_ultra_stable()) 