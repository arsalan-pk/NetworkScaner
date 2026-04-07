import tkinter as tk
from tkinter import ttk
from ui import NetworkScannerUI
from scanner_core import ScannerCore
from report_generator import ReportGenerator


class WelcomeScreen:
    """Welcome screen with navigation options."""
    
    def __init__(self, root):
        self.root = root
        self.main_app = None
        
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure the welcome window."""
        self.root.title("Network Scanner - Welcome")
        self.root.geometry("600x500")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
    
    def _setup_styles(self):
        """Configure ttk styles for the welcome screen."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="#e0e0e0")
        
        # Welcome button styling
        style.configure("Welcome.TButton", 
                       font=("Helvetica", 14, "bold"), 
                       background="#4a90e2", 
                       foreground="white", 
                       padding=15,
                       borderwidth=0,
                       focuscolor='none',
                       relief="flat",
                       width=25)
        style.map('Welcome.TButton', 
                 background=[('active', '#357abd'), ('pressed', '#2968a3')],
                 relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # Title styling
        style.configure("Title.TLabel", 
                       font=("Helvetica", 24, "bold"), 
                       foreground="#4a90e2",
                       background="#2b2b2b")
        
        # Subtitle styling
        style.configure("Subtitle.TLabel", 
                       font=("Helvetica", 12), 
                       foreground="#e0e0e0",
                       background="#2b2b2b")
    
    def _create_widgets(self):
        """Create welcome screen widgets."""
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App Title
        title_label = ttk.Label(
            main_frame, 
            text="Network Scanner", 
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 10))

        # Subtitle
        subtitle_label = ttk.Label(
            main_frame, 
            text="Developed by Arsalan Khan", 
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(0, 50))

        # Description
        desc_label = ttk.Label(
            main_frame, 
            text="Choose your scanning option:",
            font=("Helvetica", 14),
            foreground="#e0e0e0",
            background="#2b2b2b"
        )
        desc_label.pack(pady=(0, 40))

        # Buttons Container
        btn_container = ttk.Frame(main_frame)
        btn_container.pack(expand=True)

        # Network Discovery Button
        self.btn_network_scan = ttk.Button(
            btn_container,
            text="🌐 Network Discovery",
            style="Welcome.TButton",
            command=self.open_network_scan
        )
        self.btn_network_scan.pack(pady=15)

        # Target IP Scan Button
        self.btn_target_scan = ttk.Button(
            btn_container,
            text="🎯 Target IP Scan",
            style="Welcome.TButton",
            command=self.open_target_scan
        )
        self.btn_target_scan.pack(pady=15)

        # Footer
        footer_label = ttk.Label(
            main_frame,
            text="Select an option to begin scanning",
            font=("Helvetica", 10),
            foreground="#888888",
            background="#2b2b2b"
        )
        footer_label.pack(side=tk.BOTTOM, pady=20)
    
    def open_network_scan(self):
        """Open network discovery scanning interface."""
        from network_discovery_screen import NetworkDiscoveryScreen
        
        self._clear_screen()
        self.main_app = NetworkDiscoveryScreen(self.root)
    
    def open_target_scan(self):
        """Open target IP scanning interface."""
        self._clear_screen()
        self.main_app = NetworkScannerApp(self.root, mode="target")
    
    def _clear_screen(self):
        """Clear all widgets from the welcome screen."""
        for widget in self.root.winfo_children():
            widget.destroy()


class NetworkScannerApp:
    """Modified main application class that supports different modes."""
    
    def __init__(self, root, mode="target"):
        self.root = root
        self.mode = mode  # "network" or "target"
        
        # Initialize scanner core with logging callback
        try:
            self.scanner_core = ScannerCore(log_callback=self._log_message)
        except Exception:
            # If scanner initialization fails, the error is already shown by ScannerCore
            self.root.destroy()
            return
        
        # Initialize UI with callbacks and mode
        self.ui = NetworkScannerUI(
            root=root,
            scan_callback=self.start_scan,
            report_callback=self.generate_report,
            mode=mode
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
        self.ui.log(f"[*] Scan mode: {self.mode}")
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
