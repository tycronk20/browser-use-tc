#!/usr/bin/env python3
"""
camoufox_tui.py
Launch browser-use TUI with Camoufox browser integration
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import browser_use
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add the custom directory to the path for our custom modules
sys.path.insert(0, str(Path(__file__).parent))

# Import the custom Camoufox browser session
from camoufox_browser_session import CamoufoxBrowserSession

# Import browser-use components
from browser_use.cli import BrowserUseApp, load_user_config, save_user_config, get_llm
from browser_use.controller.service import Controller
from browser_use.browser.profile import BrowserProfile


# Patch the BrowserUseApp to properly handle Camoufox
class CamoufoxBrowserUseApp(BrowserUseApp):
    """Extended BrowserUseApp that properly handles Camoufox browser sessions"""
    
    def on_mount(self) -> None:
        """Override on_mount to ensure browser is started"""
        # Call parent's on_mount first
        super().on_mount()
        
        # Ensure browser session is started if it's a CamoufoxBrowserSession
        if isinstance(self.browser_session, CamoufoxBrowserSession):
            logger = logging.getLogger('browser_use.camoufox')
            
            # Schedule browser startup as a background task
            async def start_browser():
                try:
                    if not self.browser_session.is_connected():
                        logger.debug("Starting Camoufox browser session...")
                        await self.browser_session.start()
                        logger.debug("Camoufox browser session started successfully")
                except Exception as e:
                    logger.error(f"Failed to start Camoufox browser: {e}", exc_info=True)
                    # Show error in UI
                    rich_log = self.query_one('#results-log')
                    rich_log.write(f"[red]Error starting Camoufox browser: {e}[/]")
            
            # Run the browser startup in the background
            self.run_worker(start_browser, name='browser_startup')


async def camoufox_textual_interface(config: dict):
    """Modified textual_interface that uses CamoufoxBrowserSession"""
    logger = logging.getLogger('browser_use.startup')

    # Set up logging for Textual UI - prevent any logging to stdout
    def setup_textual_logging():
        # Replace all handlers with null handler
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

        # Add null handler to ensure no output to stdout/stderr
        null_handler = logging.NullHandler()
        root_logger.addHandler(null_handler)
        logger.debug('Logging configured for Textual UI')

    logger.debug('Setting up Browser, Controller, and LLM...')

    # Step 1: Initialize CamoufoxBrowserSession instead of BrowserSession
    logger.debug('Initializing CamoufoxBrowserSession...')
    browser_session = None
    try:
        # Get browser config from the config dict
        browser_config = config.get('browser', {})

        logger.info('Browser type: Camoufox (Firefox-based)')
        if browser_config.get('headless'):
            logger.info('Browser mode: headless')
        else:
            logger.info('Browser mode: visible')

        # Create browser profile with only valid parameters
        profile_kwargs = {
            'headless': browser_config.get('headless', False),
        }
        
        # Only add optional parameters if they're not None
        optional_params = [
            'viewport', 'locale', 'timezone_id', 'geolocation',
            'permissions', 'device_scale_factor', 'is_mobile', 'color_scheme'
        ]
        
        for param in optional_params:
            value = browser_config.get(param)
            if value is not None:
                profile_kwargs[param] = value
            
        profile = BrowserProfile(**profile_kwargs)

        # Create CamoufoxBrowserSession with the profile
        browser_session = CamoufoxBrowserSession(
            browser_profile=profile,
            geoip=browser_config.get('geoip', True),  # Camoufox-specific option
        )
        
        logger.debug('CamoufoxBrowserSession initialized successfully')

    except Exception as e:
        logger.error(f'Error initializing CamoufoxBrowserSession: {str(e)}', exc_info=True)
        raise RuntimeError(f'Failed to initialize CamoufoxBrowserSession: {str(e)}')

    # Step 2: Initialize Controller
    controller = None
    logger.debug('Initializing Controller...')
    try:
        controller = Controller()
        logger.debug('Controller initialized successfully')
    except Exception as e:
        logger.error(f'Error initializing Controller: {str(e)}', exc_info=True)
        raise RuntimeError(f'Failed to initialize Controller: {str(e)}')

    # Step 3: Get LLM
    llm = None
    logger.debug('Getting LLM...')
    try:
        llm = get_llm(config)
        # Log LLM details
        model_name = getattr(llm, 'model_name', None) or getattr(llm, 'model', 'Unknown model')
        provider = llm.__class__.__name__
        temperature = getattr(llm, 'temperature', 0.0)
        logger.info(f'LLM: {provider} ({model_name}), temperature: {temperature}')
        logger.debug(f'LLM initialized successfully: {provider}')
    except Exception as e:
        logger.error(f'Error getting LLM: {str(e)}', exc_info=True)
        raise RuntimeError(f'Failed to initialize LLM: {str(e)}')

    logger.debug('Initializing CamoufoxBrowserUseApp instance...')
    app = None
    try:
        # Use our custom app that handles Camoufox properly
        app = CamoufoxBrowserUseApp(config)
        
        # Pass the initialized components to the app
        app.browser_session = browser_session
        app.controller = controller
        app.llm = llm

        # Configure logging for Textual UI before going fullscreen
        setup_textual_logging()

        # Log browser and model configuration that will be used
        browser_type = 'Camoufox'
        model_name = config.get('model', {}).get('name', 'auto-detected')
        headless = config.get('browser', {}).get('headless', False)
        headless_str = 'headless' if headless else 'visible'

        logger.info(f'Preparing {browser_type} browser ({headless_str}) with {model_name} LLM')

        logger.debug('Starting Textual app with run_async()...')
        # No more logging after this point as we're in fullscreen mode
        await app.run_async()
        
    except Exception as e:
        logger.error(f'Error in camoufox_textual_interface: {str(e)}', exc_info=True)
        # Make sure to close browser session if app initialization fails
        if browser_session:
            try:
                await browser_session.close()
            except Exception as close_error:
                logger.error(f"Error closing browser session: {close_error}")
        raise
    finally:
        # Ensure cleanup happens
        if app and hasattr(app, 'browser_session') and app.browser_session:
            try:
                await app.browser_session.close()
            except Exception as e:
                logger.error(f"Error during final cleanup: {e}")


def main():
    """Main entry point for Camoufox TUI"""
    print("🦊 Starting browser-use TUI with Camoufox...")
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logger = logging.getLogger('browser_use.startup')
    
    try:
        # Load user configuration
        logger.debug('Loading user configuration...')
        config = load_user_config()
        
        # Force headless=False for better TUI experience
        if 'browser' not in config:
            config['browser'] = {}
        config['browser']['headless'] = False
        
        # Save the updated config
        save_user_config(config)
        
        # Run the modified TUI with Camoufox
        asyncio.run(camoufox_textual_interface(config))
        
    except KeyboardInterrupt:
        print("\n🔚 Interrupted by user")
    except Exception as e:
        logger.error(f'Error launching Camoufox TUI: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 