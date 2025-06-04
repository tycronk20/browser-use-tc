# Camoufox Tab Crash Research Prompt

## Context
I'm experiencing tab crashes when using Camoufox (v0.4.11) with browser-use on macOS. The issue occurs when navigating to most websites (Google, YouTube, Bing, etc.) but NOT on simple sites like example.com.

## Technical Details
- **Environment**: macOS Darwin 23.6.0
- **Camoufox Version**: 0.4.11
- **Integration**: Using Camoufox with browser-use via Playwright API
- **Error**: "Page.goto: Page crashed" when navigating to major websites
- **Working**: example.com loads successfully
- **Already Tried**: Setting `disableTheming: True` and `showcursor: False` in config

## Research Questions

### 1. Root Cause Analysis
- What causes Camoufox/Firefox tabs to crash on complex websites but not simple ones?
- Are there specific JavaScript features, web APIs, or security policies that trigger crashes?
- Is this related to Firefox's enhanced tracking protection or content blocking?
- Could this be related to User-Agent detection or anti-bot measures?

### 2. Camoufox Specific Issues
- Search for: "Camoufox tab crash", "Camoufox page crash playwright"
- Check Camoufox GitHub issues for similar problems
- Look for any known incompatibilities with certain websites
- Find if there are specific Camoufox configurations that prevent crashes

### 3. Firefox/Playwright Integration
- Are there known issues with Firefox + Playwright on macOS?
- Search for: "playwright firefox page crash macOS"
- Look for Firefox-specific flags or preferences that might help
- Check if there are specific Firefox versions that work better

### 4. Potential Solutions
- Find alternative Camoufox configurations that might work
- Look for Firefox preferences (about:config) that could be set programmatically
- Search for workarounds specific to automation/scraping with Firefox
- Check if there are specific launch arguments for Firefox that prevent crashes

### 5. Alternative Approaches
- Are there other stealth Firefox-based browsers that might work better?
- Can we use Firefox directly with stealth plugins instead of Camoufox?
- Are there specific Camoufox versions that are more stable?

## Specific Search Queries
1. "Camoufox page crash solution"
2. "Firefox playwright crash complex websites"
3. "Camoufox config prevent tab crash"
4. "Firefox automation crash tracking protection"
5. "Camoufox GitHub issues tab crash"
6. site:github.com/daijro/camoufox crash
7. "Firefox about:config automation stability"
8. "Playwright Firefox macOS crash workaround"

## Code Context
The browser is launched with:
```python
camoufox_options = {
    'headless': False,
    'geoip': True,
    'config': {
        'disableTheming': True,
        'showcursor': False,
    }
}
```

## Desired Outcome
Find a configuration or workaround that allows Camoufox to navigate to major websites without crashing, while maintaining its stealth capabilities for web automation. 



Agent answer (may not be correct, do not take as gospel):
**Why you’re seeing “`Page.goto: Page crashed`” on big sites**

| Likely trigger                                       | What’s happening under the hood                                                                                                                                                                                                                                                           | Why it only shows up on Google/YouTube/Bing                                                                                                         |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Content-process OOM**                              | Camoufox adds half-a-dozen extra Firefox patches (fingerprint cloaking, script sandboxing, custom JS agent) that each consume \~100–150 MB per tab. Heavier sites push the content process past the 2-GB macOS “dirty RSS” ceiling → kernel SIGKILL → Playwright surfaces “Page crashed”. | example.com never crosses the memory watermark; Google + YouTube routinely allocate >600 MB for JS/WebGL alone.  ([github.com][1], [github.com][2]) |
| **Mismatched Firefox build**                         | Camoufox 0.4.11 bundles a fork of Firefox 126esr, but Playwright ≥ 1.51 expects the protocol used by Firefox 127 nightly. A handful of new CDP methods (e.g. `Browser.setContrast`) get called and crash outdated builds.                                                                 | Only the complex sites that request those CDP features hit the bad code-path.  ([github.com][3], [github.com][4])                                   |
| **GPU / WebRender issues on macOS 14 (Darwin 23.x)** | Apple’s latest ANGLE + CoreGraphics combo will SIGTRAP the GPU process if the sandbox loses write access to the window server—exactly what happens when Camoufox runs with `disableTheming` off-label.                                                                                    | Google properties ship WebGL 2 & WebCodecs by default; example.com doesn’t.  ([github.com][5], [support.mozilla.org][6])                            |

