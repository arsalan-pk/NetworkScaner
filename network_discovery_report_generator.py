import os
import webbrowser
from datetime import datetime
from tkinter import messagebox


class NetworkDiscoveryReportGenerator:
    """Handles HTML report generation for network discovery results."""
    
    def __init__(self, scanner):
        self.scanner = scanner
    
    def generate_html_report(self, target, scanner_name, scan_profile, open_in_browser=True):
        """Generate and save HTML report for network discovery results."""
        try:
            # Create separate Network Discovery Reports directory
            reports_dir = os.path.join(os.getcwd(), "Reports", "Network_Discovery")
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"network_discovery_{target.replace('.', '_').replace('/', '_')}_{timestamp}.html"
            
            # Ask user where to save the report
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                initialdir=reports_dir,
                initialfile=default_filename,
                title="Save Network Discovery Report",
                filetypes=[("HTML files", "*.html")]
            )
            
            if not file_path:
                return False
            
            # Generate the HTML content
            scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html_content = self._build_network_discovery_report(target, scanner_name, scan_date, scan_profile)
            
            # Save the report
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            messagebox.showinfo("Success", f"Network Discovery Report successfully saved to:\n{file_path}")
            
            # Open report in browser
            if open_in_browser:
                self._open_report_in_browser(file_path)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Network Discovery report:\n{str(e)}")
            return False
    
    def _open_report_in_browser(self, file_path):
        """Open the HTML report in browser."""
        try:
            webbrowser.open(f'file://{os.path.abspath(file_path)}')
        except Exception as e:
            messagebox.showwarning("Browser Error", f"Could not open report in browser:\n{str(e)}")
    
    def _build_network_discovery_report(self, target, scanner_name, scan_date, scan_profile):
        """Build HTML report for network discovery results."""
        html_content = self._get_html_header(target)
        html_content += self._get_meta_info_section(target, scanner_name, scan_date, scan_profile)
        
        if self.scanner.all_hosts():
            for host in self.scanner.all_hosts():
                html_content += self._get_host_section(host)
        else:
            html_content += """
                <div class="host-card">
                    <h2>No Hosts Discovered</h2>
                    <p>No active hosts were found on the network. This could indicate:</p>
                    <ul>
                        <li>Hosts are blocking ping requests</li>
                        <li>Network configuration issues</li>
                        <li>Firewall restrictions</li>
                    </ul>
                </div>
            """
        
        html_content += self._get_html_footer(scan_date)
        return html_content
    
    def _get_html_header(self, target):
        """Generate HTML header for network discovery report."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Network Discovery Report - {target}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; line-height: 1.6; margin: 0; padding: 20px; }}
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
                .discovery {{ background-color: #3498db; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #2c3e50; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
                .stats {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Network Discovery Scan Report</h1>
                    <p><span class="badge discovery">Network Discovery Mode</span></p>
                </div>
        """
    
    def _get_meta_info_section(self, target, scanner_name, scan_date, scan_profile):
        """Generate meta information section for network discovery report."""
        return f"""
                <div class="meta-info">
                    <p><strong>Network Range Scanned:</strong> {target}</p>
                    <p><strong>Scan Performed By:</strong> {scanner_name}</p>
                    <p><strong>Date & Time of Scan:</strong> {scan_date}</p>
                    <p><strong>Scan Type:</strong> {scan_profile}</p>
                    <p><strong>Scan Method:</strong> Ping Scan (-sn -n)</p>
                </div>
        """
    
    def _get_host_section(self, host):
        """Generate HTML section for a discovered host."""
        state = self.scanner[host].state()
        state_class = "up" if state == 'up' else "down"
        hostname = self.scanner[host].hostname()
        
        html_content = f"""
                <div class="host-card">
                    <h2>Host: {host} {f'({hostname})' if hostname else ''}</h2>
                    <p>Status: <span class="badge {state_class}">{state.upper()}</span></p>
                    <p><strong>Discovery Method:</strong> Ping Response</p>
        """
        
        # Add MAC address if available
        if 'addresses' in self.scanner[host] and 'mac' in self.scanner[host]['addresses']:
            mac = self.scanner[host]['addresses']['mac']
            vendor = self.scanner[host]['addresses'].get('vendor', 'Unknown')
            html_content += f"<p><strong>MAC Address:</strong> {mac} ({vendor})</p>"
        
        html_content += "</div>"  # close host-card
        return html_content
    
    def _get_html_footer(self, scan_date):
        """Generate HTML footer for network discovery report."""
        return f"""
                <div class="footer">
                    <p>Generated by Network Discovery Scanner | Report completed on {scan_date}</p>
                    <p><em>Note: This report shows active hosts discovered through ping scanning. For detailed port and service information, run a comprehensive scan.</em></p>
                </div>
            </div>
        </body>
        </html>
        """
