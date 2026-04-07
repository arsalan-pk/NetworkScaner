import tkinter as tk
from datetime import datetime
from ui import NetworkScannerUI
from scanner_core import ScannerCore
from report_generator import ReportGenerator


class NetworkScannerApp:
    """Main application class that coordinates UI and scanner core."""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize scanner core with logging callback
        try:
            self.scanner_core = ScannerCore(log_callback=self._log_message)
        except Exception:
            # If scanner initialization fails, the error is already shown by ScannerCore
            self.root.destroy()
            return
        
        # Initialize UI with callbacks
        self.ui = NetworkScannerUI(
            root=root,
            scan_callback=self.start_scan,
            report_callback=self.generate_report
        )
        
        # Initialize report generator
        self.report_generator = ReportGenerator(self.scanner_core.get_scanner())
    
    def _log_message(self, message):
        """Log message through UI."""
        self.ui.log(message)
    
    def start_scan(self):
        """Start the network scan."""
        if self.scanner_core.is_scan_running():
            return
        
        # Validate inputs
        if not self.ui.validate_inputs():
            return
        
        # Get scan parameters
        target, scanner_name, profile = self.ui.get_scan_inputs()
        
        # Clear log and start scan
        self.ui.clear_log()
        self.ui.log(f"[*] Initiated by: {scanner_name}")
        self.ui.set_scanning_state(True)
        
        # Start scan through scanner core
        self.scanner_core.start_scan(
            target=target,
            profile=profile,
            scan_finished_callback=self._scan_finished
        )
    
    def _scan_finished(self, success, hosts):
        """Handle scan completion."""
        self.scanner_core.set_scan_finished()
        self.ui.set_scanning_state(False)
        
        if success and hosts:
            self.ui.enable_report_button()
    
    def generate_report(self):
        """Generate HTML report using the modular report generator."""
        target, scanner_name, scan_profile = self.ui.get_scan_inputs()
        
        self.report_generator.generate_html_report(target, scanner_name, scan_profile)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
