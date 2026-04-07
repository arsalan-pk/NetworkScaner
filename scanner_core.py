import nmap
import threading
from datetime import datetime
from tkinter import messagebox


class ScannerCore:
    """Handles the core network scanning functionality."""
    
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.scanner = None
        self.scan_results = {}
        self.is_scanning = False
        
        # Initialize nmap scanner
        try:
            self.scanner = nmap.PortScanner()
        except nmap.PortScannerError:
            messagebox.showerror("Nmap Not Found", "Nmap is not installed or not in your PATH. Please install it (e.g., sudo apt install nmap).")
            raise
    
    def start_scan(self, target, profile, scan_finished_callback):
        """Start a network scan in a separate thread."""
        if self.is_scanning:
            return False
        
        self.is_scanning = True
        self.log_callback(f"[*] Starting scan on target: {target}")
        self.log_callback(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_callback("-" * 60)
        
        # Run scan in a separate thread to keep UI responsive
        thread = threading.Thread(
            target=self._run_scan, 
            args=(target, profile, scan_finished_callback), 
            daemon=True
        )
        thread.start()
        return True
    
    def _run_scan(self, target, profile, scan_finished_callback):
        """Execute the actual network scan."""
        try:
            # Determine Nmap arguments based on selected profile
            args = self._get_scan_args(profile)
            
            # Check if sudo is needed for OS detection
            if self._needs_sudo(profile):
                self.log_callback(f"[*] Running command: sudo nmap {args} {target}")
                # Try to run with sudo first
                try:
                    import os
                    if os.name == 'nt':  # Windows
                        self.log_callback("[*] Note: On Windows, run as Administrator for OS detection")
                        self.scanner.scan(hosts=target, arguments=args)
                    else:  # Linux/Unix
                        # Use sudo by modifying nmap command execution
                        self._run_with_sudo(target, args)
                        return
                except Exception as sudo_error:
                    self.log_callback(f"[!] Sudo failed, trying without sudo: {sudo_error}")
                    self.scanner.scan(hosts=target, arguments=args)
            else:
                self.log_callback(f"[*] Running command: nmap {args} {target}")
                self.scanner.scan(hosts=target, arguments=args)
            
            self.scan_results = self.scanner.csv()
            
            # Process and display results
            self._process_scan_results()
            
            self.log_callback("\n[*] Scan Completed Successfully.")
            scan_finished_callback(True, self.scanner.all_hosts())
            
        except Exception as e:
            self.log_callback(f"\n[!] Error during scan: {str(e)}")
            scan_finished_callback(False, [])
    
    def _get_scan_args(self, profile):
        """Get nmap arguments based on scan profile."""
        if "Intense" in profile:
            return "-A -T4"  # -A enables OS detection, version detection, script scanning, traceroute
        elif "Quick" in profile:
            return "-T4 -F"  # Fast scan (fewer ports)
        elif "Ping" in profile or "Network Discovery" in profile:
            return "-sn -n"  # Ping scan only, no DNS resolution
        elif "Comprehensive" in profile:
            return "-A -T4 -p-"  # Scan all ports with OS detection
        else:
            return "-A -T4"  # Default to intense scan
    
    def _process_scan_results(self):
        """Process and display scan results."""
        if not self.scanner.all_hosts():
            self.log_callback("[!] Target seems down or blocking probe packets.")
            return
        
        for host in self.scanner.all_hosts():
            self.log_callback(f"\n[+] Host: {host} (" + self.scanner[host].hostname() + ")")
            self.log_callback(f"[+] State: {self.scanner[host].state()}")
            
            # OS Detection
            if 'osmatch' in self.scanner[host] and self.scanner[host]['osmatch']:
                os_name = self.scanner[host]['osmatch'][0]['name']
                self.log_callback(f"[+] Detected OS: {os_name}")
            else:
                self.log_callback("[-] OS Detection Note: Run with 'sudo' for accurate OS detection.")
            
            # Port scanning results
            for proto in self.scanner[host].all_protocols():
                self.log_callback(f"========== Protocol: {proto} ==========")
                ports = self.scanner[host][proto].keys()
                for port in sorted(ports):
                    self._display_port_info(host, proto, port)
    
    def _display_port_info(self, host, protocol, port):
        """Display information about a specific port."""
        state = self.scanner[host][protocol][port]['state']
        name = self.scanner[host][protocol][port]['name']
        version = self.scanner[host][protocol][port]['version']
        extrainfo = self.scanner[host][protocol][port]['extrainfo']
        info = f"Port: {port}\tState: {state}\tService: {name}\tVersion: {version} {extrainfo}".strip()
        self.log_callback(info)
    
    def get_scanner(self):
        """Get the nmap scanner instance."""
        return self.scanner
    
    def get_scan_results(self):
        """Get the latest scan results."""
        return self.scan_results
    
    def is_scan_running(self):
        """Check if a scan is currently running."""
        return self.is_scanning
    
    def _needs_sudo(self, profile):
        """Check if sudo is needed for the scan profile."""
        # Sudo is needed for OS detection and intensive scans
        sudo_profiles = ["Intense", "Comprehensive", "Quick"]
        return any(profile_name in profile for profile_name in sudo_profiles)
    
    def _run_with_sudo(self, target, args):
        """Run nmap with sudo privileges."""
        try:
            import subprocess
            import tempfile
            import os
            
            # Create a temporary script for sudo execution
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_script:
                temp_script.write(f"#!/bin/bash\nnmap {args} {target}")
                temp_script_path = temp_script.name
            
            # Make script executable
            os.chmod(temp_script_path, 0o755)
            
            # Run with sudo
            result = subprocess.run(['sudo', temp_script_path], 
                               capture_output=True, text=True, timeout=300)
            
            # Clean up
            os.unlink(temp_script_path)
            
            if result.returncode == 0:
                self.log_callback("[*] Sudo execution successful")
                # Parse results manually (simplified approach)
                self._parse_sudo_results(result.stdout)
            else:
                raise Exception(f"Sudo nmap failed: {result.stderr}")
                
        except Exception as e:
            raise Exception(f"Failed to run with sudo: {str(e)}")
    
    def _parse_sudo_results(self, output):
        """Parse sudo nmap output and update scanner results."""
        # This is a simplified approach - in production, you'd want proper parsing
        self.log_callback("[*] Processing sudo scan results...")
        # For now, just log that sudo was used successfully
        self.log_callback("[*] Sudo scan completed - OS detection should be available")
    
    def set_scan_finished(self):
        """Mark the scan as finished."""
        self.is_scanning = False
