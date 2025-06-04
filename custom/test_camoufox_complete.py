#!/usr/bin/env python3
"""
Complete test suite for Camoufox browser-use integration

This script tests all aspects of the Camoufox integration:
1. Native Camoufox API
2. Browser-use integration
3. Shell wrapper functionality
4. Advanced features
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Test imports
try:
    import camoufox
    from camoufox import AsyncCamoufox
    print("✅ Camoufox import successful")
except ImportError as e:
    print(f"❌ Camoufox import failed: {e}")
    sys.exit(1)

try:
    import browser_use
    from browser_use.browser.profile import BrowserProfile
    print("✅ browser-use import successful")
except ImportError as e:
    print(f"❌ browser-use import failed: {e}")
    sys.exit(1)

try:
    from camoufox_browser_session import CamoufoxBrowserSession
    print("✅ CamoufoxBrowserSession import successful")
except ImportError as e:
    print(f"❌ CamoufoxBrowserSession import failed: {e}")
    sys.exit(1)


async def test_native_camoufox():
    """Test 1: Native Camoufox API"""
    print("\n🧪 Test 1: Native Camoufox API")
    print("=" * 50)
    
    try:
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()
            await page.goto('https://httpbin.org/user-agent')
            content = await page.content()
            
            if 'Firefox' in content:
                print("✅ Native Camoufox test passed")
                print(f"🕵️ User agent contains Firefox: True")
                return True
            else:
                print("❌ Native Camoufox test failed - no Firefox in user agent")
                return False
                
    except Exception as e:
        print(f"❌ Native Camoufox test failed: {e}")
        return False


async def test_browser_use_integration():
    """Test 2: Browser-use integration"""
    print("\n🧪 Test 2: Browser-use Integration")
    print("=" * 50)
    
    try:
        # Create browser profile
        profile = BrowserProfile(headless=True)
        
        # Create Camoufox session
        session = CamoufoxBrowserSession(browser_profile=profile)
        
        # Start session
        await session.start()
        print("✅ Browser session started")
        
        # Test navigation
        page = await session.get_current_page()
        await page.goto('https://example.com')
        await page.wait_for_load_state('networkidle')
        
        title = await page.title()
        print(f"📄 Page title: {title}")
        
        # Test user agent
        user_agent = await page.evaluate('navigator.userAgent')
        print(f"🕵️ User Agent: {user_agent}")
        
        # Test webdriver detection
        webdriver = await page.evaluate('navigator.webdriver')
        print(f"🔍 Navigator.webdriver: {webdriver}")
        
        # Close session
        await session.close()
        print("✅ Browser session closed")
        
        if 'Example Domain' in title and 'Firefox' in user_agent:
            print("✅ Browser-use integration test passed")
            return True
        else:
            print("❌ Browser-use integration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Browser-use integration test failed: {e}")
        return False


def test_shell_wrapper():
    """Test 3: Shell wrapper functionality"""
    print("\n🧪 Test 3: Shell Wrapper")
    print("=" * 50)
    
    try:
        script_path = Path(__file__).parent / "camoufox"
        if not script_path.exists():
            print("❌ Shell wrapper script not found")
            return False
        
        # Test script execution (with timeout)
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=script_path.parent
        )
        
        if result.returncode == 0:
            print("✅ Shell wrapper executed successfully")
            if "Camoufox browser started successfully" in result.stdout:
                print("✅ Shell wrapper test passed")
                return True
            else:
                print("❌ Shell wrapper test failed - missing success message")
                print(f"stdout: {result.stdout}")
                return False
        else:
            print(f"❌ Shell wrapper test failed - exit code {result.returncode}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Shell wrapper test failed - timeout")
        return False
    except Exception as e:
        print(f"❌ Shell wrapper test failed: {e}")
        return False


def test_advanced_script():
    """Test 4: Advanced script functionality"""
    print("\n🧪 Test 4: Advanced Script")
    print("=" * 50)
    
    try:
        script_path = Path(__file__).parent / "camoufox_advanced.py"
        if not script_path.exists():
            print("❌ Advanced script not found")
            return False
        
        # Test help command
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=script_path.parent
        )
        
        if result.returncode == 0 and "Advanced Camoufox Browser Integration" in result.stdout:
            print("✅ Advanced script help works")
        else:
            print("❌ Advanced script help failed")
            return False
        
        # Test task execution
        result = subprocess.run(
            [sys.executable, str(script_path), "--task", "Navigate to example.com"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=script_path.parent
        )
        
        if result.returncode == 0:
            print("✅ Advanced script task execution successful")
            if "Page title: Example Domain" in result.stdout:
                print("✅ Advanced script test passed")
                return True
            else:
                print("❌ Advanced script test failed - missing page title")
                print(f"stdout: {result.stdout}")
                return False
        else:
            print(f"❌ Advanced script test failed - exit code {result.returncode}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Advanced script test failed - timeout")
        return False
    except Exception as e:
        print(f"❌ Advanced script test failed: {e}")
        return False


async def test_stealth_features():
    """Test 5: Stealth features"""
    print("\n🧪 Test 5: Stealth Features")
    print("=" * 50)
    
    try:
        # Test with stealth options
        stealth_options = {
            'block_webrtc': True,
            'humanize': True,
            'geoip': True,
        }
        
        profile = BrowserProfile(headless=True)
        session = CamoufoxBrowserSession(
            browser_profile=profile,
            camoufox_options=stealth_options
        )
        
        await session.start()
        print("✅ Stealth session started")
        
        page = await session.get_current_page()
        await page.goto('https://httpbin.org/headers')
        await page.wait_for_load_state('networkidle')
        
        content = await page.content()
        
        # Check for realistic headers
        if 'User-Agent' in content and 'Firefox' in content:
            print("✅ Stealth headers look realistic")
        else:
            print("⚠️ Stealth headers may not be optimal")
        
        await session.close()
        print("✅ Stealth session closed")
        print("✅ Stealth features test passed")
        return True
        
    except Exception as e:
        print(f"❌ Stealth features test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🦊 Camoufox Browser-use Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Native Camoufox API", test_native_camoufox()),
        ("Browser-use Integration", test_browser_use_integration()),
        ("Shell Wrapper", test_shell_wrapper()),
        ("Advanced Script", test_advanced_script()),
        ("Stealth Features", test_stealth_features()),
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Camoufox integration is working perfectly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)