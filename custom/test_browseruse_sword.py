#!/usr/bin/env python3
"""
Test browser-use with the sword Chrome profile via CDP.
"""

import asyncio
from browser_use import Agent
from browser_use.browser.browser import Browser
from langchain_openai import ChatOpenAI
import os

async def test_browseruse_sword():
    """Test browser-use with sword Chrome via CDP."""
    
    print("Testing browser-use with sword Chrome via CDP...")
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("✗ OPENAI_API_KEY environment variable not set")
        print("Please set it or test with a different LLM")
        return
    
    try:
        # Create LLM
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # Connect to existing Chrome via CDP
        browser = Browser(
            config={
                "cdp_url": "http://localhost:9222",
                "headless": False,
            }
        )
        
        # Create agent with a simple task
        task = "Go to google.com and search for 'browser automation'"
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
        )
        
        print("✓ Agent created successfully")
        print(f"✓ Task: {task}")
        
        # Run the agent
        result = await agent.run()
        
        print("✓ Agent completed successfully!")
        print(f"✓ Result: {result}")
        
    except Exception as e:
        print(f"✗ Browser-use test failed: {e}")
        print("Make sure Chrome is running with: ~/bin/sword")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_browseruse_sword()) 