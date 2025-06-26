#!/bin/bash

# run_browseruse_brave.sh
# Run browser-use with Brave browser using your normal profile

echo "Setting up browser-use with Brave browser..."

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the user's home directory
USER_HOME="$HOME"

# Brave's default profile location on macOS
BRAVE_USER_DATA_DIR="$USER_HOME/Library/Application Support/BraveSoftware/Brave-Browser"

# Check if Brave user data directory exists
if [ ! -d "$BRAVE_USER_DATA_DIR" ]; then
    echo "Error: Brave user data directory not found at: $BRAVE_USER_DATA_DIR"
    echo "Please ensure Brave browser is installed and has been run at least once."
    exit 1
fi

# Brave executable path on macOS
BRAVE_EXECUTABLE="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# Check if Brave is installed
if [ ! -f "$BRAVE_EXECUTABLE" ]; then
    echo "Error: Brave browser not found at: $BRAVE_EXECUTABLE"
    echo "Please install Brave browser from https://brave.com"
    exit 1
fi

echo "Found Brave browser at: $BRAVE_EXECUTABLE"
echo "Using Brave profile from: $BRAVE_USER_DATA_DIR"

# Create a temporary Python script to run browser-use with Brave
TEMP_SCRIPT=$(mktemp /tmp/browseruse_brave_XXXXXX.py)

cat > "$TEMP_SCRIPT" << 'EOF'
import asyncio
import sys
import os
from pathlib import Path

# Get the browser-use directory (passed as first argument)
browser_use_dir = sys.argv[1]
sys.path.insert(0, browser_use_dir)

# Now import from browser_use
from browser_use import Agent, BrowserSession, BrowserProfile
from browser_use.cli import get_llm, load_user_config, textual_interface, update_config_with_click_args
from dotenv import load_dotenv
import click

# Load .env from the browser-use directory
load_dotenv(os.path.join(browser_use_dir, '.env'))

async def main(prompt=None, headless=False):
    # Load user config for LLM settings
    config = load_user_config()
    
    # Get command line arguments
    brave_executable = sys.argv[2]
    brave_user_data_dir = sys.argv[3]
    
    if prompt:
        # Task mode - create browser session and run the task
        print(f"\n🚀 Launching Brave browser...")
        print(f"   Executable: {brave_executable}")
        print(f"   Profile: {brave_user_data_dir}")
        
        # Get LLM from config
        llm = get_llm(config)
        
        # Create browser session with Brave
        browser_session = BrowserSession(
            executable_path=brave_executable,
            user_data_dir=brave_user_data_dir,
            profile_directory="Default",  # Use the default profile
            headless=headless,
            disable_security=False,  # Keep security enabled for real browsing
            deterministic_rendering=False,
            # Brave-specific args to ensure it works properly
            args=[
                '--disable-brave-update',  # Disable update checks
                '--disable-brave-rewards',  # Disable rewards if not needed
                '--disable-brave-news',  # Disable news if not needed
            ]
        )
        
        try:
            # Start the browser session
            await browser_session.start()
            print("✅ Brave browser started successfully!")
            
            # If a prompt was provided, run it
            print(f"\n📝 Running task: {prompt}")
            
            agent = Agent(
                task=prompt,
                llm=llm,
                browser_session=browser_session,
            )
            
            result = await agent.run()
            print(f"\n✅ Task completed!")
            print(f"📄 Result: {result}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            print("\n🔚 Closing browser...")
            await browser_session.close()
    else:
        # Interactive mode - update config with Brave settings and run TUI
        print("\n🎯 Starting interactive TUI mode with Brave browser...")
        
        # Create a mock click context to pass our browser settings
        ctx = click.Context(click.Command('main'))
        ctx.params = {
            'user_data_dir': brave_user_data_dir,
            'executable_path': brave_executable,
            'profile_directory': 'Default',
        }
        
        # Update config with our Brave settings
        config = update_config_with_click_args(config, ctx)
        
        # Save the config so TUI will use these settings
        from browser_use.cli import save_user_config
        save_user_config(config)
        
        # Run the TUI - it will create its own browser session with our config
        await textual_interface(config)

if __name__ == "__main__":
    # Parse command line arguments (starting from argv[4])
    prompt = None
    headless = False
    
    for i in range(4, len(sys.argv)):
        if sys.argv[i] == "--prompt" and i + 1 < len(sys.argv):
            prompt = sys.argv[i + 1]
        elif sys.argv[i] == "--headless":
            headless = True
    
    asyncio.run(main(prompt=prompt, headless=headless))
EOF

# Change to the browser-use directory before running
cd "$SCRIPT_DIR"

# Run the Python script with Brave configuration
if [ "$#" -eq 0 ]; then
    # No arguments - run interactive mode
    python "$TEMP_SCRIPT" "$SCRIPT_DIR" "$BRAVE_EXECUTABLE" "$BRAVE_USER_DATA_DIR"
else
    # Pass all arguments to the Python script
    python "$TEMP_SCRIPT" "$SCRIPT_DIR" "$BRAVE_EXECUTABLE" "$BRAVE_USER_DATA_DIR" "$@"
fi

# Clean up temp file
rm -f "$TEMP_SCRIPT" 