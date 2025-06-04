# Camoufox Browser Integration for browser-use

This directory contains a complete integration of Camoufox browser with the browser-use framework, providing stealth browsing capabilities with anti-detection features.

## 🎯 Overview

Camoufox is a Firefox-based browser designed for web automation with built-in anti-detection features. This integration allows you to use Camoufox as the browser backend for browser-use instead of the default Chromium.

## 📁 Files

- `camoufox_browser_session.py` - Core integration class extending BrowserSession
- `camoufox` - Shell wrapper script (similar to Brave integration pattern)
- `camoufox_advanced.py` - Advanced Python script with CLI interface
- `test_camoufox_browseruse_v2.py` - Test script for the integration
- `test_camoufox_native.py` - Test script for native Camoufox API
- `CAMOUFOX_INTEGRATION.md` - This documentation file

## 🚀 Quick Start

### Prerequisites

1. Install Camoufox:
```bash
pip install 'camoufox[geoip]'
```

2. Install browser-use:
```bash
pip install 'browser-use[cli]'
```

### Basic Usage

1. **Shell wrapper (simplest)**:
```bash
./camoufox
```

2. **Advanced Python script**:
```bash
python camoufox_advanced.py --task "Navigate to example.com"
python camoufox_advanced.py --gui --stealth-mode
python camoufox_advanced.py --interactive
```

3. **Direct Python integration**:
```python
from camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile

# Create session
profile = BrowserProfile(headless=True)
session = CamoufoxBrowserSession(browser_profile=profile)

# Start browser
await session.start()

# Use with browser-use
page = await session.get_current_page()
await page.goto("https://example.com")
```

## 🔧 Features

### ✅ Working Features

- **Browser Session Integration**: Full compatibility with browser-use BrowserSession API
- **Headless/GUI Mode**: Support for both headless and GUI operation
- **Stealth Features**: Built-in anti-detection capabilities from Camoufox
- **Navigation**: Standard web navigation and page interaction
- **Playwright Compatibility**: Uses Playwright Firefox under the hood
- **Custom Options**: Support for Camoufox-specific configuration options

### ⚠️ Known Limitations

- **User Data Directory**: Custom profile directories not yet supported (Firefox persistent context complexity)
- **Clipboard Permissions**: Some Firefox permissions not available (warning only, doesn't affect functionality)
- **LLM Agent Integration**: Requires API keys for full agent capabilities

### 🔮 Future Enhancements

- **Profile Management**: Support for custom user data directories and persistent contexts
- **Enhanced Stealth**: More anti-detection configuration options
- **Agent Templates**: Pre-configured agent setups for common tasks
- **Performance Optimization**: Better resource management and startup times

## 🛠️ Technical Details

### Architecture

The integration follows the browser-use extension pattern:

1. **CamoufoxBrowserSession** extends the base `BrowserSession` class
2. **Custom Browser Setup**: Overrides `setup_new_browser_context()` to use Camoufox instead of Chromium
3. **Playwright Integration**: Leverages Camoufox's Playwright Firefox backend
4. **Session Management**: Maintains compatibility with browser-use session lifecycle

### Key Implementation Details

```python
class CamoufoxBrowserSession(BrowserSession):
    def __init__(self, browser_profile: BrowserProfile, camoufox_options: dict = None):
        # Extract camoufox_options before calling super().__init__
        self.camoufox_options = camoufox_options or {}
        super().__init__(browser_profile=browser_profile)
    
    async def setup_new_browser_context(self):
        # Use Camoufox instead of Chromium
        self._camoufox_instance = AsyncCamoufox(**camoufox_options)
        await self._camoufox_instance.__aenter__()
        self.browser = self._camoufox_instance.browser
```

### Stealth Configuration

Camoufox provides built-in stealth features:

```python
camoufox_options = {
    'headless': True,
    'block_webrtc': True,      # Block WebRTC leaks
    'humanize': True,          # Human-like behavior
    'geoip': True,            # Realistic geolocation
    'screen': (1920, 1080),   # Common screen resolution
}
```

## 🧪 Testing

### Run Tests

```bash
# Test native Camoufox API
python test_camoufox_native.py

# Test browser-use integration
python test_camoufox_browseruse_v2.py

# Test shell wrapper
./camoufox

# Test advanced features
python camoufox_advanced.py --help
```

### Expected Output

```
✅ Browser started successfully!
📝 Testing basic browser navigation...
✅ Successfully navigated to example.com
📄 Page title: Example Domain
🕵️ User Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0
🔍 Navigator.webdriver: False
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**: Make sure Camoufox is installed with `pip install 'camoufox[geoip]'`
2. **Permission Warnings**: Firefox permission warnings are normal and don't affect functionality
3. **Profile Errors**: User data directory support is not yet implemented, use default profiles
4. **GTK Errors**: On Linux, ensure GTK libraries are installed for GUI mode

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Reference

### CamoufoxBrowserSession

```python
class CamoufoxBrowserSession(BrowserSession):
    def __init__(
        self,
        browser_profile: BrowserProfile,
        camoufox_options: dict = None
    ):
        """
        Initialize Camoufox browser session.
        
        Args:
            browser_profile: Standard browser-use profile
            camoufox_options: Camoufox-specific options
        """
```

### Camoufox Options

Common options for `camoufox_options`:

```python
{
    'headless': bool,          # Headless mode
    'block_webrtc': bool,      # Block WebRTC
    'block_images': bool,      # Block images
    'humanize': bool,          # Human-like behavior
    'geoip': bool,            # Realistic geolocation
    'screen': tuple,          # Screen resolution (width, height)
    'proxy': dict,            # Proxy configuration
}
```

## 🤝 Contributing

To extend this integration:

1. **Add Features**: Extend `CamoufoxBrowserSession` class
2. **Improve Stealth**: Add more anti-detection options
3. **Profile Support**: Implement user data directory handling
4. **Agent Integration**: Create pre-configured agent templates

## 📄 License

This integration follows the same license as the browser-use project.

## 🔗 Related Links

- [Camoufox Documentation](https://github.com/daijro/camoufox)
- [browser-use Documentation](https://github.com/browser-use/browser-use)
- [Playwright Firefox](https://playwright.dev/docs/browsers#firefox)

---

**Status**: ✅ Working Integration  
**Last Updated**: 2025-06-04  
**Tested With**: Camoufox v0.4.11, browser-use v0.2.5