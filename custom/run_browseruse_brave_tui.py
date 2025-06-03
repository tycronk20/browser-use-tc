#!/usr/bin/env python3
"""
run_browseruse_brave_tui.py
Run browser-use TUI with Brave browser configuration
"""

import os
import sys
from pathlib import Path
from browser_use.cli import main as cli_main
import click

# Set Brave browser configuration as environment variables
os.environ['BROWSER_USE_EXECUTABLE_PATH'] = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
os.environ['BROWSER_USE_USER_DATA_DIR'] = str(Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser")

# Create a context with our Brave settings
ctx = click.Context(cli_main)
ctx.params = {
    'executable_path': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    'user_data_dir': str(Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser"),
    'profile_directory': 'Default',
    'headless': False,  # Force headful mode for Brave
}

# Run the CLI with our context
if __name__ == "__main__":
    print("🦁 Starting browser-use with Brave browser...")
    print("   Note: Make sure to close any existing Brave browser instances first!")
    print("")
    
    # Pass our custom args to the CLI
    sys.argv = [
        sys.argv[0],
        '--user-data-dir', str(Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser"),
        '--profile-directory', 'Default',
        '--window-width', '1280',
        '--window-height', '1024',
    ]
    
    # Add any additional arguments passed by the user
    if len(sys.argv) > 1:
        sys.argv.extend(sys.argv[1:])
    
    # Run the CLI
    cli_main() 