#!/usr/bin/env python3
"""
test_brave_browseruse.py
Simple test script to verify Brave browser works with browser-use
"""

import asyncio
from pathlib import Path
from browser_use import Agent, BrowserSession
from browser_use.cli import get_llm, load_user_config
from dotenv import load_dotenv

load_dotenv()

# Brave browser paths
BRAVE_EXECUTABLE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
BRAVE_USER_DATA_DIR = Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser"


async def test_brave_browser():
    """Test browser-use with Brave browser"""
    
    print("🧪 Testing browser-use with Brave browser...")
    print(f"   Executable: {BRAVE_EXECUTABLE}")
    print(f"   User Data: {BRAVE_USER_DATA_DIR}")
    
    # Load config for LLM
    config = load_user_config()
    llm = get_llm(config)
    
    # Create browser session with Brave
    browser_session = BrowserSession(
        executable_path=BRAVE_EXECUTABLE,
        user_data_dir=str(BRAVE_USER_DATA_DIR),
        profile_directory="Default",
        headless=False,  # Run in visible mode for testing
        disable_security=False,
        deterministic_rendering=False,
        args=[
            '--disable-brave-update',
            '--disable-brave-rewards-extension',
            '--disable-brave-news-today',
        ]
    )
    
    try:
        # Start browser
        print("\n🚀 Starting Brave browser...")
        await browser_session.start()
        print("✅ Browser started successfully!")
        
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
    asyncio.run(test_brave_browser()) 