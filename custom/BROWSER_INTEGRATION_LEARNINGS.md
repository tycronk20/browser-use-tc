# Browser Integration Learnings: Brave + Browser-Use

This document summarizes all learnings from integrating Brave browser with browser-use, which can be applied to future browser integrations (e.g., anti-detection browsers using juggler frames).

## 🔑 Key Discoveries

### 1. Browser-Use Architecture

#### Browser Session Initialization
- Browser-use uses the `BrowserSession` class to manage browser instances
- Key parameters:
  - `executable_path`: Path to the browser binary
  - `user_data_dir`: Browser profile directory
  - `profile_directory`: Specific profile within user_data_dir (e.g., "Default", "Profile 1")
  - `headless`: Boolean for headless/headful mode
  - `args`: List of browser-specific command-line arguments

#### Configuration Hierarchy
1. **Default config**: `~/.config/browseruse/config.json`
2. **CLI arguments**: Override config values
3. **Environment variables**: Can influence behavior
4. **BrowserSession parameters**: Direct instantiation

### 2. Profile Lock Issues

**Critical Learning**: Chromium-based browsers lock the profile directory when running.

#### Symptoms:
- "Opening in existing browser session" error
- `TargetClosedError: Target page, context or browser has been closed`
- Browser opens and immediately closes

#### Solutions:
1. Always close existing browser instances before launching
2. Use different profiles for manual browsing vs automation
3. Consider using temporary profiles (`user_data_dir=None`)

### 3. Browser-Use CLI Limitations

#### Available CLI Options (as of v0.2.5):
```bash
--version                  # Print version
--model TEXT              # LLM model selection
--thinking-budget INTEGER # For supported models
--debug                   # Verbose logging
--headless               # Run headless (flag, not option!)
--window-width INTEGER   
--window-height INTEGER  
--user-data-dir TEXT     # Browser profile location
--profile-directory TEXT # Profile name
--cdp-url TEXT          # CDP connection (not for direct launch)
-p, --prompt TEXT       # Single task execution
```

**Note**: No `--executable-path` CLI option! Must be set in config or BrowserSession.

### 4. Configuration Methods

#### Method 1: Direct Config Modification
```python
# Update ~/.config/browseruse/config.json
config['browser']['executable_path'] = '/path/to/browser'
config['browser']['user_data_dir'] = '/path/to/profile'
config['browser']['profile_directory'] = 'Default'
config['browser']['headless'] = False
```

#### Method 2: BrowserSession Parameters
```python
browser_session = BrowserSession(
    executable_path='/path/to/browser',
    user_data_dir='/path/to/profile',
    profile_directory='Default',
    headless=False,
    args=['--browser-specific-flags']
)
```

#### Method 3: Environment Variables
- Limited support
- Not all parameters can be set via env vars

### 5. TUI vs Task Mode

Browser-use has two distinct modes:

#### TUI Mode (Interactive)
- Creates its own BrowserSession
- Uses config from `~/.config/browseruse/config.json`
- Must NOT pre-create a browser session

#### Task Mode (--prompt)
- Can use pre-created BrowserSession
- Runs single task and exits
- Better for testing

### 6. Browser-Specific Arguments

#### Brave-Specific Args That Worked:
```python
args=[
    '--disable-brave-update',
    '--disable-brave-rewards-extension',
    '--disable-brave-news-today',
    '--disable-search-engine-choice-screen',
]
```

#### General Chromium Args (from browser_use/browser/profile.py):
- Extensive list of disabled features
- Security-related flags
- Automation detection prevention
- Performance optimizations

### 7. Common Pitfalls & Solutions

#### Pitfall 1: Creating Browser Session Before TUI
**Wrong**:
```python
browser_session = BrowserSession(...)
await browser_session.start()
await textual_interface(config)  # TUI has no browser!
```

**Right**:
```python
# Update config with browser settings
config['browser']['executable_path'] = '/path/to/browser'
# Let TUI create its own session
await textual_interface(config)
```

#### Pitfall 2: CDP vs Direct Launch Confusion
- CDP requires browser to be pre-launched with `--remote-debugging-port`
- Direct launch uses `executable_path` and launches fresh instance
- Don't mix CDP configuration with direct launch

#### Pitfall 3: Headless Flag Syntax
**Wrong**: `--headless false`
**Right**: Omit flag for headful, include `--headless` for headless

### 8. File Structure Best Practices

```
project/
├── run_browseruse_[browser].sh      # Simple bash wrapper
├── run_browseruse_[browser]_profile.py  # Advanced profile selector
├── [BROWSER]_PROFILE_SETUP.md      # Documentation
├── test_[browser]_browseruse.py    # Test script
└── browser_config_updater.py       # Config modification utility
```

