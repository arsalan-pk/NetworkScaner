#!/usr/bin/env python3
"""
Network Scanner - Network Security Assessment Tool
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
    from network_scanner.core.exceptions import NetworkScannerError, ConfigurationError
    from network_scanner.ui.main_window import NetworkScannerApp
    
    def main() -> None:
        """Main application entry point."""
        try:
            # Initialize settings
            try:
                settings = Settings()
            except ConfigurationError:
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
