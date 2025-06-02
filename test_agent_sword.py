#!/usr/bin/env python3
"""
Test browser-use Agent with the sword Chrome profile via CDP using a local LLM.
"""

import asyncio
from browser_use import Agent
from browser_use.browser.session import BrowserSession
from langchain_ollama import ChatOllama
import os

async def test_agent_sword():
    """Test browser-use Agent with sword Chrome via CDP."""
    
    print("Testing browser-use Agent with sword Chrome via CDP...")
    
    try:
        # Use Ollama local LLM (no API key needed)
        llm = ChatOllama(
            model="llama3.1:8b",  # You can change this to any model you have locally
            temperature=0
        )
        
        # Connect to existing Chrome via CDP
        browser_session = BrowserSession(
            cdp_url="http://localhost:9222",
        )
        
        # Create agent with a simple task
        task = "Go to example.com and tell me what the page says"
        agent = Agent(
            task=task,
            llm=llm,
            browser_session=browser_session,
        )
        
        print("✓ Agent created successfully")
        print(f"✓ Task: {task}")
        
        # Run the agent
        result = await agent.run()
        
        print("✓ Agent completed successfully!")
        print(f"✓ Result summary: {len(str(result))} characters returned")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent test failed: {e}")
        print("Make sure:")
        print("  1. Chrome is running with: ~/bin/sword")
        print("  2. Ollama is running with llama3.1:8b model available")
        print("     (Run: ollama run llama3.1:8b)")
        return False

if __name__ == "__main__":
    asyncio.run(test_agent_sword()) 