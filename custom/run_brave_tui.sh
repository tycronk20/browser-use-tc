#!/bin/bash

# Close any existing Brave instances
echo "🔒 Closing any existing Brave instances..."
pkill -f "Brave Browser" 2>/dev/null

# Wait a moment for processes to close
sleep 2

# Set environment variables for Brave
export BROWSER_USE_EXECUTABLE_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# Run browser-use with Brave configuration
echo "🦁 Starting browser-use with Brave browser..."
echo "   Profile: ~/Library/Application Support/BraveSoftware/Brave-Browser"
echo ""

# Update the config to set executable_path
cat > /tmp/brave_browser_config.py << 'EOF'
import json
from pathlib import Path

config_file = Path.home() / ".config/browseruse/config.json"
config = json.loads(config_file.read_text())

# Update browser config
config["browser"]["executable_path"] = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
config["browser"]["headless"] = False

# Write back
config_file.write_text(json.dumps(config, indent=2))
print("✅ Config updated with Brave executable path")
EOF

python /tmp/brave_browser_config.py

# Run the browser-use CLI with Brave settings
python -m browser_use.cli \
    --user-data-dir "$HOME/Library/Application Support/BraveSoftware/Brave-Browser" \
    --profile-directory "Default"

# Clean up
rm -f /tmp/brave_browser_config.py
