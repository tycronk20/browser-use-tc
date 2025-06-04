#!/usr/bin/env python3
"""
camoufox_browser_session.py
Custom BrowserSession that uses Camoufox instead of Chromium
"""

import logging
from typing import Self
from pathlib import Path

from browser_use.browser.session import BrowserSession
from browser_use.browser.profile import BrowserProfile
from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class CamoufoxBrowserSession(BrowserSession):
    """
    Custom BrowserSession that uses Camoufox browser instead of Chromium.
    
    Camoufox is a stealthy Firefox-based browser designed for automation.
    """
    
    def __init__(self, **kwargs):
        # Extract Camoufox-specific options before calling super().__init__
        camoufox_geoip = kwargs.pop('geoip', True)
        camoufox_addons = kwargs.pop('addons', None)
        camoufox_fonts = kwargs.pop('fonts', None)
        camoufox_screen = kwargs.pop('screen', None)
        camoufox_os = kwargs.pop('os', None)
        
        # Extract additional stability options
        block_webgl = kwargs.pop('block_webgl', None)
        block_webrtc = kwargs.pop('block_webrtc', None)
        disable_coop = kwargs.pop('disable_coop', None)
        
        # Extract Firefox-specific preferences and args for stability
        firefox_user_prefs = kwargs.pop('firefox_user_prefs', {})
        args = kwargs.pop('args', [])
        
        # Initialize parent with remaining kwargs
        super().__init__(**kwargs)
        
        # Store Camoufox options after parent initialization
        self.camoufox_options = {
            'geoip': camoufox_geoip,
            'addons': camoufox_addons,
            'fonts': camoufox_fonts,
            'screen': camoufox_screen,
            'os': camoufox_os,
        }
        
        # Add stability options if provided
        if block_webgl is not None:
            self.camoufox_options['block_webgl'] = block_webgl
        if block_webrtc is not None:
            self.camoufox_options['block_webrtc'] = block_webrtc
        if disable_coop is not None:
            self.camoufox_options['disable_coop'] = disable_coop
        
        # Store Firefox preferences and args
        self.firefox_user_prefs = firefox_user_prefs
        self.args = args
        
        # Store Camoufox instance
        self._camoufox_instance = None
    
    async def setup_new_browser_context(self) -> None:
        """Override to use Camoufox instead of Playwright's chromium"""
        
        # Check if we already have a browser context from parent's setup
        if self.browser_context:
            logger.info("Browser context already exists, skipping Camoufox setup")
            return
        
        logger.info(f'🦊 Launching Camoufox browser headless={self.browser_profile.headless}')
        
        # Default Firefox preferences to prevent crashes
        default_firefox_prefs = {
            "gfx.webrender.software": True,    # Fall back to software rasterizer
            "fission.autostart": False,         # Keep everything in one content process
            "dom.ipc.processCount": 4,          # Cap process fan-out
        }
        
        # Merge user preferences with defaults
        firefox_prefs = {**default_firefox_prefs, **self.firefox_user_prefs}
        
        # Default launch arguments to prevent GPU crashes
        default_launch_args = ["--disable-gpu"]
        
        # Combine launch args
        launch_args = list(set(default_launch_args + self.args))
        
        # Prepare Camoufox launch options
        camoufox_options = {
            'headless': self.browser_profile.headless,
            **self.camoufox_options,
            # Disable custom theming to prevent tab crashes on major websites
            'config': {
                'disableTheming': True,  # Use standard Firefox UI
                'showcursor': False,     # Disable the red cursor indicator
            },
            # Add Firefox preferences and launch args
            'firefox_user_prefs': firefox_prefs,
            'args': launch_args,
        }
        
        # Add proxy if specified
        if hasattr(self.browser_profile, 'proxy') and self.browser_profile.proxy:
            camoufox_options['proxy'] = self.browser_profile.proxy
        
        # Note: For now, we'll skip user_data_dir support to simplify the integration
        # Camoufox handles profiles differently and we want to focus on getting basic functionality working
        if self.browser_profile.user_data_dir:
            logger.warning("User data directory not yet supported with Camoufox integration. Using default profile.")
        
        logger.info(f"🔧 Camoufox launch options: firefox_prefs={firefox_prefs}, launch_args={launch_args}")
        
        # Launch Camoufox
        self._camoufox_instance = AsyncCamoufox(**camoufox_options)
        
        # Start the browser and get the underlying Playwright browser
        await self._camoufox_instance.__aenter__()
        
        # Get the Playwright browser instance from Camoufox
        # Camoufox wraps Playwright, so we can access the underlying browser
        self.browser = self._camoufox_instance.browser
        
        # Create a new context or use the default one
        if self.browser.contexts:
            self.browser_context = self.browser.contexts[0]
        else:
            # Create new context with browser profile settings
            context_options = {}
            
            # Add viewport if specified
            if hasattr(self.browser_profile, 'viewport') and self.browser_profile.viewport:
                context_options['viewport'] = self.browser_profile.viewport
            
            # Add user agent if specified  
            if hasattr(self.browser_profile, 'user_agent') and self.browser_profile.user_agent:
                context_options['user_agent'] = self.browser_profile.user_agent
                
            self.browser_context = await self.browser.new_context(**context_options)
        
        # The parent class will handle page setup in _setup_viewports()
        logger.info(f'🦊 Camoufox browser context created successfully')
    
    async def start(self) -> Self:
        """Override start to properly follow parent's initialization flow"""
        async with self._start_lock:
            # Check if we're already initialized and connected
            if self.initialized and self.is_connected():
                return self
            
            # Reset connection state
            self._reset_connection_state()
            
            self.initialized = True  # Set this first to prevent race conditions
            try:
                # Follow parent's initialization flow
                # 1. Prepare browser profile
                assert isinstance(self.browser_profile, BrowserProfile)
                self.browser_profile.prepare_user_data_dir()
                self.browser_profile.detect_display_configuration()
                
                # 2. Set up Playwright
                await self.setup_playwright()
                
                # 3. Try to use passed browser objects first (if any)
                await self.setup_browser_via_passed_objects()
                
                # 4. Try other connection methods
                await self.setup_browser_via_browser_pid()
                await self.setup_browser_via_wss_url()
                await self.setup_browser_via_cdp_url()
                
                # 5. If no browser context yet, create new one with Camoufox
                await self.setup_new_browser_context()
                
                assert self.browser_context, f'Failed to connect to or create a new BrowserContext for browser={self.browser}'
                
                # 6. Set up viewports and page listeners
                await self._setup_viewports()
                await self._setup_current_page_change_listeners()
                
            except Exception:
                self.initialized = False
                raise
            
            return self
    
    async def close(self) -> None:
        """Override to properly close Camoufox"""
        try:
            # First, set the browser context to None to prevent parent from trying to close it
            # since Camoufox will handle the closing
            if self._camoufox_instance:
                # Save references before clearing
                browser_context = self.browser_context
                browser = self.browser
                
                # Clear references to prevent parent class from trying to close them
                self.browser_context = None
                self.browser = None
                
                # Now let Camoufox close everything
                await self._camoufox_instance.__aexit__(None, None, None)
                self._camoufox_instance = None
                
                logger.info("🦊 Camoufox browser closed successfully")
            
            # Call parent's stop method to handle other cleanup
            await self.stop()
            
        except Exception as e:
            logger.warning(f"Error closing Camoufox browser: {e}")
    
    async def _setup_viewports(self) -> None:
        """Override to skip CDP-specific viewport setup that doesn't work with Firefox"""
        
        viewport = self.browser_profile.viewport
        logger.debug(
            '📐 Setting up viewport for Camoufox: '
            + f'headless={self.browser_profile.headless} '
            + (
                f'window={self.browser_profile.window_size["width"]}x{self.browser_profile.window_size["height"]}px '
                if self.browser_profile.window_size
                else '(no window) '
            )
            + (
                f'viewport={viewport["width"]}x{viewport["height"]}px'
                if viewport
                else '(no viewport)'
            )
        )
        
        # Set permissions if specified (skip unsupported ones for Firefox)
        if self.browser_profile.permissions:
            try:
                # Filter out permissions that Firefox doesn't support
                supported_permissions = [p for p in self.browser_profile.permissions if p not in ['clipboard-read', 'clipboard-write']]
                if supported_permissions:
                    await self.browser_context.grant_permissions(supported_permissions)
                if len(supported_permissions) < len(self.browser_profile.permissions):
                    unsupported = set(self.browser_profile.permissions) - set(supported_permissions)
                    logger.debug(f'Skipped unsupported Firefox permissions: {unsupported}')
            except Exception as e:
                logger.warning(f'⚠️ Failed to grant browser permissions: {type(e).__name__}: {e}')
        
        # Set other browser context properties
        try:
            if self.browser_profile.http_credentials:
                await self.browser_context.set_http_credentials(self.browser_profile.http_credentials)
        except Exception as e:
            logger.warning(f'⚠️ Failed to set HTTP credentials: {type(e).__name__}: {e}')
        
        try:
            if self.browser_profile.extra_http_headers:
                await self.browser_context.set_extra_http_headers(self.browser_profile.extra_http_headers)
        except Exception as e:
            logger.warning(f'⚠️ Failed to setup extra HTTP headers: {type(e).__name__}: {e}')
        
        try:
            if self.browser_profile.geolocation:
                await self.browser_context.set_geolocation(self.browser_profile.geolocation)
        except Exception as e:
            logger.warning(f'⚠️ Failed to update browser geolocation: {type(e).__name__}: {e}')
        
        if self.browser_profile.storage_state:
            await self.load_storage_state()
        
        page = None
        
        # Apply viewport size to existing pages
        for page in self.browser_context.pages:
            if viewport:
                await page.set_viewport_size(viewport)
            
            # Show loading animation on about:blank pages
            if page.url == 'about:blank':
                # Skip the DVD screensaver for Camoufox as it causes visual artifacts
                # await self._show_dvd_screensaver_loading_animation(page)
                pass
        
        # Create a new page if none exist
        page = page or (await self.browser_context.new_page())
        
        # Apply viewport to the new page as well
        if viewport and page:
            await page.set_viewport_size(viewport)
        
        # For Firefox/Camoufox, we'll use JavaScript to resize the window instead of CDP
        if (not viewport) and (self.browser_profile.window_size is not None) and not self.browser_profile.headless:
            try:
                # Use JavaScript to resize the window (works with Firefox)
                await page.evaluate(
                    """(size) => {
                        window.resizeTo(size.width, size.height);
                    }""",
                    self.browser_profile.window_size
                )
                logger.debug(f'✅ Resized Firefox window using JavaScript')
            except Exception as e:
                logger.warning(
                    f'⚠️ Failed to resize Firefox window to {self.browser_profile.window_size["width"]}x{self.browser_profile.window_size["height"]}px: {type(e).__name__}: {e}'
                )

    async def get_current_page(self) -> Page:
        """Override to add better error handling for Camoufox"""
        try:
            page = await super().get_current_page()
            
            # Remove the responsiveness check as it causes issues with Firefox/Camoufox
            # and leads to multiple unnecessary windows being opened
            
            return page
        except Exception as e:
            logger.error(f"Error getting current page: {e}")
            raise