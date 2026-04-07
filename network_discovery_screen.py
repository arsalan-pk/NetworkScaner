import tkinter as tk
from tkinter import ttk, Canvas
import math
import threading
from ui import NetworkScannerUI
from scanner_core import ScannerCore
from report_generator import ReportGenerator


class NetworkDiscoveryScreen:
    """Network discovery screen with loading animation."""
    
    def __init__(self, root):
        self.root = root
        self.main_app = None
        self.is_loading = False
        self.loading_angle = 0
        
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure the network discovery window."""
        self.root.title("Network Discovery Scanner - Developed by Arsalan Khan")
        self.root.geometry("850x700")
        self.root.configure(bg="#2b2b2b")
    
    def _setup_styles(self):
        """Configure ttk styles for the network discovery screen."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="#e0e0e0")
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#4a90e2")
        
        # Button styling
        style.configure("Action.TButton", 
                       font=("Helvetica", 12, "bold"), 
                       background="#4a90e2", 
                       foreground="white", 
                       padding=12,
                       borderwidth=0,
                       focuscolor='none',
                       relief="flat")
        style.map('Action.TButton', 
                 background=[('active', '#357abd'), ('pressed', '#2968a3')])
    
    def _create_widgets(self):
        """Create network discovery screen widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Back button
        btn_back = ttk.Button(
            header_frame,
            text="← Back to Welcome",
            command=self.back_to_welcome,
            style="Action.TButton"
        )
        btn_back.pack(side=tk.LEFT)
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="Network Discovery Scanner", 
            style="Header.TLabel"
        )
        title_label.pack(side=tk.LEFT, padx=(20, 0))

        # Loading and content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Loading animation canvas
        self.canvas = Canvas(
            content_frame, 
            width=200, 
            height=200, 
            bg="#2b2b2b", 
            highlightthickness=0
        )
        self.canvas.pack(pady=30)

        # Loading text
        self.loading_label = ttk.Label(
            content_frame,
            text="Discovering Network...",
            font=("Helvetica", 14),
            foreground="#4a90e2",
            background="#2b2b2b"
        )
        self.loading_label.pack(pady=(0, 20))

        # Results frame (initially hidden)
        self.results_frame = ttk.Frame(content_frame)
        
        # Start discovery button
        self.btn_start = ttk.Button(
            content_frame,
            text="🔍 Start Network Discovery",
            command=self.start_discovery,
            style="Action.TButton"
        )
        self.btn_start.pack(pady=20)
    
    def start_discovery(self):
        """Start the network discovery process."""
        self.is_loading = True
        self.btn_start.pack_forget()
        self.loading_label.pack(pady=(0, 20))
        self.canvas.pack(pady=30)
        
        # Start loading animation
        self.animate_loading()
        
        # Start network discovery in background thread
        threading.Thread(target=self._perform_discovery, daemon=True).start()
    
    def animate_loading(self):
        """Animate the circular loading indicator."""
        if not self.is_loading:
            return
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw circular loading animation
        center_x, center_y = 100, 100
        radius = 40
        
        # Draw background circle
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="#3c3f41", width=4
        )
        
        # Draw animated arc
        arc_length = 90  # degrees
        start_angle = self.loading_angle
        
        self.canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle, extent=arc_length,
            outline="#4a90e2", width=4, style=tk.ARC
        )
        
        # Update angle for next frame
        self.loading_angle = (self.loading_angle + 10) % 360
        
        # Schedule next frame
        self.root.after(50, self.animate_loading)
    
    def _perform_discovery(self):
        """Perform the actual network discovery."""
        try:
            # Initialize scanner
            scanner_core = ScannerCore(log_callback=self._log_message)
            
            # Perform network discovery scan
            target = "192.168.1.0/24"  # Default network range
            profile = "Network Discovery (Ping Scan)"
            
            # Simulate discovery process
            import time
            time.sleep(3)  # Simulate scanning time
            
            # Stop loading animation
            self.is_loading = False
            self.root.after(0, self._show_results, scanner_core)
            
        except Exception as e:
            self.is_loading = False
            self.root.after(0, self._show_error, str(e))
    
    def _log_message(self, message):
        """Log discovery messages."""
        print(f"[Discovery] {message}")  # For debugging
    
    def _show_results(self, scanner_core):
        """Show discovery results."""
        # Hide loading elements
        self.canvas.pack_forget()
        self.loading_label.pack_forget()
        
        # Show results
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Create results display
        results_label = ttk.Label(
            self.results_frame,
            text="🎉 Network Discovery Complete!",
            font=("Helvetica", 16, "bold"),
            foreground="#27ae60",
            background="#2b2b2b"
        )
        results_label.pack(pady=10)
        
        # Add scan results button
        btn_scan_results = ttk.Button(
            self.results_frame,
            text="📊 View Scan Results",
            command=lambda: self.open_scan_results(scanner_core),
            style="Action.TButton"
        )
        btn_scan_results.pack(pady=10)
        
        # Add new discovery button
        btn_new_discovery = ttk.Button(
            self.results_frame,
            text="🔄 Start New Discovery",
            command=self.reset_discovery,
            style="Action.TButton"
        )
        btn_new_discovery.pack(pady=5)
    
    def _show_error(self, error_message):
        """Show discovery error."""
        self.canvas.pack_forget()
        self.loading_label.pack_forget()
        
        error_label = ttk.Label(
            self.results_frame,
            text=f"❌ Discovery Failed: {error_message}",
            font=("Helvetica", 12),
            foreground="#e74c3c",
            background="#2b2b2b"
        )
        error_label.pack(pady=20)
        
        btn_retry = ttk.Button(
            self.results_frame,
            text="🔄 Retry Discovery",
            command=self.reset_discovery,
            style="Action.TButton"
        )
        btn_retry.pack(pady=10)
    
    def open_scan_results(self, scanner_core):
        """Open detailed scan results screen."""
        self._clear_screen()
        self.main_app = NetworkScannerApp(self.root, scanner_core, mode="target")
    
    def reset_discovery(self):
        """Reset for new discovery."""
        self.results_frame.pack_forget()
        self.btn_start.pack(pady=20)
        self.is_loading = False
        self.loading_angle = 0
    
    def back_to_welcome(self):
        """Return to welcome screen."""
        from welcome_screen import WelcomeScreen
        
        self._clear_screen()
        WelcomeScreen(self.root)
    
    def _clear_screen(self):
        """Clear all widgets from the screen."""
        for widget in self.root.winfo_children():
            widget.destroy()


class NetworkScannerApp:
    """Modified main application class for scan results."""
    
    def __init__(self, root, scanner_core, mode="target"):
        self.root = root
        self.mode = mode
        self.scanner_core = scanner_core
        
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
