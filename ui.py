import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


class NetworkScannerUI:
    """Handles all UI components for the Network Scanner application."""
    
    def __init__(self, root, scan_callback, report_callback, mode="target"):
        self.root = root
        self.scan_callback = scan_callback
        self.report_callback = report_callback
        self.mode = mode  # "network" or "target"
        
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
        if self.mode == "network":
            title = "Network Discovery Scanner - Developed by Arsalan Khan"
            default_target = "192.168.1.0/24"
        else:
            title = "Target IP Scanner - Developed by Arsalan Khan"
            default_target = "127.0.0.1"
        
        self.root.title(title)
        self.root.geometry("850x700")
        self.root.configure(bg="#2b2b2b")
        self.default_target = default_target
    
    def _setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="#e0e0e0", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#4a90e2")
        
        # Enhanced button styling
        style.configure("TButton", 
                       font=("Helvetica", 11, "bold"), 
                       background="#4a90e2", 
                       foreground="white", 
                       padding=10,
                       borderwidth=0,
                       focuscolor='none',
                       relief="flat")
        style.map('TButton', 
                 background=[('active', '#357abd'), ('pressed', '#2968a3')],
                 relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # Enhanced entry styling
        style.configure("TEntry", 
                       fieldbackground="#3c3f41", 
                       foreground="#ffffff",
                       borderwidth=1,
                       relief="solid",
                       padding=8,
                       insertcolor="#ffffff")
        style.map("TEntry", 
                 focuscolor=[('focus', 'none')],
                 bordercolor=[('focus', '#4a90e2')])
        
        # Enhanced combobox styling
        style.configure("TCombobox", 
                       fieldbackground="#3c3f41", 
                       foreground="#ffffff",
                       borderwidth=1,
                       relief="solid",
                       padding=8,
                       arrowcolor="#e0e0e0")
        style.map("TCombobox", 
                 focuscolor=[('focus', 'none')],
                 bordercolor=[('focus', '#4a90e2')])
    
    def _create_widgets(self):
        """Create all UI widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Title
        if self.mode == "network":
            title_text = "Network Discovery Scanner"
        else:
            title_text = "Target IP Scanner"
        
        lbl_title = ttk.Label(main_frame, text=title_text, style="Header.TLabel")
        lbl_title.pack(pady=(0, 20))

        # Inputs Frame with enhanced styling
        input_container = ttk.Frame(main_frame)
        input_container.pack(fill=tk.X, pady=10)
        
        # Add a subtle background frame for inputs
        input_frame = ttk.Frame(input_container, relief="solid", borderwidth=1)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Inner padding for inputs
        inner_frame = ttk.Frame(input_frame, padding="15")
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # Scanner Name Input
        ttk.Label(inner_frame, text="Scanner Name:", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(8, 8), padx=(0, 15))
        self.entry_name = ttk.Entry(inner_frame, width=35, font=("Helvetica", 10))
        self.entry_name.grid(row=0, column=1, pady=(8, 8), padx=(0, 10), sticky=tk.W)
        self.entry_name.insert(0, "Anonymous")

        # Target IP/Network Input
        if self.mode == "network":
            target_label = "Network Range:"
        else:
            target_label = "Target IP/Domain:"
        
        ttk.Label(inner_frame, text=target_label, font=("Helvetica", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=(8, 8), padx=(0, 15))
        self.entry_target = ttk.Entry(inner_frame, width=35, font=("Helvetica", 10))
        self.entry_target.grid(row=1, column=1, pady=(8, 8), padx=(0, 10), sticky=tk.W)
        self.entry_target.insert(0, self.default_target)

        # Scan Type Selection
        ttk.Label(inner_frame, text="Scan Profile:", font=("Helvetica", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(8, 8), padx=(0, 15))
        
        # Different scan profiles for different modes
        if self.mode == "network":
            scan_profiles = [
                "Network Discovery (Ping Scan)",
                "Quick Network Scan",
                "Comprehensive Network Scan"
            ]
        else:
            scan_profiles = [
                "Intense Scan (OS, Services, Default Scripts)",
                "Quick Scan",
                "Ping Scan (Host Discovery)"
            ]
        
        self.combo_profile = ttk.Combobox(inner_frame, values=scan_profiles, width=42, state="readonly", font=("Helvetica", 10))
        self.combo_profile.current(0)
        self.combo_profile.grid(row=2, column=1, pady=(8, 8), padx=(0, 10), sticky=tk.W)

        # Enhanced Buttons Frame
        btn_container = ttk.Frame(main_frame)
        btn_container.pack(fill=tk.X, pady=20)
        
        # Top button row with back button
        top_btn_frame = ttk.Frame(btn_container)
        top_btn_frame.pack(anchor=tk.CENTER, pady=(0, 10))
        
        self.btn_back = ttk.Button(
            top_btn_frame, 
            text="← Back to Welcome", 
            command=self.back_to_welcome,
            width=20
        )
        self.btn_back.pack()
        
        # Main action buttons
        btn_frame = ttk.Frame(btn_container)
        btn_frame.pack(anchor=tk.CENTER)

        # Create styled buttons with better spacing
        self.btn_scan = ttk.Button(
            btn_frame, 
            text="▶ Start Scan", 
            command=self.scan_callback,
            width=15
        )
        self.btn_scan.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_report = ttk.Button(
            btn_frame, 
            text="📄 Generate Report", 
            command=self.report_callback, 
            state=tk.DISABLED,
            width=18
        )
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
    
    def back_to_welcome(self):
        """Return to welcome screen."""
        from welcome_screen import WelcomeScreen
        
        # Clear current screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show welcome screen
        WelcomeScreen(self.root)
