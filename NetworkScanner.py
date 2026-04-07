import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import nmap
import threading
from datetime import datetime
import os
from report_generator import ReportGenerator

class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kali-Linux Network & OS Scanner")
        self.root.geometry("850x700")
        self.root.configure(bg="#2b2b2b")
        
        # Scanner Instance
        try:
            self.scanner = nmap.PortScanner()
        except nmap.PortScannerError:
            messagebox.showerror("Nmap Not Found", "Nmap is not installed or not in your PATH. Please install it (e.g., sudo apt install nmap).")
            self.root.destroy()
            return
            
        self.scan_results = {}
        self.is_scanning = False
        
        # Initialize report generator
        self.report_generator = ReportGenerator(self.scanner)
        
        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
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
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Title
        lbl_title = ttk.Label(main_frame, text="Network & OS Discovery Scanner", style="Header.TLabel")
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

        self.btn_scan = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan_thread)
        self.btn_scan.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_report = ttk.Button(btn_frame, text="Generate HTML Report", command=self.generate_report, state=tk.DISABLED)
        self.btn_report.pack(side=tk.LEFT)

        # Output Text Area
        ttk.Label(main_frame, text="Scan Logs:").pack(anchor=tk.W, pady=(10, 5))
        self.text_output = scrolledtext.ScrolledText(main_frame, height=15, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.text_output.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.see(tk.END)

    def start_scan_thread(self):
        if self.is_scanning:
            return

        target = self.entry_target.get().strip()
        scanner_name = self.entry_name.get().strip()

        if not target:
            messagebox.showwarning("Input Error", "Please provide a target.")
            return
        
        if not scanner_name:
            messagebox.showwarning("Input Error", "Please provide the scanner's name.")
            return

        self.is_scanning = True
        self.btn_scan.config(state=tk.DISABLED, text="Scanning...")
        self.btn_report.config(state=tk.DISABLED)
        self.text_output.delete(1.0, tk.END)
        self.log(f"[*] Starting scan on target: {target}")
        self.log(f"[*] Initiated by: {scanner_name}")
        self.log(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("-" * 60)

        # Run scan in a separate thread to keep user interface responsive
        threading.Thread(target=self.run_scan, args=(target,), daemon=True).start()

    def run_scan(self, target):
        profile = self.combo_profile.get()
        
        # Determine Nmap arguments based on selected profile
        args = ""
        if "Intense" in profile:
            args = "-A -T4"  # -A enables OS detection, version detection, script scanning, traceroute
        elif "Quick" in profile:
            args = "-T4 -F"  # Fast scan (fewer ports)
        elif "Ping" in profile:
            args = "-sn"     # Ping scan only

        try:
            self.log(f"[*] Running command: nmap {args} {target}")
            self.scanner.scan(hosts=target, arguments=args)
            
            self.scan_results = self.scanner.csv()  # Just store CSV locally if needed
            
            # Print simplified results to log
            if not self.scanner.all_hosts():
                self.log("[!] Target seems down or blocking probe packets.")
            else:
                for host in self.scanner.all_hosts():
                    self.log(f"\n[+] Host: {host} (" + self.scanner[host].hostname() + ")")
                    self.log(f"[+] State: {self.scanner[host].state()}")
                    
                    if 'osmatch' in self.scanner[host] and self.scanner[host]['osmatch']:
                        os_name = self.scanner[host]['osmatch'][0]['name']
                        self.log(f"[+] Detected OS: {os_name}")
                    else:
                        self.log("[-] OS Detection Note: Run with 'sudo' for accurate OS detection.")

                    for proto in self.scanner[host].all_protocols():
                        self.log(f"========== Protocol: {proto} ==========")
                        ports = self.scanner[host][proto].keys()
                        for port in sorted(ports):
                            state = self.scanner[host][proto][port]['state']
                            name = self.scanner[host][proto][port]['name']
                            version = self.scanner[host][proto][port]['version']
                            extrainfo = self.scanner[host][proto][port]['extrainfo']
                            info = f"Port: {port}\tState: {state}\tService: {name}\tVersion: {version} {extrainfo}".strip()
                            self.log(info)

            self.log("\n[*] Scan Completed Successfully.")
            self.root.after(0, self._scan_finished, True)
            
        except Exception as e:
            self.log(f"\n[!] Error during scan: {str(e)}")
            self.root.after(0, self._scan_finished, False)

    def _scan_finished(self, success):
        self.is_scanning = False
        self.btn_scan.config(state=tk.NORMAL, text="Start Scan")
        if success and self.scanner.all_hosts():
            self.btn_report.config(state=tk.NORMAL)

    def generate_report(self):
        """Generate HTML report using the modular report generator."""
        target = self.entry_target.get()
        scanner_name = self.entry_name.get()
        scan_profile = self.combo_profile.get()
        
        self.report_generator.generate_html_report(target, scanner_name, scan_profile)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
