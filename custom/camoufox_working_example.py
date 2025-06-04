#!/usr/bin/env python3
"""
Working example of Camoufox integration with browser-use
Uses sites that are known to work without crashes
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from browser_use import Agent, Controller
from browser_use.browser.profile import BrowserProfile
from custom.camoufox_browser_session import CamoufoxBrowserSession
from langchain_google_genai import ChatGoogleGenerativeAI


async def main():
    print("🦊 Starting Camoufox browser-use example...")
    
    # Initialize components
    controller = Controller()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    
    # Create browser session with stability settings
    browser_session = CamoufoxBrowserSession(
        browser_profile=BrowserProfile(
            headless=False,
            disable_security=True
        ),
        firefox_user_prefs={
            "gfx.webrender.software": True,
            "fission.autostart": False,
            "dom.ipc.processCount": 2,
            "browser.tabs.remote.autostart": False,
            "layers.acceleration.disabled": True,
        },
        args=["--disable-gpu"],
        block_webgl=True,
    )
    
    # Example tasks that work well with Camoufox
    tasks = [
        "Go to example.com and tell me what the main heading says",
        "Navigate to httpbin.org/headers and tell me what my user agent is",
        "Go to Wikipedia and search for 'Python programming language', then tell me when it was created",
    ]
    
    try:
        # Start browser
        await browser_session.start()
        print("✅ Browser started successfully")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n📋 Task {i}: {task}")
            
            # Create agent
            agent = Agent(
                task=task,
                llm=llm,
                controller=controller,
                browser_session=browser_session,
            )
            
            # Run the task
            result = await agent.run()
            print(f"✅ Task completed!")
            
            # Brief pause between tasks
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if browser_session:
            await browser_session.close()
            print("\n✅ Browser closed")


if __name__ == "__main__":
    print("=" * 60)
    print("Camoufox Browser-Use Working Example")
    print("This example uses sites that are known to work with Camoufox")
    print("=" * 60)
    
    asyncio.run(main()) 