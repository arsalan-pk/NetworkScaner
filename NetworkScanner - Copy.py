import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import nmap
import threading
from datetime import datetime
import os

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
        target = self.entry_target.get()
        scanner_name = self.entry_name.get()
        scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create output file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=f"scan_report_{target.replace('.', '_')}.html",
            title="Save Clean Report",
            filetypes=[("HTML files", "*.html")]
        )

        if not file_path:
            return

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Scan Report - {target}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; line-height: 1.6; margin: 0; padding: 20px; }}
                max-width: 1000px; margin: 0 auto;
                .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ border-bottom: 2px solid #2c3e50; padding-bottom: 15px; margin-bottom: 25px; }}
                .header h1 {{ color: #2c3e50; margin: 0 0 10px 0; }}
                .meta-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 25px; }}
                .meta-info p {{ margin: 5px 0; }}
                h2 {{ color: #34495e; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                .host-card {{ background: #fafafa; border: 1px solid #ddd; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .badge {{ padding: 5px 10px; border-radius: 3px; font-weight: bold; color: white; font-size: 0.9em; }}
                .up {{ background-color: #27ae60; }}
                .down {{ background-color: #e74c3c; }}
                .open {{ background-color: #2ecc71; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }}
                .closed {{ background-color: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #2c3e50; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Network Security Scan Report</h1>
                </div>
                
                <div class="meta-info">
                    <p><strong>Target Assessed:</strong> {target}</p>
                    <p><strong>Scan Performed By:</strong> {scanner_name}</p>
                    <p><strong>Date & Time of Scan:</strong> {scan_date}</p>
                    <p><strong>Scan Type:</strong> {self.combo_profile.get()}</p>
                </div>
        """

        for host in self.scanner.all_hosts():
            state = self.scanner[host].state()
            state_class = "up" if state == 'up' else "down"
            hostname = self.scanner[host].hostname()
            
            os_info = "Unknown (Requires root privileges for OS detection)"
            if 'osmatch' in self.scanner[host] and self.scanner[host]['osmatch']:
                os_info = self.scanner[host]['osmatch'][0]['name']

            html_content += f"""
                <div class="host-card">
                    <h2>Host: {host} {f'({hostname})' if hostname else ''}</h2>
                    <p>Status: <span class="badge {state_class}">{state.upper()}</span></p>
                    <p><strong>Operating System Detected:</strong> {os_info}</p>
            """

            for proto in self.scanner[host].all_protocols():
                html_content += f"""
                    <h3>Protocol: {proto.upper()} Details</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Port</th>
                                <th>State</th>
                                <th>Service</th>
                                <th>Version / Details</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                ports = self.scanner[host][proto].keys()
                for port in sorted(ports):
                    port_info = self.scanner[host][proto][port]
                    port_state = port_info['state']
                    port_state_class = "open" if port_state == 'open' else "closed"
                    
                    html_content += f"""
                            <tr>
                                <td>{port}</td>
                                <td><span class="{port_state_class}">{port_state}</span></td>
                                <td>{port_info['name']}</td>
                                <td>{port_info['version']} {port_info.get('extrainfo', '')}</td>
                            </tr>
                    """

                html_content += """
                        </tbody>
                    </table>
                """

            html_content += "</div>" # close host-card

        html_content += f"""
                <div class="footer">
                    <p>Generated by Network & OS Discovery Scanner | Report completed on {scan_date}</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            messagebox.showinfo("Success", f"Report successfully saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
