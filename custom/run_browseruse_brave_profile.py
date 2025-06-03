#!/usr/bin/env python3
"""
run_browseruse_brave_profile.py
Run browser-use with Brave browser using a specific profile
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict

from browser_use import Agent, BrowserSession, BrowserProfile
from browser_use.cli import get_llm, load_user_config, textual_interface
from dotenv import load_dotenv

load_dotenv()

# Brave browser paths on macOS
BRAVE_USER_DATA_DIR = Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser"
BRAVE_EXECUTABLE = Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser")


def find_brave_profiles() -> List[Dict[str, str]]:
    """Find all available Brave profiles"""
    profiles = []
    
    if not BRAVE_USER_DATA_DIR.exists():
        return profiles
    
    # Read the Local State file to get profile information
    local_state_file = BRAVE_USER_DATA_DIR / "Local State"
    if local_state_file.exists():
        try:
            with open(local_state_file, 'r') as f:
                local_state = json.load(f)
                
            profile_info = local_state.get("profile", {}).get("info_cache", {})
            
            for profile_dir, info in profile_info.items():
                profiles.append({
                    "directory": profile_dir,
                    "name": info.get("name", profile_dir),
                    "gaia_name": info.get("gaia_name", ""),
                    "user_name": info.get("user_name", ""),
                })
        except Exception as e:
            print(f"Warning: Could not read profile information: {e}")
    
    # Always include Default profile
    if not any(p["directory"] == "Default" for p in profiles):
        profiles.insert(0, {
            "directory": "Default",
            "name": "Default Profile",
            "gaia_name": "",
            "user_name": "",
        })
    
    return profiles


def select_profile(profiles: List[Dict[str, str]]) -> str:
    """Let user select a profile"""
    if not profiles:
        print("No Brave profiles found!")
        return "Default"
    
    if len(profiles) == 1:
        return profiles[0]["directory"]
    
    print("\n🦁 Available Brave profiles:")
    for i, profile in enumerate(profiles, 1):
        name = profile["name"]
        if profile["gaia_name"]:
            name += f" ({profile['gaia_name']})"
        elif profile["user_name"]:
            name += f" ({profile['user_name']})"
        print(f"  {i}. {name} [{profile['directory']}]")
    
    while True:
        try:
            choice = input("\nSelect profile (1-{}): ".format(len(profiles)))
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                return profiles[idx]["directory"]
        except (ValueError, IndexError):
            pass
        print("Invalid selection. Please try again.")


async def run_brave_browseruse(
    profile_directory: str = "Default",
    prompt: Optional[str] = None,
    headless: bool = False,
    interactive: bool = False
):
    """Run browser-use with Brave browser"""
    
    # Check if Brave is installed
    if not BRAVE_EXECUTABLE.exists():
        print(f"❌ Error: Brave browser not found at: {BRAVE_EXECUTABLE}")
        print("Please install Brave browser from https://brave.com")
        sys.exit(1)
    
    # Check if user data directory exists
    if not BRAVE_USER_DATA_DIR.exists():
        print(f"❌ Error: Brave user data directory not found at: {BRAVE_USER_DATA_DIR}")
        print("Please ensure Brave browser has been run at least once.")
        sys.exit(1)
    
    print(f"\n🚀 Launching Brave browser...")
    print(f"   Executable: {BRAVE_EXECUTABLE}")
    print(f"   User Data: {BRAVE_USER_DATA_DIR}")
    print(f"   Profile: {profile_directory}")
    
    # Load user config for LLM settings
    config = load_user_config()
    llm = get_llm(config)
    
    # Create browser session with Brave
    browser_session = BrowserSession(
        executable_path=str(BRAVE_EXECUTABLE),
        user_data_dir=str(BRAVE_USER_DATA_DIR),
        profile_directory=profile_directory,
        headless=headless,
        disable_security=False,  # Keep security enabled for real browsing
        deterministic_rendering=False,
        # Brave-specific args
        args=[
            '--disable-brave-update',  # Disable update checks
            '--disable-brave-rewards-extension',  # Disable rewards extension
            '--disable-brave-news-today',  # Disable news
            '--disable-search-engine-choice-screen',  # Skip search engine choice
        ]
    )
    
    try:
        # Start the browser session
        await browser_session.start()
        print("✅ Brave browser started successfully!")
        
        if interactive and not prompt:
            # Run the TUI interface
            print("\n🎯 Starting interactive TUI mode...")
            await browser_session.close()
            await textual_interface(config)
        elif prompt:
            # Run a specific task
            print(f"\n📝 Running task: {prompt}")
            
            agent = Agent(
                task=prompt,
                llm=llm,
                browser_session=browser_session,
            )
            
            result = await agent.run()
            print(f"\n✅ Task completed!")
            print(f"📄 Result: {result}")
        else:
            # Just keep browser open
            print("\n🎯 Browser is ready! Press Ctrl+C to exit.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if not interactive or prompt:
            print("\n🔚 Closing browser...")
            await browser_session.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run browser-use with Brave browser"
    )
    parser.add_argument(
        "--profile", 
        help="Brave profile directory name (e.g., 'Default', 'Profile 1')"
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available Brave profiles"
    )
    parser.add_argument(
        "--prompt",
        help="Task to run (if not provided, opens interactive mode)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive TUI mode"
    )
    
    args = parser.parse_args()
    
    # List profiles if requested
    if args.list_profiles:
        profiles = find_brave_profiles()
        if not profiles:
            print("No Brave profiles found!")
        else:
            print("\n🦁 Brave profiles:")
            for profile in profiles:
                name = profile["name"]
                if profile["gaia_name"]:
                    name += f" ({profile['gaia_name']})"
                print(f"  • {name} [{profile['directory']}]")
        return
    
    # Select profile
    if args.profile:
        profile_directory = args.profile
    else:
        profiles = find_brave_profiles()
        if profiles:
            profile_directory = select_profile(profiles)
        else:
            profile_directory = "Default"
    
    # Run browser-use
    asyncio.run(run_brave_browseruse(
        profile_directory=profile_directory,
        prompt=args.prompt,
        headless=args.headless,
        interactive=args.interactive
    ))


if __name__ == "__main__":
    main() 