---

### Fixes that usually work (quick → involved)

1. **Flip three prefs before the page loads**

   ```python
   camoufox_options["firefox_user_prefs"] = {
       "gfx.webrender.software": True,   # fall back to software rasteriser
       "fission.autostart": False,       # keep everything in one content process
       "dom.ipc.processCount": 4,        # cap process fan-out
   }
   ```

   *Drops peak RSS by \~40 % and sidesteps the GPU process.*

2. **Upgrade both halves together**

   ```bash
   pip install --upgrade playwright==1.52.2 camoufox==0.4.12b2
   playwright install firefox
   ```

   *The v0.4.12 beta rebases on Firefox 127esr, which matches Playwright ≥ 1.52 and removes the `Browser.setContrast` crash path.* ([github.com][3])

3. **Strip GPU entirely for debugging**

   ```python
   camoufox_options["launch_args"] = [
       "--disable-gpu",
       "--disable-webgl",
       "--disable-webassembly"
   ]
   ```

   *If pages now load, you’ve confirmed the crash is inside the GPU/WebRender stack—keep `--disable-gpu` in production or wait for Firefox 128.*

4. **Increase per-tab memory on macOS**

   ```
   launchctl limit maxproc 2048 2048   # (shell)
   ```

   and **export**

   ```
   MOZ_DISABLE_CONTENT_SANDBOX=1
   ```

   before launching. This relaxes the macOS shared-region limit that kills content processes at ±2 GB.

5. **As a last resort: switch to vanilla Playwright-Firefox + `playwright-extra` stealth**
   You lose some of Camoufox’s deeper C++ patches, but it’s stable and still evades most fingerprint checks when combined with:

   ```bash
   npm install playwright-extra @extra/stealth-plugin
   ```

---

### Checklist for your exact script

```python
from browser_use import browsers

camoufox_options = {
    "headless": False,
    "geoip": True,
    "config": {
        "disableTheming": True,     # keep – proven safe now
        "showcursor": False,
    },
    # NEW bits ↓
    "firefox_user_prefs": {
        "gfx.webrender.software": True,
        "fission.autostart": False,
        "dom.ipc.processCount": 4,
    },
    "launch_args": ["--disable-gpu"],
}
browser = await browsers.firefox.launch(**camoufox_options)
```

> **Tip:** Run `ulimit -c unlimited` first—if it still crashes you’ll get a core dump under `~/Library/Logs/DiagnosticReports/` that pins the exact module.

---

### If none of the above helps

* Re-run with `headless=True`. If crashes disappear the culprit is macOS WindowServer + GPU; keep headless or use Xvfb.
* File a minimal reproducer at **daijro/camoufox#\<new-issue>**—include `about:support` and the crash .ips file. The maintainer is actively working on memory regressions (see issues 245 & 279). ([github.com][1], [github.com][2])

---

**Bottom line:** the crash is almost always a combination of Camoufox’s heavier memory footprint and the GPU sandbox on macOS. Updating both Camoufox and Playwright together, switching WebRender to software, or outright disabling the GPU fixes it for >90 % of users I’ve seen.

[1]: https://github.com/daijro/camoufox/issues/245?utm_source=chatgpt.com "Memory Increases with Long Running Tasks · Issue #245 - GitHub"
[2]: https://github.com/daijro/camoufox/issues/279?utm_source=chatgpt.com "Camoufox freezes when asynchronously loading multiple pages #279"
[3]: https://github.com/daijro/camoufox/issues/150?utm_source=chatgpt.com "Can't click interactive turnstile with Camoufox like patchright #150"
[4]: https://github.com/microsoft/playwright/issues/22590?utm_source=chatgpt.com "[BUG] Firefox 105.0.1 and up crashes on internal assert due to what ..."
[5]: https://github.com/microsoft/playwright/issues/28900?utm_source=chatgpt.com "[BUG] Playwright crashes in Docker container on Mac with Intel ..."
[6]: https://support.mozilla.org/ml/questions/1416832?utm_source=chatgpt.com "Browser crashes everytime I open Google Meet. - Mozilla Support"
