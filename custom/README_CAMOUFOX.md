# Camoufox Browser Integration for browser-use

This directory contains a custom integration for using [Camoufox](https://github.com/daijro/camoufox) - a stealthy Firefox-based browser - with browser-use.

## What is Camoufox?

Camoufox is a privacy-focused browser based on Firefox that's designed to evade detection while web scraping or automating browser tasks. It includes:
- Built-in fingerprint spoofing
- GeoIP-based locale detection
- Human-like behavior patterns
- Stealth mode optimizations

## Known Issues and Solutions

### Tab Crashes on Major Websites

**📋 See [CAMOUFOX_DEBUG_SUMMARY.md](./CAMOUFOX_DEBUG_SUMMARY.md) for detailed debugging results and analysis.**

**Issue**: Tabs may crash when navigating to Google, YouTube, Bing, and other major websites.

**Cause**: This is caused by:
- Memory constraints with Camoufox's additional Firefox patches
- GPU/WebRender issues on macOS
- Firefox/Playwright version mismatches

**Solution**: The integration now includes comprehensive crash prevention measures:

1. **Automatic Fixes Applied**:
   - Disabled GPU acceleration with `--disable-gpu`
   - Set Firefox to use software rendering
   - Disabled process isolation (fission)
   - Limited content processes to reduce memory usage
   - Disabled custom theming

2. **If You Still Experience Crashes**, run the fixed debug script:
   ```bash
   # This script includes additional memory optimizations
   python custom/debug_camoufox_fixed.py
   ```

3. **Manual Fixes You Can Try**:
   ```bash
   # Increase memory limits on macOS
   launchctl limit maxproc 2048 2048
   
   # Disable content sandbox
   export MOZ_DISABLE_CONTENT_SANDBOX=1
   
   # Run with fixed version
   python custom/camoufox_tui_fixed.py
   ```

4. **For Extreme Cases**, use the debug script with maximum stability settings:
   ```python
   # The debug script automatically applies:
   firefox_user_prefs={
       "gfx.webrender.software": True,
       "fission.autostart": False,
       "dom.ipc.processCount": 2,
       "browser.tabs.remote.autostart": False,
       "media.hardware-video-decoding.enabled": False,
       "layers.acceleration.disabled": True,
       "gfx.canvas.accelerated": False,
   }
   launch_args=[
       "--disable-gpu",
       "--disable-webgl",
       "--disable-webassembly",
       "--safe-mode",
   ]
   ```

### TUI Agent Hanging Issue

**Issue**: The TUI agent hangs or doesn't start up after receiving a command.

**Cause**: This is due to async execution issues between the Textual UI event loop and the browser session initialization.

**Solution**: Use the fixed version of the TUI integration:

```bash
# Use the fixed version (recommended)
python custom/camoufox_tui_fixed.py

# Or run with debug logging to diagnose issues
DEBUG=1 ./custom/camoufox-tui
```

**Debugging Steps**:

1. **Run simple tests first**:
   ```bash
   python custom/test_camoufox_tui_simple.py
   ```

2. **Run enhanced debug tests**:
   ```bash
   python custom/debug_camoufox_tui_enhanced.py
   ```

3. **If tests pass but TUI still hangs**, use the fixed version:
   ```bash
   python custom/camoufox_tui_fixed.py
   ```

The fixed version includes:
- Proper async handling with context managers
- Browser session initialization before agent creation
- Better error handling and recovery
- Debug logging for troubleshooting

## Installation

1. First, install Camoufox with GeoIP support:
```bash
uv add 'camoufox[geoip]'
```

2. Make sure browser-use is installed:
```bash
uv add 'browser-use[cli]'
```

3. **macOS users**: If you encounter library conflicts, unlink NSS:
```bash
brew unlink nss
```

## Quick Start

1. **Test the integration**:
```bash
cd custom && python test_camoufox_tui_simple.py
```

2. **If tests pass, use the fixed TUI version**:
```bash
python custom/camoufox_tui_fixed.py
```

3. **Or for debugging, launch with debug mode**:
```bash
DEBUG=1 ./custom/camoufox-tui
```

4. **For basic browser automation**:
```bash
./custom/camoufox https://example.com
```

## Usage

### Basic Usage

Navigate to a URL:
```bash
./custom/camoufox https://example.com
```

Launch browser for manual testing:
```bash
./custom/camoufox
```

### Using with browser-use TUI (Fixed Version)

Launch the interactive browser-use TUI with Camoufox:
```bash
# Recommended - use the fixed version
python custom/camoufox_tui_fixed.py

# Or use the shell wrapper
./custom/camoufox-tui
```

This will start the browser-use Text User Interface (TUI) using Camoufox instead of Chromium. You can:
- Enter tasks for the AI agent to perform
- Watch the browser automation in real-time
- See detailed logs of the agent's actions
- Use all standard browser-use TUI features with Camoufox's stealth capabilities

**Note**: Make sure you have API keys configured in your `.env` file:
```env
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here
# or
GOOGLE_API_KEY=your-key-here
```

### From Python

```python
from custom.camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile

# Create a browser profile
profile = BrowserProfile(
    headless=False,  # Set to True for headless mode
    # Add other browser settings here
)

# Create and start the session
session = CamoufoxBrowserSession(browser_profile=profile)
await session.start()

# Get the current page and navigate
page = await session.get_current_page()
await page.goto("https://example.com")

# Close when done
await session.close()
```

### Advanced Usage with Agent

To use Camoufox with the browser-use Agent (requires API keys):

```python
from custom.camoufox_browser_session import CamoufoxBrowserSession
from browser_use import Agent
from langchain_openai import ChatOpenAI

# Create browser session
browser_session = CamoufoxBrowserSession(
    browser_profile=BrowserProfile(headless=False)
)

# Create agent with the custom browser
agent = Agent(
    task="Search for Python tutorials",
    llm=ChatOpenAI(model="gpt-4"),
    browser_session=browser_session
)

# Run the agent
await agent.run()
```

## Features

- **Stealth Mode**: Camoufox automatically applies anti-detection measures
- **GeoIP Support**: Automatic locale and timezone configuration based on IP
- **Firefox-based**: Uses Firefox engine instead of Chromium
- **Compatible**: Works with browser-use's existing API
- **Stable**: Custom theming disabled to prevent tab crashes

## Limitations

- User data directories are not yet supported (uses default profile)
- Some Chromium-specific permissions (like `clipboard-read`) may show warnings but don't affect functionality
- On macOS, NSS library conflicts may require unlinking NSS from Homebrew

## Troubleshooting

If you encounter issues:

1. **Tab crashes on major websites**: This has been fixed by disabling Camoufox's custom theming. If you still experience crashes, ensure you're using the latest version of this integration.

2. **TUI Agent Hanging**: Use the fixed version (`camoufox_tui_fixed.py`) which properly handles async execution. Run with `DEBUG=1` for detailed logging.

3. **Browser crashes on close**: This has been fixed in the latest version

4. **NSS Library Conflict (macOS)**: If you see errors like "Symbol not found: _PR_GMTParameters" or "XPCOMGlueLoad error":
   ```bash
   # Unlink NSS from Homebrew to avoid conflicts
   brew unlink nss
   ```
   
   **Note**: If you need NSS for other applications, you can relink it later:
   ```bash
   brew link nss
   ```

5. **Permissions warnings**: Firefox handles permissions differently than Chromium - these can be safely ignored:
   ```
   WARNING: Failed to grant browser permissions ['clipboard-read', 'clipboard-write', 'notifications']
   ```

6. **Hanging on startup**: Make sure you have the latest version of the integration and that NSS conflicts are resolved

7. **Validation errors in TUI**: These have been fixed in the latest version by properly handling None values in browser configuration

## Testing

To verify the integration is working:

```bash
# Test the basic functionality
cd custom && python test_camoufox_tui_simple.py

# Run enhanced debug tests
python custom/debug_camoufox_tui_enhanced.py

# If tests pass, use the fixed TUI version
python custom/camoufox_tui_fixed.py
```

## Files

- `camoufox` - Shell script wrapper for easy command-line usage
- `camoufox-tui` - Shell script wrapper for launching the TUI with Camoufox
- `camoufox_browser_session.py` - Python class implementing the BrowserSession interface for Camoufox
- `camoufox_tui.py` - Python script that integrates Camoufox with browser-use TUI
- `camoufox_tui_fixed.py` - Fixed version with better async handling (recommended)
- `test_camoufox_tui_simple.py` - Simple test script for basic functionality
- `debug_camoufox_tui_enhanced.py` - Enhanced debug script for troubleshooting
- `README_CAMOUFOX.md` - This documentation file