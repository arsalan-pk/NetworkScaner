#!/usr/bin/env python3
"""
Network Scanner - Professional Network Security Assessment Tool

Simple entry point that uses the enterprise architecture internally
while providing the same simple interface as the original.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import tkinter as tk
    from tkinter import messagebox
    from network_scanner.config.settings import Settings
    from network_scanner.core.logging_config import LoggerSetup
    from network_scanner.core.exceptions import NetworkScannerError, ConfigurationError
    from network_scanner.ui.main_window import NetworkScannerApp
    
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

    def main() -> None:
        """Main application entry point."""
        try:
            # Setup logging
            setup_logging()
            
            # Initialize settings
            try:
                settings = Settings()
            except ConfigurationError:
                # Use defaults if config fails
                settings = Settings()
            
            # Create and run application
            root = tk.Tk()
            
            try:
                app = NetworkScannerApp(root, settings)
            except NetworkScannerError as e:
                messagebox.showerror("Initialization Error", 
                                   f"Failed to initialize application:\n{e.message}")
                return
            
            # Run main loop
            root.mainloop()
            
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        except Exception as e:
            print(f"Fatal error: {str(e)}")
            try:
                messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{str(e)}")
            except:
                pass

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install python-nmap PyYAML")
    print("\nAlso ensure nmap is installed:")
    print("sudo apt install nmap  # For Kali/Debian")
    print("winget install NmapSoftware.Nmap  # For Windows")
except Exception as e:
    print(f"Unexpected error: {e}")
