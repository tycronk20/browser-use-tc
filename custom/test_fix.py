#!/usr/bin/env python3
"""
test_fix.py
Quick test to verify the on_mount fix works
"""

import asyncio
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from camoufox_tui_fixed import CamoufoxBrowserUseApp
from browser_use.cli import load_user_config


def test_on_mount():
    """Test that on_mount method works correctly"""
    print("Testing on_mount method fix...")
    
    try:
        # Load config
        config = load_user_config()
        
        # Create app instance
        app = CamoufoxBrowserUseApp(config)
        
        # Try calling on_mount directly
        app.on_mount()
        
        print("✅ on_mount method works correctly!")
        return True
        
    except Exception as e:
        print(f"❌ on_mount test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_on_mount()
    
    if success:
        print("\n✅ Fix verified! You can now run:")
        print("   ./custom/camoufox-tui")
        print("   or")
        print("   python custom/camoufox_tui_fixed.py")
    else:
        print("\n❌ Fix verification failed. Check the error above.")
    
    sys.exit(0 if success else 1) 