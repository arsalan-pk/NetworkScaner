"""
Main entry point for Enterprise Network Scanner.

This module provides the main application entry point with proper
initialization, error handling, and configuration management.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import messagebox

from .config.settings import Settings
from .core.logging_config import LoggerSetup
from .core.exceptions import NetworkScannerError, ConfigurationError
from .ui.main_window import NetworkScannerApp


def setup_environment() -> None:
    """Setup environment variables and paths."""
    # Set environment variable for config directory
    config_dir = Path(__file__).parent.parent.parent.parent / "config"
    os.environ['NETWORK_SCANNER_CONFIG_DIR'] = str(config_dir)
    
    # Set environment (development by default)
    if 'NETWORK_SCANNER_ENV' not in os.environ:
        os.environ['NETWORK_SCANNER_ENV'] = 'development'


def initialize_logging(settings: Settings) -> None:
    """
    Initialize logging configuration.
    
    Args:
        settings: Application settings
    """
    def setup_logging() -> None:
        """Setup basic logging for the application."""
        try:
            LoggerSetup.setup_logging(
                log_level="INFO",
                log_file="network_scanner.log",
                console_output=True
            )
        except ConfigurationError:
            # Continue without logging if setup fails
            pass

    try:
        setup_logging()
    except ConfigurationError as e:
        print(f"Failed to initialize logging: {e.message}")
        # Continue without logging rather than crash


def handle_global_exception(exc_type, exc_value, exc_traceback) -> None:
    """
    Handle uncaught exceptions globally.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle keyboard interrupt gracefully
        logger.info("Application interrupted by user")
        sys.exit(0)
    
    # Log the exception
    logger.critical(
        "Uncaught exception occurred",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Show error dialog if GUI is available
    try:
        error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
        messagebox.showerror("Critical Error", error_msg)
    except tk.TclError:
        # GUI not available, print to console
        print("Critical Error:", error_msg)
    
    sys.exit(1)


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Setup environment
        setup_environment()
        
        # Initialize settings
        try:
            settings = Settings()
        except ConfigurationError as e:
            print(f"Configuration error: {e.message}")
            return 1
        
        # Initialize logging
        initialize_logging(settings)
        
        # Setup global exception handler
        sys.excepthook = handle_global_exception
        
        # Create and run application
        root = tk.Tk()
        
        # Create application instance
        try:
            app = NetworkScannerApp(root, settings)
        except NetworkScannerError as e:
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize application:\n{e.message}")
            return 1
        
        # Run main loop
        root.mainloop()
        
        return 0
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
