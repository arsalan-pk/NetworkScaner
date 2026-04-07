import os
from datetime import datetime
from tkinter import filedialog, messagebox


class ReportGenerator:
    """Handles HTML report generation for network scan results."""
    
    def __init__(self, scanner):
        self.scanner = scanner
    
    def generate_html_report(self, target, scanner_name, scan_profile):
        """Generate and save HTML report for scan results."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=f"scan_report_{target.replace('.', '_')}.html",
            title="Save Clean Report",
            filetypes=[("HTML files", "*.html")]
        )
        
        if not file_path:
            return False
        
        scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = self._build_html_report(target, scanner_name, scan_date, scan_profile)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            messagebox.showinfo("Success", f"Report successfully saved to:\n{file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")
            return False
    
    def _build_html_report(self, target, scanner_name, scan_date, scan_profile):
        """Build the complete HTML report content."""
        html_content = self._get_html_header(target)
        html_content += self._get_meta_info_section(target, scanner_name, scan_date, scan_profile)
        
        for host in self.scanner.all_hosts():
            html_content += self._get_host_section(host)
        
        html_content += self._get_html_footer(scan_date)
        return html_content
    
    def _get_html_header(self, target):
        """Generate the HTML header section with CSS styles."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Scan Report - {target}</title>
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
        """
    
    def _get_meta_info_section(self, target, scanner_name, scan_date, scan_profile):
        """Generate the meta information section of the report."""
        return f"""
                <div class="meta-info">
                    <p><strong>Target Assessed:</strong> {target}</p>
                    <p><strong>Scan Performed By:</strong> {scanner_name}</p>
                    <p><strong>Date & Time of Scan:</strong> {scan_date}</p>
                    <p><strong>Scan Type:</strong> {scan_profile}</p>
                </div>
        """
    
    def _get_host_section(self, host):
        """Generate the HTML section for a specific host."""
        state = self.scanner[host].state()
        state_class = "up" if state == 'up' else "down"
        hostname = self.scanner[host].hostname()
        
        os_info = self._get_os_info(host)
        
        html_content = f"""
                <div class="host-card">
                    <h2>Host: {host} {f'({hostname})' if hostname else ''}</h2>
                    <p>Status: <span class="badge {state_class}">{state.upper()}</span></p>
                    <p><strong>Operating System Detected:</strong> {os_info}</p>
        """
        
        for proto in self.scanner[host].all_protocols():
            html_content += self._get_protocol_section(host, proto)
        
        html_content += "</div>"  # close host-card
        return html_content
    
    def _get_os_info(self, host):
        """Extract OS information for a host."""
        if 'osmatch' in self.scanner[host] and self.scanner[host]['osmatch']:
            return self.scanner[host]['osmatch'][0]['name']
        return "Unknown (Requires root privileges for OS detection)"
    
    def _get_protocol_section(self, host, protocol):
        """Generate the HTML section for a specific protocol."""
        html_content = f"""
                    <h3>Protocol: {protocol.upper()} Details</h3>
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
        
        ports = self.scanner[host][protocol].keys()
        for port in sorted(ports):
            html_content += self._get_port_row(host, protocol, port)
        
        html_content += """
                        </tbody>
                    </table>
        """
        return html_content
    
    def _get_port_row(self, host, protocol, port):
        """Generate HTML table row for a specific port."""
        port_info = self.scanner[host][protocol][port]
        port_state = port_info['state']
        port_state_class = "open" if port_state == 'open' else "closed"
        
        return f"""
                            <tr>
                                <td>{port}</td>
                                <td><span class="{port_state_class}">{port_state}</span></td>
                                <td>{port_info['name']}</td>
                                <td>{port_info['version']} {port_info.get('extrainfo', '')}</td>
                            </tr>
        """
    
    def _get_html_footer(self, scan_date):
        """Generate the HTML footer section."""
        return f"""
                <div class="footer">
                    <p>Generated by Network & OS Discovery Scanner | Report completed on {scan_date}</p>
                </div>
            </div>
        </body>
        </html>
        """