### 9. Testing Approach

1. **Start Simple**: Test with a basic BrowserSession creation
2. **Verify Launch**: Check if browser process starts
3. **Test Navigation**: Simple navigate to example.com
4. **Test with Agent**: Full agent task execution
5. **Test TUI**: Interactive mode testing

### 10. Debugging Techniques

#### Process Monitoring:
```bash
ps aux | grep -i [browser_name]
lsof -i :9222  # For CDP connections
```

#### Config Verification:
```python
cat ~/.config/browseruse/config.json | jq .browser
```

#### Logging:
- Use `--debug` flag for verbose output
- Check browser logs in launch output
- Monitor `browser_use.log` if configured

## 🎯 Recommendations for New Browser Integration

### 1. Pre-Integration Research
- [ ] Identify browser's executable path
- [ ] Locate user data directory structure
- [ ] Understand profile organization
- [ ] Check for existing playwright/puppeteer support
- [ ] Document any special launch requirements (juggler frames, etc.)

### 2. Initial Implementation
1. Create simple test script with direct BrowserSession
2. Test browser launch without profiles first
3. Add profile support incrementally
4. Document all browser-specific arguments needed

### 3. Integration Patterns

#### Pattern A: Direct Launch (Recommended)
```python
BrowserSession(
    executable_path='/path/to/special/browser',
    user_data_dir='/path/to/profiles',
    args=['--special-browser-flags']
)
```

#### Pattern B: Custom Playwright Instance
```python
# For browsers with special playwright requirements
custom_playwright = await special_playwright().start()
BrowserSession(
    playwright=custom_playwright,
    browser=await custom_playwright.firefox.launch()  # or juggler
)
```

### 4. Configuration Strategy
1. Start with temporary profiles (`user_data_dir=None`)
2. Test with isolated test profile
3. Only use real profiles after confirming stability
4. Always provide profile cleanup/unlock utilities

### 5. Error Handling
- Expect profile lock issues
- Handle "browser already running" scenarios
- Provide clear error messages
- Include recovery procedures

## 📋 Checklist for New Browser

- [ ] Browser executable located and accessible
- [ ] Profile directory structure understood
- [ ] Test script created and working
- [ ] Browser-specific arguments documented
- [ ] Profile lock handling implemented
- [ ] Config update mechanism created
- [ ] CLI wrapper script created
- [ ] Documentation written
- [ ] Error scenarios tested
- [ ] TUI mode verified

## 🔧 Useful Code Snippets

### Profile Finder
```python
def find_browser_profiles(base_dir):
    """Find all profiles in a browser directory"""
    profiles = []
    local_state = base_dir / "Local State"
    if local_state.exists():
        data = json.loads(local_state.read_text())
        profile_info = data.get("profile", {}).get("info_cache", {})
        for name, info in profile_info.items():
            profiles.append({"directory": name, "name": info.get("name")})
    return profiles
```

### Safe Browser Launch
```python
async def safe_browser_launch(config):
    """Launch browser with error handling"""
    # Kill existing instances
    os.system(f'pkill -f "{browser_name}"')
    await asyncio.sleep(2)
    
    try:
        session = BrowserSession(**config)
        await session.start()
        return session
    except Exception as e:
        print(f"Launch failed: {e}")
        # Try without profile
        config['user_data_dir'] = None
        session = BrowserSession(**config)
        await session.start()
        return session
```

### Config Updater
```python
def update_browser_config(browser_path, profile_path):
    """Update browser-use config for new browser"""
    config_file = Path.home() / '.config/browseruse/config.json'
    config = json.loads(config_file.read_text())
    
    config['browser'].update({
        'executable_path': str(browser_path),
        'user_data_dir': str(profile_path),
        'headless': False,
        'profile_directory': 'Default'
    })
    
    # Remove CDP if present
    config['browser'].pop('cdp_url', None)
    
    config_file.write_text(json.dumps(config, indent=2))
```

## 🚀 Final Tips

1. **Start Simple**: Get basic launch working before adding complexity
2. **Document Everything**: Browser quirks, special arguments, profile structures
3. **Test Incrementally**: Browser → Profile → Agent → TUI
4. **Expect Issues**: Profile locks are common with all browsers
5. **Provide Utilities**: Scripts to unlock profiles, update configs, test connections

---

This knowledge should transfer well to integrating any browser with browser-use, including anti-detection browsers using specialized playwright adapters. 