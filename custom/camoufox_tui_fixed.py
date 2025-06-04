#!/usr/bin/env python3
"""
camoufox_tui_fixed.py
Fixed version of Camoufox TUI integration that addresses async execution issues
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

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
from browser_use.agent.service import Agent


class CamoufoxBrowserUseApp(BrowserUseApp):
    """Extended BrowserUseApp that properly handles Camoufox browser sessions"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._browser_started = False
    
    def on_mount(self) -> None:
        """Override on_mount to ensure browser is started"""
        # Call parent's on_mount first
        super().on_mount()
        
        # Ensure browser session is started if it's a CamoufoxBrowserSession
        if isinstance(self.browser_session, CamoufoxBrowserSession) and not self._browser_started:
            logger = logging.getLogger('browser_use.camoufox')
            
            # Schedule browser startup as a background task
            async def start_browser():
                try:
                    if not self.browser_session.is_connected():
                        logger.debug("Starting Camoufox browser session...")
                        await self.browser_session.start()
                        self._browser_started = True
                        logger.debug("Camoufox browser session started successfully")
                except Exception as e:
                    logger.error(f"Failed to start Camoufox browser: {e}", exc_info=True)
                    # Show error in UI
                    rich_log = self.query_one('#results-log')
                    rich_log.write(f"[red]Error starting Camoufox browser: {e}[/]")
            
            # Run the browser startup in the background
            self.run_worker(start_browser, name='browser_startup')
    
    def run_task(self, task: str) -> None:
        """Override run_task to add better error handling for Camoufox"""
        # Import AgentSettings here to avoid circular imports
        from browser_use.cli import AgentSettings
        
        logger = logging.getLogger('browser_use.app')
        
        # Make sure intro is hidden and log is ready
        self.hide_intro_panels()
        
        # Start continuous updates of all info panels
        self.update_info_panels()
        
        # Clear the log to start fresh
        rich_log = self.query_one('#results-log')
        rich_log.clear()
        
        # Create agent with proper error handling
        try:
            agent_settings = AgentSettings.model_validate(self.config.get('agent', {}))
            
            if self.agent is None:
                # Ensure browser is started before creating agent
                if isinstance(self.browser_session, CamoufoxBrowserSession):
                    if not self.browser_session.is_connected():
                        # Start browser synchronously in the worker
                        logger.debug("Browser not connected, will start in worker")
                
                self.agent = Agent(
                    task=task,
                    llm=self.llm,
                    controller=self.controller,
                    browser_session=self.browser_session,
                    source='cli',
                    **agent_settings.model_dump(),
                )
                
                # Update our browser_session reference to point to the agent's
                if hasattr(self.agent, 'browser_session'):
                    self.browser_session = self.agent.browser_session
            else:
                self.agent.add_new_task(task)
        except Exception as e:
            logger.error(f"Error creating agent: {e}", exc_info=True)
            rich_log.write(f"[red]Error creating agent: {e}[/]")
            return
        
        # Let the agent run in the background with proper async handling
        async def agent_task_worker() -> None:
            logger.debug(f'\n🚀 Working on task: {task}')
            
            # Set flags to indicate the agent is running
            self.agent.running = True
            self.agent.last_response_time = 0
            
            try:
                # Ensure browser is started
                if isinstance(self.browser_session, CamoufoxBrowserSession):
                    if not self.browser_session.is_connected():
                        logger.debug("Starting browser in worker...")
                        await self.browser_session.start()
                        logger.debug("Browser started in worker")
                
                # Run the agent task
                logger.debug("Starting agent.run()...")
                await self.agent.run()
                logger.debug("agent.run() completed successfully")
                
            except asyncio.CancelledError:
                logger.warning("Agent task was cancelled")
                raise
            except Exception as e:
                logger.error(f'\nError running agent: {str(e)}', exc_info=True)
                rich_log.write(f"[red]Error running agent: {str(e)}[/]")
            finally:
                # Clear the running flag
                self.agent.running = False
                
                logger.debug('\n✅ Task completed!')
                
                # Make sure the task input container is visible
                task_input_container = self.query_one('#task-input-container')
                task_input_container.display = True
                
                # Refocus the input field
                input_field = self.query_one('#task-input')
                input_field.focus()
                
                # Ensure the input is visible by scrolling to it
                self.call_after_refresh(self.scroll_to_input)
        
        # Run the worker with error handling
        try:
            self.run_worker(agent_task_worker, name='agent_task')
        except Exception as e:
            logger.error(f"Error starting agent worker: {e}", exc_info=True)
            rich_log.write(f"[red]Error starting agent worker: {e}[/]")


