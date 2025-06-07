#!/usr/bin/env python3
"""
test_camoufox_browseruse_v2.py
Test Camoufox browser with browser-use using custom CamoufoxBrowserSession
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Import our custom Camoufox session
from camoufox_browser_session import CamoufoxBrowserSession

load_dotenv()

# Camoufox browser paths
CAMOUFOX_USER_DATA_DIR = Path.home() / ".cache/camoufox-profiles"


async def test_camoufox_browser_v2():
    """Test browser-use with Camoufox using custom session"""
    
    print("🧪 Testing browser-use with Camoufox (v2 - Custom Session)...")
    print(f"   User Data: {CAMOUFOX_USER_DATA_DIR}")
    
    # Check if we have API keys for LLM testing
    has_api_key = any([
        os.getenv('OPENAI_API_KEY'),
        os.getenv('ANTHROPIC_API_KEY'),
        os.getenv('GOOGLE_API_KEY'),
        os.getenv('OLLAMA_BASE_URL')
    ])
    
    if not has_api_key:
        print("⚠️ No API keys found. Testing browser functionality only (no LLM agent).")
    
    # Create Camoufox browser session with crash prevention
    browser_session = CamoufoxBrowserSession(
        user_data_dir=str(CAMOUFOX_USER_DATA_DIR),
        headless=False,  # Run in GUI mode to prevent crashes
        # Camoufox-specific options
        geoip=True,  # Enable GeoIP for location spoofing
        # Enhanced crash prevention measures
        firefox_user_prefs={
            "gfx.webrender.software": True,    # Use software rendering
            "fission.autostart": False,         # Disable process isolation
            "dom.ipc.processCount": 2,          # Limit content processes
            "browser.tabs.remote.autostart": False,  # Disable tab sandboxing
            "media.hardware-video-decoding.enabled": False,  # Disable hardware video
            "layers.acceleration.disabled": True,  # Disable layer acceleration
            "gfx.canvas.accelerated": False,    # Disable canvas acceleration
        },
        args=[
            "--disable-gpu",           # Disable GPU acceleration
            "--disable-webgl",         # Disable WebGL
            "--disable-webassembly",   # Disable WebAssembly
            "--safe-mode",             # Run in safe mode
        ]
    )
    
    try:
        # Start browser
        print("\n🚀 Starting Camoufox browser...")
        await browser_session.start()
        print("✅ Browser started successfully!")
        
        if has_api_key:
            # Test with LLM agent
            from browser_use import Agent
            from browser_use.cli import get_llm, load_user_config
            
            config = load_user_config()
            llm = get_llm(config)
            
            print("\n📝 Creating agent to navigate to example.com...")
            agent = Agent(
                task="Navigate to example.com and tell me the page title",
                llm=llm,
                browser_session=browser_session,
            )
            
            # Run the task
            result = await agent.run()
            print(f"\n✅ Task completed!")
            print(f"📄 Result: {result}")
        else:
            # Just test basic browser functionality
            print("\n📝 Testing basic browser navigation...")
            page = await browser_session.get_current_page()
            await page.goto("https://example.com")
            title = await page.title()
            print(f"✅ Successfully navigated to example.com")
            print(f"📄 Page title: {title}")
            
            # Test some stealth features
            user_agent = await page.evaluate("navigator.userAgent")
            print(f"🕵️ User Agent: {user_agent}")
            
            # Check if we have webdriver property (should be undefined for stealth)
            webdriver = await page.evaluate("navigator.webdriver")
            print(f"🔍 Navigator.webdriver: {webdriver}")
        
        # Wait a bit before closing
        print("\n⏳ Waiting 5 seconds before closing...")
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔚 Closing browser...")
        await browser_session.close()
        print("✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_camoufox_browser_v2())