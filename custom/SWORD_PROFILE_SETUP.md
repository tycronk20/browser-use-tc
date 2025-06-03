# Sword Profile Setup for Browser-Use

This document describes the battle-tested setup for using the real "sword" Chrome profile (Profile 2) with browser-use via Chrome DevTools Protocol (CDP).

## Overview

Starting with Chrome 136, the `--remote-debugging-port` flag is ignored when Chrome uses its default data directory. This implementation moves the Chrome profile to a non-default location and creates a wrapper script for launching Chrome with CDP enabled.

## ✅ What Was Implemented

### 1. **One-time Profile Relocation**
- ✅ Moved entire Chrome directory from `~/Library/Application Support/Google/Chrome` to `~/chrome_sword`
- ✅ Preserves all profile data: cookies, passwords, extensions, bookmarks
- ✅ No data loss or corruption

### 2. **Chrome Launcher Script** (`~/bin/sword`)
```bash
#!/usr/bin/env bash
# Launch the real "sword" profile with CDP open.

PORT=9222                    # pick any free TCP port
open -n -a "Google Chrome" --args \
  --user-data-dir="$HOME/chrome_sword" \
  --profile-directory="Profile 2" \
  --remote-debugging-port=$PORT \
  --remote-debugging-address=127.0.0.1
```

### 3. **Browser-Use Connection Script** (`run_browseruse_sword.sh`)
```bash
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
```

### 4. **Test Scripts**
- ✅ `test_sword_connection.py` - Tests Playwright CDP connection
- ✅ `test_browseruse_simple.py` - Tests browser-use BrowserSession
- ✅ `test_agent_sword.py` - Tests full Agent with local LLM

## 🚀 Usage

### Daily Usage
```bash
# Launch Chrome with sword profile and CDP
~/bin/sword

# In another terminal, run browser-use tasks
./run_browseruse_sword.sh --prompt "Your task here"

# Or use the TUI interface
./run_browseruse_sword.sh
```

### Example Commands
```bash
# Simple navigation test
./run_browseruse_sword.sh --prompt "Go to google.com"

# Search task
./run_browseruse_sword.sh --prompt "Go to google.com and search for browser automation"

# Interactive TUI mode
./run_browseruse_sword.sh
```

## 🧪 Verification

All tests pass successfully:

### 1. **CDP Connection Test**
```bash
python test_sword_connection.py
```
Output:
```
✓ Successfully connected to Chrome via CDP
✓ Found 1 browser context(s)
✓ Using context with 1 page(s)
✓ Created new page
✓ Successfully navigated to example.com
✓ Page title: Example Domain
✓ Test page closed
✓ Connection test completed successfully!
```

### 2. **Browser-Use Session Test**
```bash
python test_browseruse_simple.py
```
Output:
```
✓ BrowserSession instance created
✓ BrowserSession connected via CDP
✓ New tab created
✓ Navigated to httpbin.org/get
✓ Page content loaded correctly
✓ Test page closed
✓ BrowserSession closed
🎉 All tests passed! Sword Chrome CDP connection is working!
```

### 3. **End-to-End Agent Test**
```bash
./run_browseruse_sword.sh --prompt "Go to google.com"
```
Result: ✅ **Task completed successfully** - "Successfully navigated to google.com"

## 🔧 Technical Details

### Why This Works
1. **Non-default data directory**: Chrome's security restrictions only apply to the default profile location
2. **Profile preservation**: Moving (not copying) preserves all Chrome profile locks and metadata
3. **CDP availability**: Chrome honors `--remote-debugging-port` when using non-default `--user-data-dir`
4. **Browser-use compatibility**: Uses standard BrowserSession with `cdp_url` parameter

### Architecture
```
┌─────────────────┐    CDP     ┌──────────────────┐
│   browser-use   ├──────────►│   Chrome CDP     │
│   (Python)      │:9222       │   (sword profile)│
└─────────────────┘            └──────────────────┘
                                        │
                                        ▼
                               ┌──────────────────┐
                               │ ~/chrome_sword/  │
                               │ Profile 2/       │
                               │ (all user data)  │
                               └──────────────────┘
```

### Benefits
- ✅ **Real profile**: Full access to saved logins, extensions, cookies
- ✅ **No interference**: Can browse manually while automation runs
- ✅ **Cloudflare-friendly**: Uses real Chrome signatures
- ✅ **Persistent**: Profile data persists between sessions
- ✅ **Safe**: No risk of profile corruption or data loss

## 📁 File Structure

```
/Users/yungkronos/
├── bin/
│   └── sword                          # Chrome launcher script
├── chrome_sword/                      # Relocated Chrome data
│   ├── Profile 2/                     # Sword profile data
│   ├── Default/                       # Other profiles
│   └── ...                            # Chrome metadata
└── browser-use/
    ├── run_browseruse_sword.sh        # Browser-use connector
    ├── test_sword_connection.py       # CDP test
    ├── test_browseruse_simple.py      # BrowserSession test
    └── test_agent_sword.py            # Agent test
```

## 🎯 Next Steps

The setup is complete and fully functional. You can now:

1. **Daily browsing**: Use `~/bin/sword` to launch Chrome with your profile
2. **Automation tasks**: Use `./run_browseruse_sword.sh` for browser-use tasks
3. **Manual + automation**: Run both simultaneously without conflicts
4. **Scale up**: Add more complex automation workflows as needed

## ⚠️ Important Notes

- **Always launch Chrome via `~/bin/sword`** to ensure CDP is available
- **Profile data is now in `~/chrome_sword/`** (moved from the default location)
- **Don't launch Chrome from Dock** - it will create a new empty profile in the old location
- **The setup is permanent** - no need to repeat the migration process

## 🔧 Troubleshooting

### Chrome won't start with CDP
```bash
# Check if port 9222 is in use
lsof -i :9222

# Force kill any Chrome processes
pkill -f "Google Chrome"

# Restart sword Chrome
~/bin/sword
```

### Browser-use can't connect
```bash
# Test CDP connection
curl http://localhost:9222/json

# Check browser-use config
cat ~/.config/browseruse/config.json

# Remove any conflicting CDP config
sed -i '' '/"cdp_url":/d' ~/.config/browseruse/config.json
```

### Profile data not loading
The profile should work immediately since it was moved (not copied). If issues persist:
1. Verify `~/chrome_sword/Profile 2/` contains your data
2. Check Chrome isn't creating a new profile in the old location
3. Ensure only one Chrome process is running

---

**Status**: ✅ **Implementation Complete and Tested**  
**Last Updated**: June 2, 2025  
**Tested With**: Chrome 136.0.7103.114, browser-use 0.2.4, macOS 14.7 