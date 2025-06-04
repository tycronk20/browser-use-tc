#!/usr/bin/env python3
"""
debug_camoufox_tui.py
Debug script to understand where the TUI is hanging
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.cli import load_user_config, get_llm
from browser_use.controller.service import Controller
from browser_use.agent.service import Agent


async def debug_tui():
    """Debug the TUI initialization step by step"""
    logger = logging.getLogger('debug_tui')
    
    try:
        # 1. Test config loading
        logger.info("Step 1: Loading configuration...")
        config = load_user_config()
        logger.info("✓ Config loaded successfully")
        
        # 2. Test LLM initialization
        logger.info("Step 2: Initializing LLM...")
        llm = get_llm(config)
        logger.info(f"✓ LLM initialized: {llm.__class__.__name__}")
        
        # 3. Test Controller initialization
        logger.info("Step 3: Initializing Controller...")
        controller = Controller()
        logger.info("✓ Controller initialized")
        
        # 4. Test CamoufoxBrowserSession initialization
        logger.info("Step 4: Initializing CamoufoxBrowserSession...")
        profile = BrowserProfile(headless=False)
        browser_session = CamoufoxBrowserSession(browser_profile=profile)
        logger.info("✓ CamoufoxBrowserSession created")
        
        # 5. Test browser start
        logger.info("Step 5: Starting browser...")
        await browser_session.start()
        logger.info("✓ Browser started")
        
        # 6. Test Agent creation
        logger.info("Step 6: Creating Agent...")
        agent = Agent(
            task="Test task",
            llm=llm,
            controller=controller,
            browser_session=browser_session,
            source='cli',
        )
        logger.info("✓ Agent created successfully")
        
        # 7. Test basic agent operation
        logger.info("Step 7: Testing basic agent operation...")
        
        # Get current page
        page = await browser_session.get_current_page()
        logger.info(f"✓ Got current page: {page.url}")
        
        # Navigate somewhere
        await page.goto("https://www.google.com")
        logger.info("✓ Navigated to Google")
        
        # Get browser state
        state = await browser_session.get_state_summary(cache_clickable_elements_hashes=False)
        logger.info(f"✓ Got browser state: {state.url}")
        
        # 8. Test agent run
        logger.info("Step 8: Testing agent run...")
        logger.info("Creating a simple task...")
        
        # Update agent task
        agent.task = "Go to google.com and click on the search box"
        
        # Try to run one step
        logger.info("Running agent.step()...")
        await agent.step()
        logger.info("✓ Agent step completed")
        
        logger.info("\n✅ All debug steps passed! The agent initialization works.")
        logger.info("\nThe hanging issue might be in the TUI's event loop or message handling.")
        
        # Close browser
        await browser_session.close()
        
    except Exception as e:
        logger.error(f"\n❌ Debug failed at step: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    print("🔍 Running Camoufox TUI debug script...")
    success = asyncio.run(debug_tui())
    sys.exit(0 if success else 1) 