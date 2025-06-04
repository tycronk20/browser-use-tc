#!/usr/bin/env python3
"""
test_camoufox_browseruse.py
Simple test script to verify Camoufox browser works with browser-use
"""

import asyncio
from pathlib import Path
from browser_use import Agent, BrowserSession
from browser_use.cli import get_llm, load_user_config
from dotenv import load_dotenv
import camoufox

load_dotenv()

# Camoufox browser paths
CAMOUFOX_EXECUTABLE = camoufox.pkgman.launch_path()
CAMOUFOX_USER_DATA_DIR = Path.home() / ".cache/camoufox-profiles"


async def test_camoufox_browser():
    """Test browser-use with Camoufox browser"""
    
    print("🧪 Testing browser-use with Camoufox browser...")
    print(f"   Executable: {CAMOUFOX_EXECUTABLE}")
    print(f"   User Data: {CAMOUFOX_USER_DATA_DIR}")
    
    # Load config for LLM
    config = load_user_config()
    
    # Check if we have API keys, if not, skip LLM test
    import os
    has_api_key = any([
        os.getenv('OPENAI_API_KEY'),
        os.getenv('ANTHROPIC_API_KEY'),
        os.getenv('GOOGLE_API_KEY'),
        os.getenv('OLLAMA_BASE_URL')
    ])
    
    if not has_api_key:
        print("⚠️ No API keys found. Testing browser launch only (no LLM agent).")
        llm = None
    else:
        llm = get_llm(config)
    
    # Create browser session with Camoufox
    browser_session = BrowserSession(
        executable_path=CAMOUFOX_EXECUTABLE,
        user_data_dir=str(CAMOUFOX_USER_DATA_DIR),
        profile_directory="Default",
        headless=True,  # Run in headless mode for Docker environment
        disable_security=False,
        deterministic_rendering=False,
        # Firefox/Camoufox-specific args
        args=[
            '--headless',  # Firefox headless mode
            '--no-first-run',
            '--disable-default-browser-check',
            '--disable-popup-blocking',
            '--disable-translate',
            '--new-instance',
            '--safe-mode',
        ]
    )
    
    try:
        # Start browser
        print("\n🚀 Starting Camoufox browser...")
        await browser_session.start()
        print("✅ Browser started successfully!")
        
        if llm:
            # Create a simple agent
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
    asyncio.run(test_camoufox_browser())