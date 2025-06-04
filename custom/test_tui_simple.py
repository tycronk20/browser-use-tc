#!/usr/bin/env python3
"""
test_tui_simple.py
Simple test to debug TUI hanging
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.cli import load_user_config, get_llm, BrowserUseApp
from browser_use.controller.service import Controller


async def test_tui_simple():
    """Simple TUI test"""
    print("🧪 Testing TUI initialization...")
    
    # Load config
    config = load_user_config()
    config['browser']['headless'] = False
    
    # Initialize components
    print("1. Initializing LLM...")
    llm = get_llm(config)
    
    print("2. Initializing Controller...")
    controller = Controller()
    
    print("3. Initializing CamoufoxBrowserSession...")
    profile = BrowserProfile(headless=False)
    browser_session = CamoufoxBrowserSession(browser_profile=profile)
    
    print("4. Starting browser...")
    await browser_session.start()
    
    print("5. Creating BrowserUseApp...")
    app = BrowserUseApp(config)
    app.browser_session = browser_session
    app.controller = controller
    app.llm = llm
    
    print("6. Testing agent task...")
    # Instead of running the full TUI, just test a simple task
    from browser_use.agent.service import Agent
    
    agent = Agent(
        task="Navigate to example.com",
        llm=llm,
        controller=controller,
        browser_session=browser_session,
        source='cli',
    )
    
    print("7. Running one agent step...")
    await agent.step()
    
    print("\n✅ All components initialized successfully!")
    print("The hanging issue might be in the TUI's event loop.")
    
    # Keep browser open for observation
    await asyncio.sleep(5)
    
    # Close browser
    await browser_session.close()


if __name__ == '__main__':
    print("🔍 Running simple TUI debug test...\n")
    asyncio.run(test_tui_simple()) 