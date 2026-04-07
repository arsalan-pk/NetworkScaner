"""
Main application window for Network Scanner.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Optional, Callable
from datetime import datetime
import threading

from ..core.scanner import NetworkScanner, ScanRequest
from ..core.exceptions import NetworkScannerError, ScanError, ValidationError
from ..core.validator import InputValidator
from ..config.settings import Settings, ScanProfiles
from ..reports.html_generator import HTMLReportGenerator
from .styles import UIStyles


class NetworkScannerApp:
    """
    Main application window for the Network Scanner.
    """
    
    def __init__(self, root: tk.Tk, settings: Optional[Settings] = None) -> None:
        """
        Initialize the main application window.
        
        Args:
            root: Root tkinter window
            settings: Application settings instance
        """
        self.root = root
        self.settings = settings or Settings()
        self.ui_styles = UIStyles(self.settings)
        
        # Initialize scanner - simple approach
        try:
            import nmap
            self.scanner = nmap.PortScanner()
            self.log_message("✅ Scanner initialized successfully")
        except Exception as e:
            messagebox.showerror("Nmap Not Found", 
                f"Nmap is not installed or not in your PATH.\n\n"
                "For Linux/Debian/Kali: sudo apt install nmap\n"
                "For Windows: https://nmap.org/download.html\n"
                "For macOS: brew install nmap\n\n"
                "After installation, restart this application")
            self.root.destroy()
            return
        
        # UI state
        self.is_scanning = False
        self.scan_results = []
        
        # Setup UI
        self._setup_window()
        self.ui_styles.configure_styles()
        self._create_widgets()
        
    def _setup_window(self) -> None:
        """Setup the main window properties."""
        self.root.title(f"{self.settings.app_name} v{self.settings.app_version}")
        self.root.geometry(f"{self.settings.get('ui.window_width', 850)}x{self.settings.get('ui.window_height', 700)}")
        self.root.configure(bg=self.settings.get('ui.bg_color', '#2b2b2b'))
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_input_section()
        self._create_control_section()
        self._create_output_section()
        self._create_status_section()
    
    def _create_header_section(self) -> None:
        """Create the header section with title."""
        header_frame = self.ui_styles.create_card_frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = self.ui_styles.create_header_label(
            header_frame, 
            text="Network Security Scanner"
        )
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Professional Network Assessment & Security Analysis Tool",
            style="Status.TLabel"
        )
        subtitle_label.pack()
    
    def _create_input_section(self) -> None:
        """Create the input section for scan parameters."""
        input_frame = self.ui_styles.create_card_frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Title
        ttk.Label(input_frame, text="Scan Configuration", style="Subheader.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        # Create input grid
        self.input_grid = ttk.Frame(input_frame)
        self.input_grid.pack(fill=tk.X, padx=10)
        
        # Scanner Name
        ttk.Label(self.input_grid, text="Scanner Name:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.entry_name = ttk.Entry(self.input_grid, width=30)
        self.entry_name.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 20))
        self.entry_name.insert(0, "Security Analyst")
        
        # Target Input
        ttk.Label(self.input_grid, text="Target:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(0, 10))
        self.entry_target = ttk.Entry(self.input_grid, width=40)
        self.entry_target.grid(row=0, column=3, sticky=tk.W, pady=5)
        self.entry_target.insert(0, "127.0.0.1")
        
        # Scan Profile
        ttk.Label(self.input_grid, text="Scan Profile:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        profile_names = [profile['name'] for profile in ScanProfiles.get_all_profiles().values()]
        self.combo_profile = ttk.Combobox(self.input_grid, values=profile_names, width=38, state="readonly")
        self.combo_profile.current(0)
        self.combo_profile.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(0, 20))
        
        # Custom Ports (optional)
        ttk.Label(self.input_grid, text="Custom Ports:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(0, 10))
        self.entry_ports = ttk.Entry(self.input_grid, width=40)
        self.entry_ports.grid(row=1, column=3, sticky=tk.W, pady=5)
        self.entry_ports.insert(0, "")
        
        # Help text
        help_text = "Examples: 192.168.1.1, 192.168.1.1-100, 192.168.1.0/24, example.com"
        ttk.Label(input_frame, text=help_text, style="Status.TLabel").pack(anchor=tk.W, padx=10, pady=(5, 0))
    
    def _create_control_section(self) -> None:
        """Create the control section with buttons."""
        control_frame = self.ui_styles.create_card_frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        # Scan button
        self.btn_scan = self.ui_styles.create_primary_button(
            button_frame,
            text="Start Scan",
            command=self.start_scan
        )
        self.btn_scan.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button (initially disabled)
        self.btn_stop = self.ui_styles.create_danger_button(
            button_frame,
            text="Stop Scan",
            command=self.stop_scan,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 10))
        
        # Report button
        self.btn_report = self.ui_styles.create_success_button(
            button_frame,
            text="Generate Report",
            command=self.generate_report,
            state=tk.DISABLED
        )
        self.btn_report.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.btn_clear = self.ui_styles.create_secondary_button(
            button_frame,
            text="Clear Output",
            command=self.clear_output
        )
        self.btn_clear.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame,
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
    
    def _create_output_section(self) -> None:
        """Create the output section for scan logs."""
        output_frame = self.ui_styles.create_card_frame(self.main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Header
        header_frame = ttk.Frame(output_frame)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(header_frame, text="Scan Output & Logs", style="Subheader.TLabel").pack(side=tk.LEFT)
        
        # Output text area
        self.text_output = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            wrap=tk.WORD
        )
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Apply styling to text widget
        self.ui_styles.create_scrolled_text_style(self.text_output)
        
        # Initial welcome message
        self.log_message("=== Enterprise Network Scanner ===")
        self.log_message(f"Version: {self.settings.app_version}")
        self.log_message(f"Nmap Version: {self.scanner.get_nmap_version()}")
        self.log_message("Ready to scan. Configure parameters and click 'Start Scan'.")
        self.log_message("=" * 50)
    
    def _create_status_section(self) -> None:
        """Create the status bar."""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Add timestamp
        self.timestamp_label = ttk.Label(
            self.status_frame,
            text="",
            style="Status.TLabel"
        )
        self.timestamp_label.pack(side=tk.RIGHT)
        
        self.update_timestamp()
    
    def log_message(self, message: str) -> None:
        """
        Log a message to the output area.
        
        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.text_output.insert(tk.END, formatted_message + "\n")
        self.text_output.see(tk.END)
        
        # Update status if this is an important message
        if any(keyword in message.lower() for keyword in ['error', 'failed', 'completed', 'starting']):
            self.update_status(message)
    
    def update_status(self, message: str) -> None:
        """
        Update the status bar.
        
        Args:
            message: Status message
        """
        # Truncate long messages
        if len(message) > 50:
            message = message[:47] + "..."
        
        self.status_label.config(text=message)
    
    def update_timestamp(self) -> None:
        """Update the timestamp display."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.config(text=current_time)
        
        # Update every second
        self.root.after(1000, self.update_timestamp)
    
    def start_scan(self) -> None:
        """Start the network scan."""
        if self.is_scanning:
            return
        
                
        # Get and validate inputs
        target = self.entry_target.get().strip()
        scanner_name = self.entry_name.get().strip()
        profile_name = self.combo_profile.get()
        custom_ports = self.entry_ports.get().strip()
        
        # Find profile key from profile name
        profile_key = None
        for key, profile in ScanProfiles.get_all_profiles().items():
            if profile['name'] == profile_name:
                profile_key = key
                break
        
        if not profile_key:
            messagebox.showerror("Error", "Invalid scan profile selected")
            return
        
        # Validate inputs
        try:
            is_valid, error_msg = InputValidator.validate_target(target)
            if not is_valid:
                messagebox.showerror("Validation Error", f"Invalid target: {error_msg}")
                return
            
            is_valid, error_msg = InputValidator.validate_scanner_name(scanner_name)
            if not is_valid:
                messagebox.showerror("Validation Error", f"Invalid scanner name: {error_msg}")
                return
            
            if custom_ports:
                is_valid, error_msg, ports = InputValidator.validate_port_range(custom_ports)
                if not is_valid:
                    messagebox.showerror("Validation Error", f"Invalid port range: {error_msg}")
                    return
        
        except ValidationError as e:
            messagebox.showerror("Validation Error", e.message)
            return
        
        # Create scan request
        request = ScanRequest(
            target=target,
            scanner_name=scanner_name,
            profile=profile_key,
            ports=custom_ports if custom_ports else None,
            timeout=self.settings.get('scanning.timeout', 300)
        )
        
        # Update UI state
        self.is_scanning = True
        self.btn_scan.config(state=tk.DISABLED, text="Scanning...")
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_report.config(state=tk.DISABLED)
        
        # Start progress bar
        self.progress_bar.start(10)
        
        # Clear previous results
        self.scan_results = []
        self.clear_output()
        
        # Log scan start
        self.log_message(f"Starting scan on: {target}")
        self.log_message(f"Scanner: {scanner_name}")
        self.log_message(f"Profile: {profile_name}")
        self.log_message(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message("-" * 50)
        
        # Start scan asynchronously
        self.scanner.scan_async(
            request,
            completion_callback=self._on_scan_complete,
            error_callback=self._on_scan_error
        )
    
    def stop_scan(self) -> None:
        """Stop the current scan."""
        if not self.is_scanning:
            return
        
        self.scanner.stop_scan()
        self.log_message("Scan stopped by user")
        self._reset_ui_state()
    
    def _on_scan_complete(self, results: list) -> None:
        """Handle scan completion."""
        self.scan_results = results
        self.log_message(f"Scan completed successfully! Found {len(results)} host(s).")
        
        # Show statistics
        stats = self.scanner.get_scan_stats()
        if stats:
            self.log_message(f"Statistics: {stats.get('up_hosts', 0)} hosts up, {stats.get('open_ports', 0)} open ports")
        
        self._reset_ui_state()
    
    def _on_scan_error(self, error: ScanError) -> None:
        """Handle scan error."""
        self.log_message(f"Scan failed: {error.message}")
        messagebox.showerror("Scan Error", error.message)
        self._reset_ui_state()
    
    def _reset_ui_state(self) -> None:
        """Reset UI state after scan completion."""
        self.is_scanning = False
        self.btn_scan.config(state=tk.NORMAL, text="Start Scan")
        self.btn_stop.config(state=tk.DISABLED)
        
        # Enable report button if we have results
        if self.scan_results:
            self.btn_report.config(state=tk.NORMAL)
        
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_var.set(0)
    
    def clear_output(self) -> None:
        """Clear the output area."""
        self.text_output.delete(1.0, tk.END)
    
    def generate_report(self) -> None:
        """Generate HTML report."""
        if not self.scan_results:
            messagebox.showwarning("No Data", "No scan results available for report generation")
            return
        
        # Get file path from user
        target = self.entry_target.get().strip()
        scanner_name = self.entry_name.get().strip()
        
        default_filename = f"scan_report_{target.replace('.', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=default_filename,
            title="Save Scan Report",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Generate report
            generator = HTMLReportGenerator()
            output_path = generator.generate_report(
                results=self.scan_results,
                target=target,
                scanner_name=scanner_name,
                output_path=file_path,
                include_summary=True,
                include_recommendations=True
            )
            
            self.log_message(f"Report generated successfully: {output_path}")
            messagebox.showinfo("Success", f"Report saved to:\n{output_path}")
            
        except Exception as e:
            error_msg = f"Failed to generate report: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Report Error", error_msg)
    
    def _on_closing(self) -> None:
        """Handle window closing event."""
        if self.is_scanning:
            if messagebox.askokcancel("Scan in Progress", "A scan is currently running. Do you want to stop it and exit?"):
                self.scanner.stop_scan()
                self.root.destroy()
        else:
            self.root.destroy()
