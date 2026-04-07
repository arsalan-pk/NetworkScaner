#!/usr/bin/env python3
"""
Debug nmap installation and python-nmap package
"""

import subprocess
import sys
import os

def check_nmap_binary():
    """Check if nmap binary is available."""
    print("=== Checking nmap binary ===")
    try:
        result = subprocess.run(['which', 'nmap'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ nmap binary found at: {result.stdout.strip()}")
        else:
            print("❌ nmap binary not found")
    except FileNotFoundError:
        print("❌ 'which' command not found")
    except Exception as e:
        print(f"❌ Error checking nmap binary: {e}")
    
    # Try direct path check
    nmap_paths = ['/usr/bin/nmap', '/usr/local/bin/nmap', '/snap/bin/nmap']
    for path in nmap_paths:
        if os.path.exists(path):
            print(f"✅ nmap found at: {path}")
            return
    print("❌ nmap not found in common paths")

def check_python_nmap():
    """Check python-nmap package."""
    print("\n=== Checking python-nmap package ===")
    try:
        import nmap
        print("✅ python-nmap package imported successfully")
        
        try:
            scanner = nmap.PortScanner()
            print("✅ nmap.PortScanner() created successfully")
            
            # Try to get version
            try:
                version = scanner.nmap_version()
                print(f"✅ nmap version: {version}")
            except Exception as e:
                print(f"⚠️  Could not get nmap version: {e}")
                
        except Exception as e:
            print(f"❌ Failed to create nmap.PortScanner: {e}")
            
    except ImportError:
        print("❌ python-nmap package not installed")
        print("Install with: pip install python-nmap")
    except Exception as e:
        print(f"❌ Error importing python-nmap: {e}")

def check_permissions():
    """Check if running with proper permissions."""
    print("\n=== Checking permissions ===")
    if os.geteuid() == 0:
        print("✅ Running as root")
    else:
        print("⚠️  Not running as root - some nmap scans may require sudo")

def main():
    print("Nmap Installation Diagnostic Tool")
    print("=" * 40)
    
    check_nmap_binary()
    check_python_nmap()
    check_permissions()
    
    print("\n=== Summary ===")
    print("If nmap is installed but still failing:")
    print("1. Try: sudo python3 networkscanner.py")
    print("2. Check nmap version: nmap --version")
    print("3. Reinstall python-nmap: pip uninstall python-nmap && pip install python-nmap")

if __name__ == "__main__":
    main()
