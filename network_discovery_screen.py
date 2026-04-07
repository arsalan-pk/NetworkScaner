import tkinter as tk
from tkinter import ttk, Canvas
import math
import threading
import subprocess
import re
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
            width=250, 
            height=250, 
            bg="#001100", 
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
            text="� Radar Scanner",
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
        """Animate realistic radar scanner."""
        if not self.is_loading:
            return
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Radar parameters
        center_x, center_y = 125, 125
        radius = 100
        
        # Draw radar circles (concentric circles)
        for i in range(1, 5):
            r = radius * (i / 4)
            self.canvas.create_oval(
                center_x - r, center_y - r,
                center_x + r, center_y + r,
                outline="#1a472a", width=1
            )
        
        # Draw radar cross lines
        # Horizontal line
        self.canvas.create_line(
            center_x - radius, center_y,
            center_x + radius, center_y,
            fill="#1a472a", width=1
        )
        # Vertical line
        self.canvas.create_line(
            center_x, center_y - radius,
            center_x, center_y + radius,
            fill="#1a472a", width=1
        )
        # Diagonal lines
        self.canvas.create_line(
            center_x - radius*0.7, center_y - radius*0.7,
            center_x + radius*0.7, center_y + radius*0.7,
            fill="#1a472a", width=1
        )
        self.canvas.create_line(
            center_x - radius*0.7, center_y + radius*0.7,
            center_x + radius*0.7, center_y - radius*0.7,
            fill="#1a472a", width=1
        )
        
        # Draw sweeping radar line
        sweep_angle = self.loading_angle
        sweep_end_x = center_x + radius * math.cos(math.radians(sweep_angle))
        sweep_end_y = center_y - radius * math.sin(math.radians(sweep_angle))
        
        # Main sweep line
        self.canvas.create_line(
            center_x, center_y,
            sweep_end_x, sweep_end_y,
            fill="#00ff00", width=2
        )
        
        # Fade effect - draw trailing sweep lines
        for i in range(1, 4):
            fade_angle = sweep_angle - (i * 15)
            fade_end_x = center_x + radius * math.cos(math.radians(fade_angle))
            fade_end_y = center_y - radius * math.sin(math.radians(fade_angle))
            alpha = 255 - (i * 60)
            color = f"#{0:02x}{alpha:02x}{0:02x}" if alpha > 0 else "#001100"
            self.canvas.create_line(
                center_x, center_y,
                fade_end_x, fade_end_y,
                fill=color, width=2
            )
        
        # Add random target blips
        if self.loading_angle % 30 == 0:  # Add new blip every 30 degrees
            import random
            blip_angle = random.randint(0, 360)
            blip_distance = random.randint(20, radius - 10)
            blip_x = center_x + blip_distance * math.cos(math.radians(blip_angle))
            blip_y = center_y - blip_distance * math.sin(math.radians(blip_angle))
            
            # Draw target blip
            self.canvas.create_oval(
                blip_x - 3, blip_y - 3,
                blip_x + 3, blip_y + 3,
                fill="#ff0000", outline="#ff6666"
            )
        
        # Update angle for next frame
        self.loading_angle = (self.loading_angle + 3) % 360
        
        # Schedule next frame
        self.root.after(30, self.animate_loading)
    
        
    def _get_local_network_info(self):
        """Get local IP address and subnet mask using system commands."""
        try:
            import platform
            system = platform.system().lower()
            
            if system == "windows":
                return self._get_windows_network_info()
            else:
                return self._get_linux_network_info()
                
        except Exception as e:
            raise Exception(f"Error getting network info: {str(e)}")
    
    def _get_windows_network_info(self):
        """Get network info on Windows using ipconfig."""
        try:
            # Run 'ipconfig' command to get network interface information
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"Failed to execute 'ipconfig' command: {result.stderr}")
            
            # Parse the output to find IPv4 addresses and subnet masks
            lines = result.stdout.split('\n')
            current_adapter = None
            adapters = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(' '):
                    # New adapter
                    current_adapter = {'name': line, 'ip': None, 'subnet': None}
                    adapters.append(current_adapter)
                elif current_adapter and 'IPv4 Address' in line:
                    # Extract IP address
                    ip_match = re.search(r'IPv4 Address[\.]*:\s*(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        current_adapter['ip'] = ip_match.group(1)
                elif current_adapter and 'Subnet Mask' in line:
                    # Extract subnet mask
                    subnet_match = re.search(r'Subnet Mask[\.]*:\s*(\d+\.\d+\.\d+\.\d+)', line)
                    if subnet_match:
                        current_adapter['subnet'] = subnet_match.group(1)
            
            # Find the first adapter with valid IP and subnet
            for adapter in adapters:
                if (adapter['ip'] and adapter['subnet'] and 
                    not adapter['ip'].startswith('127.') and 
                    not adapter['ip'].startswith('169.254.') and
                    not adapter['ip'].startswith('0.')):
                    
                    # Convert subnet mask to CIDR prefix
                    prefix_length = self._subnet_to_prefix_length(adapter['subnet'])
                    network_cidr = f"{adapter['ip']}/{prefix_length}"
                    return adapter['ip'], adapter['subnet'], network_cidr
            
            raise Exception("No suitable network interface found")
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout while executing 'ipconfig' command")
        except Exception as e:
            raise Exception(f"Error getting Windows network info: {str(e)}")
    
    def _get_linux_network_info(self):
        """Get network info on Linux using 'ip a' command."""
        try:
            # Run 'ip a' command to get network interface information
            result = subprocess.run(['ip', 'a'], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"Failed to execute 'ip a' command: {result.stderr}")
            
            # Parse the output to find IPv4 addresses
            ip_pattern = r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)'
            matches = re.findall(ip_pattern, result.stdout)
            
            if not matches:
                raise Exception("No IPv4 addresses found")
            
            # Find the first non-loopback interface
            for ip, prefix_length in matches:
                if not ip.startswith('127.') and not ip.startswith('169.254.'):
                    # Convert prefix length to subnet mask
                    subnet_mask = self._prefix_to_subnet_mask(int(prefix_length))
                    return ip, subnet_mask, f"{ip}/{prefix_length}"
            
            # If no suitable interface found, use the first one
            if matches:
                ip, prefix_length = matches[0]
                subnet_mask = self._prefix_to_subnet_mask(int(prefix_length))
                return ip, subnet_mask, f"{ip}/{prefix_length}"
            
            raise Exception("No suitable network interface found")
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout while executing 'ip a' command")
        except FileNotFoundError:
            raise Exception("'ip' command not found. Please install iproute2 package")
        except Exception as e:
            raise Exception(f"Error getting Linux network info: {str(e)}")
    
    def _subnet_to_prefix_length(self, subnet_mask):
        """Convert subnet mask to CIDR prefix length."""
        try:
            parts = list(map(int, subnet_mask.split('.')))
            binary_str = ''.join(f'{part:08b}' for part in parts)
            return binary_str.count('1')
        except:
            return 24  # Default to /24 if conversion fails
    
    def _prefix_to_subnet_mask(self, prefix_length):
        """Convert CIDR prefix length to subnet mask."""
        if prefix_length < 0 or prefix_length > 32:
            return "255.255.255.255"
        
        mask = (0xffffffff << (32 - prefix_length)) & 0xffffffff
        return ".".join(str((mask >> (8 * (3 - i))) & 0xff) for i in range(4))
    
    def _get_network_range(self, ip_with_prefix):
        """Extract network range from IP with prefix."""
        ip, prefix = ip_with_prefix.split('/')
        # Convert to network address by zeroing host bits
        ip_parts = list(map(int, ip.split('.')))
        prefix_length = int(prefix)
        
        if prefix_length <= 8:
            network = f"{ip_parts[0]}.0.0.0/{prefix_length}"
        elif prefix_length <= 16:
            network = f"{ip_parts[0]}.{ip_parts[1]}.0.0/{prefix_length}"
        elif prefix_length <= 24:
            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/{prefix_length}"
        else:
            network = f"{ip}/{prefix_length}"
        
        return network

    def _perform_discovery(self):
        """Perform the actual network discovery."""
        try:
            # Initialize scanner
            scanner_core = ScannerCore(log_callback=self._log_message)
            
            # Get local network information
            self._log_message("Detecting local network configuration...")
            local_ip, subnet_mask, network_cidr = self._get_local_network_info()
            self._log_message(f"Local IP: {local_ip}")
            self._log_message(f"Subnet Mask: {subnet_mask}")
            self._log_message(f"Network Range: {network_cidr}")
            
            # Get network range for scanning
            target = self._get_network_range(network_cidr)
            self._log_message(f"Scanning network: {target}")
            
            # Perform network discovery scan
            profile = "Network Discovery (Ping Scan)"
            
            # Start the actual scan
            scanner_core.start_scan(
                target=target,
                profile=profile,
                scan_finished_callback=lambda success, hosts: self._scan_finished(success, hosts, scanner_core)
            )
            
        except Exception as e:
            self.is_loading = False
            self.root.after(0, self._show_error, str(e))
    
    def _scan_finished(self, success, hosts, scanner_core):
        """Handle scan completion."""
        self.is_loading = False
        if success:
            self.root.after(0, self._show_results, scanner_core)
        else:
            self.root.after(0, self._show_error, "Network scan failed")
    
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
            text="🎉 Radar Scan Complete!",
            font=("Helvetica", 16, "bold"),
            foreground="#27ae60",
            background="#2b2b2b"
        )
        results_label.pack(pady=10)
        
        # Add report button
        btn_report = ttk.Button(
            self.results_frame,
            text="� Generate Report",
            command=lambda: self.generate_report(scanner_core),
            style="Action.TButton"
        )
        btn_report.pack(pady=10)
    
    def _show_error(self, error_message):
        """Show discovery error."""
        self.canvas.pack_forget()
        self.loading_label.pack_forget()
        
        error_label = ttk.Label(
            self.results_frame,
            text=f"❌ Radar Scan Failed: {error_message}",
            font=("Helvetica", 12),
            foreground="#e74c3c",
            background="#2b2b2b"
        )
        error_label.pack(pady=20)
    
    def generate_report(self, scanner_core):
        """Generate HTML report from scan results."""
        try:
            from report_generator import ReportGenerator
            report_generator = ReportGenerator(scanner_core.get_scanner())
            
            # Get the network information that was used for scanning
            local_ip, subnet_mask, network_cidr = self._get_local_network_info()
            target = self._get_network_range(network_cidr)
            scanner_name = "Network Discovery Scanner"
            scan_profile = "Network Discovery (Ping Scan)"
            
            report_generator.generate_html_report(target, scanner_name, scan_profile)
        except Exception as e:
            print(f"Report generation failed: {e}")
    
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
