import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


class NetworkScannerUI:
    """Handles all UI components for the Network Scanner application."""
    
    def __init__(self, root, scan_callback, report_callback):
        self.root = root
        self.scan_callback = scan_callback
        self.report_callback = report_callback
        
        # UI Components
        self.entry_name = None
        self.entry_target = None
        self.combo_profile = None
        self.btn_scan = None
        self.btn_report = None
        self.text_output = None
        
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure the main window."""
        self.root.title("Network Scanner Developed by Arsalan Khan")
        self.root.geometry("850x700")
        self.root.configure(bg="#2b2b2b")
    
    def _setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="#e0e0e0", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#4a90e2")
        style.configure("TButton", font=("Helvetica", 11, "bold"), background="#4a90e2", foreground="white", padding=5)
        style.map('TButton', background=[('active', '#357abd')])
        style.configure("TEntry", fieldbackground="#3c3f41", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#3c3f41", foreground="#ffffff")
    
    def _create_widgets(self):
        """Create all UI widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Title
        lbl_title = ttk.Label(main_frame, text="Network Scanner", style="Header.TLabel")
        lbl_title.pack(pady=(0, 20))

        # Inputs Frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)

        # Scanner Name Input
        ttk.Label(input_frame, text="Scanner Name:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.entry_name = ttk.Entry(input_frame, width=30)
        self.entry_name.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        self.entry_name.insert(0, "Anonymous")

        # Target IP Input
        ttk.Label(input_frame, text="Target IP/Domain:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.entry_target = ttk.Entry(input_frame, width=30)
        self.entry_target.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        self.entry_target.insert(0, "127.0.0.1")

        # Scan Type Selection
        ttk.Label(input_frame, text="Scan Profile:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.combo_profile = ttk.Combobox(input_frame, values=[
            "Intense Scan (OS, Services, Default Scripts)",
            "Quick Scan",
            "Ping Scan (Host Discovery)"
        ], width=40, state="readonly")
        self.combo_profile.current(0)
        self.combo_profile.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        # Buttons Frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)

        self.btn_scan = ttk.Button(btn_frame, text="Start Scan", command=self.scan_callback)
        self.btn_scan.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_report = ttk.Button(btn_frame, text="Generate HTML Report", command=self.report_callback, state=tk.DISABLED)
        self.btn_report.pack(side=tk.LEFT)

        # Output Text Area
        ttk.Label(main_frame, text="Scan Logs:").pack(anchor=tk.W, pady=(10, 5))
        self.text_output = scrolledtext.ScrolledText(main_frame, height=15, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.text_output.pack(fill=tk.BOTH, expand=True)
    
    def get_scan_inputs(self):
        """Get scan input values from UI."""
        target = self.entry_target.get().strip()
        scanner_name = self.entry_name.get().strip()
        profile = self.combo_profile.get()
        return target, scanner_name, profile
    
    def validate_inputs(self):
        """Validate user inputs."""
        target, scanner_name, _ = self.get_scan_inputs()
        
        if not target:
            messagebox.showwarning("Input Error", "Please provide a target.")
            return False
        
        if not scanner_name:
            messagebox.showwarning("Input Error", "Please provide the scanner's name.")
            return False
        
        return True
    
    def log(self, message):
        """Add a message to the output log."""
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.see(tk.END)
    
    def clear_log(self):
        """Clear the output log."""
        self.text_output.delete(1.0, tk.END)
    
    def set_scanning_state(self, is_scanning):
        """Update UI state based on scanning status."""
        if is_scanning:
            self.btn_scan.config(state=tk.DISABLED, text="Scanning...")
            self.btn_report.config(state=tk.DISABLED)
        else:
            self.btn_scan.config(state=tk.NORMAL, text="Start Scan")
    
    def enable_report_button(self):
        """Enable the report generation button."""
        self.btn_report.config(state=tk.NORMAL)
