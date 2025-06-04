# Camoufox Tab Crash Debug Summary

## Issue Description
Tabs crash when navigating to major websites (Google, YouTube, Bing, DuckDuckGo) using Camoufox v0.4.11 on macOS, but simpler sites (example.com, httpbin.org, wikipedia.org) work fine.

## Root Cause
Based on testing and research, the crashes are caused by:
1. **Memory constraints**: Camoufox's additional Firefox patches consume ~100-150MB extra per tab
2. **GPU/WebRender issues**: macOS GPU sandbox conflicts with Camoufox's modifications
3. **Site complexity**: Sites with heavy JavaScript, WebGL, or anti-bot measures trigger the issues

## Testing Results

### Sites That Work ✅
- example.com
- httpbin.org
- wikipedia.org

### Sites That Crash ❌
- duckduckgo.com
- google.com
- youtube.com
- bing.com

## Implemented Fixes

### 1. Firefox Preferences (Partial Success)
```python
firefox_user_prefs = {
    "gfx.webrender.software": True,      # Use software rendering
    "fission.autostart": False,           # Disable process isolation
    "dom.ipc.processCount": 1,            # Minimize processes
    "browser.tabs.remote.autostart": False,
    "layers.acceleration.disabled": True,
    "gfx.canvas.accelerated": False,
}
```

### 2. Launch Arguments
```python
args = [
    "--disable-gpu",
    "--disable-webgl",
    "--disable-webassembly",
    "--safe-mode",
]
```

### 3. Environment Variables
```bash
export MOZ_DISABLE_CONTENT_SANDBOX=1
export MOZ_FORCE_DISABLE_E10S=1
export MOZ_WEBRENDER=0
```

### 4. Camoufox Options
```python
block_webgl=True
block_webrtc=True
disable_coop=True
```

## Recommendations

### Short-term Solutions

1. **Use for specific sites only**: Camoufox works well for simpler sites and API testing
2. **Headless mode**: Slightly more stable but still crashes on complex sites
3. **Site-specific workarounds**: Use alternative search engines or simpler interfaces

### Long-term Solutions

1. **Update Camoufox and Playwright**:
   ```bash
   pip install --upgrade playwright==1.52.2 camoufox==0.4.12b2
   playwright install firefox
   ```
   The v0.4.12 beta rebases on Firefox 127esr which may fix compatibility issues.

2. **Alternative: Use Playwright Firefox with stealth plugins**:
   Instead of Camoufox, use regular Firefox with playwright-extra stealth plugins for better stability.

3. **Wait for fixes**: The Camoufox maintainer is actively working on memory regression issues (see GitHub issues #245 and #279).

## Code to Use Right Now

For maximum stability with current version:

```python
from custom.camoufox_browser_session import CamoufoxBrowserSession
from browser_use.browser.profile import BrowserProfile

browser_session = CamoufoxBrowserSession(
    browser_profile=BrowserProfile(headless=False),
    firefox_user_prefs={
        "gfx.webrender.software": True,
        "fission.autostart": False,
        "dom.ipc.processCount": 1,
        "browser.tabs.remote.autostart": False,
        "layers.acceleration.disabled": True,
    },
    args=["--disable-gpu"],
    block_webgl=True,
    block_webrtc=True,
)
```

## Conclusion

The tab crashes are a known issue with Camoufox on macOS when dealing with complex websites. The implemented fixes improve stability for simpler sites but don't fully resolve crashes on major platforms like Google or DuckDuckGo. Consider using Camoufox only for specific use cases where its stealth features are essential and the target sites are known to work. 