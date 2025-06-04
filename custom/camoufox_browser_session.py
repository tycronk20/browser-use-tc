#!/usr/bin/env python3
"""
camoufox_browser_session.py
Custom BrowserSession that uses Camoufox instead of Chromium
"""

import logging
from typing import Self
from pathlib import Path

from browser_use.browser.session import BrowserSession
from camoufox.async_api import AsyncCamoufox

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
        
        # Store Camoufox instance
        self._camoufox_instance = None
    
    async def setup_new_browser_context(self) -> None:
        """Override to use Camoufox instead of Playwright's chromium"""
        
        logger.info(f'🦊 Launching Camoufox browser headless={self.browser_profile.headless}')
        
        # Prepare Camoufox launch options
        camoufox_options = {
            'headless': self.browser_profile.headless,
            **self.camoufox_options
        }
        
        # Add proxy if specified
        if hasattr(self.browser_profile, 'proxy') and self.browser_profile.proxy:
            camoufox_options['proxy'] = self.browser_profile.proxy
        
        # Note: For now, we'll skip user_data_dir support to simplify the integration
        # Camoufox handles profiles differently and we want to focus on getting basic functionality working
        if self.browser_profile.user_data_dir:
            logger.warning("User data directory not yet supported with Camoufox integration. Using default profile.")
        
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
        
        # Set up the current page
        if self.browser_context.pages:
            self.agent_current_page = self.browser_context.pages[0]
        else:
            self.agent_current_page = await self.browser_context.new_page()
        
        logger.info(f'🦊 Camoufox browser connected successfully')
    
    async def close(self) -> None:
        """Override to properly close Camoufox"""
        try:
            if self._camoufox_instance:
                await self._camoufox_instance.__aexit__(None, None, None)
                self._camoufox_instance = None
            
            # Call parent close for cleanup
            await super().close()
            
        except Exception as e:
            logger.warning(f"Error closing Camoufox browser: {e}")
    
    async def start(self) -> Self:
        """Override start to use Camoufox setup"""
        if self.initialized:
            return self
        
        # Set up Playwright
        if not self.playwright:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
        
        # Use our custom Camoufox setup instead of the parent's browser setup
        await self.setup_new_browser_context()
        
        # Initialize browser state (similar to parent class)
        await self._setup_viewports()
        await self._setup_current_page_change_listeners()
        
        self.initialized = True
        return self