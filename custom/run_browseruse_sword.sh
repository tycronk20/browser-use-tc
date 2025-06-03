#!/bin/bash

# run_browseruse_sword.sh
# Connect browser-use to the existing sword Chrome instance via CDP

echo "Connecting browser-use to sword Chrome profile via CDP..."

# Remove any CDP URL config to ensure we can override it
sed -i '' '/"cdp_url":/d' ~/.config/browseruse/config.json 2>/dev/null || true

# Check if Chrome with CDP is running
if ! curl -s http://localhost:9222/json > /dev/null; then
    echo "Chrome with CDP not running. Starting sword Chrome..."
    ~/bin/sword
    sleep 3
    
    # Check again
    if ! curl -s http://localhost:9222/json > /dev/null; then
        echo "Failed to start Chrome with CDP. Please run ~/bin/sword manually first."
        exit 1
    fi
fi

echo "Chrome CDP server detected at localhost:9222"

# Run browser-use with CDP connection using the CLI module
python -m browser_use.cli --cdp-url http://localhost:9222 "$@" 