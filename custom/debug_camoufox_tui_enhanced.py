#!/usr/bin/env python3
"""
debug_camoufox_tui_enhanced.py
Enhanced debug script to identify exactly where the TUI hangs
"""

import asyncio
import sys
import logging
import time
from pathlib import Path
from typing import Any

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
from browser_use.cli import load_user_config, get_llm, AgentSettings
from browser_use.controller.service import Controller
from browser_use.agent.service import Agent


class DebugAgent(Agent):
    """Debug wrapper for Agent to track execution"""
    
    async def run(self, *args, **kwargs):
        """Override run to add debug logging"""
        logger = logging.getLogger('debug_agent')
        logger.info("🚀 DebugAgent.run() called")
        
        try:
            # Call parent run with debug tracking
            logger.info("Starting parent Agent.run()...")
            result = await super().run(*args, **kwargs)
            logger.info("✓ Parent Agent.run() completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Error in Agent.run(): {e}", exc_info=True)
            raise
    
    async def step(self, *args, **kwargs):
        """Override step to add debug logging"""
        logger = logging.getLogger('debug_agent')
        logger.info("📍 DebugAgent.step() called")
        
        try:
            # Call parent step with debug tracking
            start_time = time.time()
            result = await super().step(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"✓ DebugAgent.step() completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            logger.error(f"❌ Error in Agent.step(): {e}", exc_info=True)
            raise


async def test_agent_execution_flow():
    """Test the exact flow of agent execution in the TUI"""
    logger = logging.getLogger('test_flow')
    
    logger.info("=" * 60)
    logger.info("Testing Agent Execution Flow")
    logger.info("=" * 60)
    
    config = None
    llm = None
    controller = None
    browser_session = None
    agent = None
    
    try:
        # 1. Load config
        logger.info("\n1️⃣ Loading configuration...")
        config = load_user_config()
        logger.info("✓ Config loaded")
        
        # 2. Get LLM
        logger.info("\n2️⃣ Initializing LLM...")
        llm = get_llm(config)
        logger.info(f"✓ LLM initialized: {llm.__class__.__name__}")
        
        # 3. Initialize Controller
        logger.info("\n3️⃣ Initializing Controller...")
        controller = Controller()
        logger.info("✓ Controller initialized")
        
        # 4. Create browser session
        logger.info("\n4️⃣ Creating CamoufoxBrowserSession...")
        profile = BrowserProfile(headless=False)
        browser_session = CamoufoxBrowserSession(browser_profile=profile)
        logger.info("✓ CamoufoxBrowserSession created")
        
        # 5. Start browser
        logger.info("\n5️⃣ Starting browser session...")
        await browser_session.start()
        logger.info("✓ Browser session started")
        
        # 6. Verify browser is working
        logger.info("\n6️⃣ Testing browser functionality...")
        page = await browser_session.get_current_page()
        await page.goto("https://www.google.com")
        logger.info(f"✓ Navigated to: {page.url}")
        
        # 7. Create agent (mimicking TUI behavior)
        logger.info("\n7️⃣ Creating Agent (as TUI does)...")
        agent_settings = AgentSettings.model_validate(config.get('agent', {}))
        
        agent = DebugAgent(
            task="Search for 'test' on Google",
            llm=llm,
            controller=controller,
            browser_session=browser_session,
            source='cli',
            **agent_settings.model_dump(),
        )
        logger.info("✓ Agent created")
        
        # 8. Test agent.run() with timeout
        logger.info("\n8️⃣ Testing agent.run() with 30s timeout...")
        logger.info("This is where the TUI might be hanging...")
        
        # Create a wrapper to run with timeout
        async def run_with_timeout():
            try:
                await asyncio.wait_for(agent.run(), timeout=30.0)
                logger.info("✅ agent.run() completed successfully!")
            except asyncio.TimeoutError:
                logger.error("❌ agent.run() TIMED OUT after 30 seconds!")
                logger.error("This is likely where the TUI is hanging.")
                raise
        
        await run_with_timeout()
        
        logger.info("\n✅ All tests passed! Agent execution works correctly.")
        return True
        
    except asyncio.TimeoutError:
        logger.error("\n⏱️ TIMEOUT DETECTED - Agent is hanging during execution")
        logger.error("Possible causes:")
        logger.error("1. Browser session not responding")
        logger.error("2. LLM API call hanging")
        logger.error("3. Controller action hanging")
        logger.error("4. Async deadlock in agent logic")
        return False
        
    except Exception as e:
        logger.error(f"\n❌ Test failed with error: {e}", exc_info=True)
        return False
        
    finally:
        # Cleanup
        logger.info("\n🧹 Cleaning up...")
        if browser_session:
            try:
                await browser_session.close()
                logger.info("✓ Browser session closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


async def test_tui_mimicry():
    """Test that mimics exactly what the TUI does when running a task"""
    logger = logging.getLogger('tui_mimicry')
    
    logger.info("=" * 60)
    logger.info("Testing TUI Task Execution Mimicry")
    logger.info("=" * 60)
    
    # This mimics the run_task method from BrowserUseApp
    logger.info("\nMimicking BrowserUseApp.run_task() behavior...")
    
    config = load_user_config()
    agent_settings = AgentSettings.model_validate(config.get('agent', {}))
    
    # Initialize components
    llm = get_llm(config)
    controller = Controller()
    browser_session = CamoufoxBrowserSession(browser_profile=BrowserProfile(headless=False))
    
    # Start browser
    await browser_session.start()
    
    # Create agent as TUI does
    agent = Agent(
        task="Search for Python tutorials",
        llm=llm,
        controller=controller,
        browser_session=browser_session,
        source='cli',
        **agent_settings.model_dump(),
    )
    
    # Simulate the async worker
    async def agent_task_worker():
        logger.info("📍 agent_task_worker() started")
        agent.running = True
        agent.last_response_time = 0
        
        try:
            logger.info("Calling agent.run()...")
            await agent.run()
            logger.info("✓ agent.run() completed")
        except Exception as e:
            logger.error(f"Error in agent.run(): {e}", exc_info=True)
        finally:
            agent.running = False
            logger.info("📍 agent_task_worker() finished")
    
    # Run with timeout
    try:
        await asyncio.wait_for(agent_task_worker(), timeout=30.0)
        logger.info("\n✅ TUI mimicry test passed!")
        return True
    except asyncio.TimeoutError:
        logger.error("\n❌ TUI mimicry test TIMED OUT!")
        return False
    finally:
        await browser_session.close()


async def main():
    """Run all debug tests"""
    logger = logging.getLogger('main')
    
    print("\n🔍 Running Enhanced Camoufox TUI Debug Tests")
    print("=" * 60)
    
    # Test 1: Basic agent execution flow
    logger.info("\n📋 Test 1: Agent Execution Flow")
    test1_passed = await test_agent_execution_flow()
    
    # Test 2: TUI mimicry
    if test1_passed:
        logger.info("\n📋 Test 2: TUI Task Execution Mimicry")
        test2_passed = await test_tui_mimicry()
    else:
        test2_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"  Test 1 (Agent Flow): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Test 2 (TUI Mimicry): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✅ All tests passed! The issue might be in the Textual UI event loop.")
        print("   Try running the TUI with additional logging to see where it hangs.")
    else:
        print("\n❌ Tests failed. Check the logs above to identify the hanging point.")
    
    return test1_passed and test2_passed


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 