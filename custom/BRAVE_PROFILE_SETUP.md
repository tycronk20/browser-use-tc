# Brave Profile Setup for Browser-Use

This document describes how to use your normal Brave browser profile with browser-use WITHOUT using Chrome DevTools Protocol (CDP).

## Overview

Unlike the Chrome/sword setup that requires CDP, this implementation directly launches Brave with your existing profile using Playwright's `executable_path` and `user_data_dir` options. This approach:

- ✅ Uses your real Brave profile with all cookies, passwords, extensions
- ✅ Doesn't require moving profiles or special configurations
- ✅ Works with Brave's default security settings
- ✅ Supports multiple Brave profiles
- ❌ Cannot connect to an already-running Brave instance (no CDP)

## 🚀 Quick Start

### Simple Script (`run_browseruse_brave.sh`)

For basic usage with your default Brave profile:

```bash
# Run interactive TUI mode
./run_browseruse_brave.sh

# Run a specific task
./run_browseruse_brave.sh --prompt "Go to google.com and search for AI news"

# Run in headless mode
./run_browseruse_brave.sh --headless --prompt "Navigate to example.com"
```

### Advanced Script (`run_browseruse_brave_profile.py`)

For more control and profile selection:

```bash
# List all available Brave profiles
python run_browseruse_brave_profile.py --list-profiles

# Run with profile selection menu
python run_browseruse_brave_profile.py

# Run with a specific profile
python run_browseruse_brave_profile.py --profile "Profile 1"

# Run interactive TUI
python run_browseruse_brave_profile.py --interactive

# Run a task with a specific profile
python run_browseruse_brave_profile.py --profile "Default" --prompt "Check my Gmail"
```

## 🛠️ Technical Details

### How It Works

1. **Direct Launch**: Browser-use launches a new Brave process with your profile
2. **Profile Access**: Uses Brave's actual user data directory at `~/Library/Application Support/BraveSoftware/Brave-Browser`
3. **Full Integration**: All your bookmarks, extensions, saved passwords, and cookies are available
4. **No CDP Required**: Works without remote debugging, more secure

### Architecture

```
┌─────────────────┐          ┌──────────────────┐
│   browser-use   │────────►│   Brave Browser  │
│   (Python)      │ Launch   │   (New Process)  │
└─────────────────┘          └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────┐
                            │ ~/Library/...        │
                            │ /BraveSoftware/      │
                            │ /Brave-Browser/      │
                            │   ├── Default/       │
                            │   ├── Profile 1/     │
                            │   └── Local State   │
                            └──────────────────────┘
```

### Brave-Specific Configuration

The scripts include Brave-specific command line arguments:

```python
args=[
    '--disable-brave-update',        # Disable update checks
    '--disable-brave-rewards-extension',  # Disable rewards if not needed
    '--disable-brave-news-today',    # Disable news feature
    '--disable-search-engine-choice-screen',  # Skip search engine choice
]
```

## 📁 File Descriptions

### `run_browseruse_brave.sh`
- Simple bash script for quick usage
- Automatically finds your Brave installation and profile
- Creates a temporary Python script to handle the browser session
- Best for: Quick tasks with default profile

### `run_browseruse_brave_profile.py`
- Advanced Python script with profile management
- Can list and select from multiple Brave profiles
- Reads Brave's `Local State` file to find profile names
- Best for: Users with multiple profiles or needing more control

## ⚠️ Important Notes

### Profile Lock Warning
- **Cannot run if Brave is already open with the same profile**
- Brave locks the profile directory when in use
- You must close Brave before running browser-use with that profile

### Workarounds for Profile Lock:
1. **Use a different profile**: Create a dedicated Brave profile for automation
2. **Close Brave first**: Ensure no Brave processes are running
3. **Create a copy**: Use browser-use's profile copying feature (set `user_data_dir=None`)

### Security Considerations
- Your full browsing profile is accessible to the automation
- Be cautious when running untrusted tasks
- Consider using a separate profile for sensitive tasks

## 🔧 Troubleshooting

### "Profile is already in use" Error
```bash
# Check if Brave is running
ps aux | grep "Brave Browser"

# Kill all Brave processes (careful - saves will be lost)
pkill -f "Brave Browser"
```

### Profile Not Found
```bash
# Verify Brave profile location exists
ls -la ~/Library/Application\ Support/BraveSoftware/Brave-Browser/

# List available profiles
find ~/Library/Application\ Support/BraveSoftware/Brave-Browser -name "Profile*" -type d
```

### Extensions Not Working
Some extensions may not work in automation mode. This is a Playwright/Chromium limitation, not specific to Brave.

## 🎯 Use Cases

### Best For:
- Using saved logins and sessions
- Testing with real browser fingerprints
- Accessing sites that require specific extensions
- Working with bookmarks and saved data

### Not Ideal For:
- Running parallel browser instances (profile lock)
- Connecting to existing browser windows (no CDP)
- Headless automation with extensions

## 📚 Examples

### Example 1: Check Email with Saved Login
```bash
python run_browseruse_brave_profile.py --prompt "Go to gmail.com and check for new emails"
```

### Example 2: Use Specific Profile for Banking
```bash
python run_browseruse_brave_profile.py --profile "Banking" --prompt "Check account balance"
```

### Example 3: Interactive Session with Extensions
```bash
# This launches Brave with all your extensions loaded
python run_browseruse_brave_profile.py --interactive
```

---

**Status**: ✅ **Implementation Complete**  
**Tested With**: Brave 1.73.97, browser-use 0.2.5, macOS 14.7 