@asynccontextmanager
async def create_camoufox_session(config: dict):
    """Context manager for creating and cleaning up Camoufox browser session"""
    browser_session = None
    try:
        # Get browser config
        browser_config = config.get('browser', {})
        
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
        
        # Create CamoufoxBrowserSession
        browser_session = CamoufoxBrowserSession(
            browser_profile=profile,
            geoip=browser_config.get('geoip', True),
        )
        
        yield browser_session
        
    finally:
        if browser_session:
            try:
                await browser_session.close()
            except Exception as e:
                logging.error(f"Error closing browser session: {e}")


async def camoufox_textual_interface(config: dict):
    """Modified textual_interface that uses CamoufoxBrowserSession with better error handling"""
    logger = logging.getLogger('browser_use.startup')
    
    # Set up logging for Textual UI
    def setup_textual_logging():
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
        
        null_handler = logging.NullHandler()
        root_logger.addHandler(null_handler)
        logger.debug('Logging configured for Textual UI')
    
    logger.debug('Setting up Browser, Controller, and LLM...')
    
    # Use context manager for browser session
    async with create_camoufox_session(config) as browser_session:
        logger.info('Browser type: Camoufox (Firefox-based)')
        logger.info(f'Browser mode: {"headless" if config.get("browser", {}).get("headless", False) else "visible"}')
        
        # Initialize Controller
        logger.debug('Initializing Controller...')
        try:
            controller = Controller()
            logger.debug('Controller initialized successfully')
        except Exception as e:
            logger.error(f'Error initializing Controller: {str(e)}', exc_info=True)
            raise RuntimeError(f'Failed to initialize Controller: {str(e)}')
        
        # Get LLM
        logger.debug('Getting LLM...')
        try:
            llm = get_llm(config)
            model_name = getattr(llm, 'model_name', None) or getattr(llm, 'model', 'Unknown model')
            provider = llm.__class__.__name__
            temperature = getattr(llm, 'temperature', 0.0)
            logger.info(f'LLM: {provider} ({model_name}), temperature: {temperature}')
        except Exception as e:
            logger.error(f'Error getting LLM: {str(e)}', exc_info=True)
            raise RuntimeError(f'Failed to initialize LLM: {str(e)}')
        
        # Create and run app
        logger.debug('Initializing CamoufoxBrowserUseApp instance...')
        try:
            app = CamoufoxBrowserUseApp(config)
            
            # Pass the initialized components to the app
            app.browser_session = browser_session
            app.controller = controller
            app.llm = llm
            
            # Configure logging for Textual UI before going fullscreen
            setup_textual_logging()
            
            logger.info(f'Preparing Camoufox browser with {model_name} LLM')
            logger.debug('Starting Textual app with run_async()...')
            
            # Run the app
            await app.run_async()
            
        except Exception as e:
            logger.error(f'Error in camoufox_textual_interface: {str(e)}', exc_info=True)
            raise


def main():
    """Main entry point for fixed Camoufox TUI"""
    print("🦊 Starting browser-use TUI with Camoufox (Fixed Version)...")
    
    # Set up basic logging
    log_level = logging.DEBUG if os.getenv('DEBUG') or os.getenv('BROWSER_USE_DEBUG') else logging.INFO
    logging.basicConfig(
        level=log_level,
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