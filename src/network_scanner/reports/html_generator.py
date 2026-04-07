"""
HTML report generation for Network Scanner.

This module provides professional HTML report generation with
templates, styling, and comprehensive scan result presentation.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ..core.scanner import ScanResult
from ..core.exceptions import ReportGenerationError


class HTMLReportGenerator:
    """
    Professional HTML report generator for network scan results.
    
    Generates comprehensive, styled HTML reports with proper structure,
    responsive design, and detailed scan information.
    """
    
    def __init__(self, template_dir: Optional[str] = None) -> None:
        """
        Initialize HTML report generator.
        
        Args:
            template_dir: Directory containing HTML templates
        """
        self.template_dir = Path(template_dir) if template_dir else Path(__file__).parent / "templates"
        self._ensure_template_dir()
    
    def _ensure_template_dir(self) -> None:
        """Ensure template directory exists and contains default templates."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default template if it doesn't exist
        template_path = self.template_dir / "default_report.html"
        if not template_path.exists():
            self._create_default_template(template_path)
    
    def _create_default_template(self, template_path: Path) -> None:
        """Create default HTML template."""
        template_content = self._get_default_template()
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def generate_report(
        self, 
        results: List[ScanResult], 
        target: str, 
        scanner_name: str,
        output_path: str,
        include_summary: bool = True,
        include_recommendations: bool = True
    ) -> str:
        """
        Generate comprehensive HTML report.
        
        Args:
            results: List of scan results
            target: Target that was scanned
            scanner_name: Name of the person who performed the scan
            output_path: Path where to save the HTML report
            include_summary: Whether to include summary statistics
            include_recommendations: Whether to include security recommendations
            
        Returns:
            Path to generated report
            
        Raises:
            ReportGenerationError: If report generation fails
        """
        try:
            if not results:
                raise ReportGenerationError("No scan results to report")
            
            # Generate HTML content
            html_content = self._generate_html_content(
                results, target, scanner_name, include_summary, include_recommendations
            )
            
            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(output_file.absolute())
            
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate HTML report: {str(e)}",
                report_type="HTML",
                details={"output_path": output_path}
            )
    
    def _generate_html_content(
        self, 
        results: List[ScanResult], 
        target: str, 
        scanner_name: str,
        include_summary: bool,
        include_recommendations: bool
    ) -> str:
        """Generate the main HTML content."""
        scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate statistics
        stats = self._calculate_statistics(results)
        
        # Generate HTML sections
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Security Scan Report - {target}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Network Security Scan Report</h1>
            <p class="subtitle">Comprehensive Network Assessment & Security Analysis</p>
        </div>
        
        <div class="meta-info">
            <div class="meta-grid">
                <div class="meta-item">
                    <span class="meta-label">Target Assessed:</span>
                    <span class="meta-value">{target}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Scan Performed By:</span>
                    <span class="meta-value">{scanner_name}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Date & Time:</span>
                    <span class="meta-value">{scan_date}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Scan Profile:</span>
                    <span class="meta-value">{results[0].scan_profile if results else 'Unknown'}</span>
                </div>
            </div>
        </div>"""
        
        # Add summary section
        if include_summary:
            html_content += self._generate_summary_section(stats)
        
        # Add host details
        html_content += self._generate_host_details_section(results)
        
        # Add recommendations section
        if include_recommendations:
            html_content += self._generate_recommendations_section(results, stats)
        
        # Add footer
        html_content += f"""
        <div class="footer">
            <p>Generated by Enterprise Network Scanner | Report completed on {scan_date}</p>
            <p class="disclaimer">This report contains sensitive security information. Handle with appropriate care.</p>
        </div>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _calculate_statistics(self, results: List[ScanResult]) -> Dict[str, Any]:
        """Calculate scan statistics."""
        if not results:
            return {}
        
        total_hosts = len(results)
        up_hosts = len([r for r in results if r.state == 'up'])
        down_hosts = total_hosts - up_hosts
        
        total_ports = 0
        open_ports = 0
        closed_ports = 0
        filtered_ports = 0
        
        services = {}
        operating_systems = {}
        
        for result in results:
            for proto, ports in result.protocols.items():
                for port, port_info in ports.items():
                    total_ports += 1
                    state = port_info['state']
                    
                    if state == 'open':
                        open_ports += 1
                    elif state == 'closed':
                        closed_ports += 1
                    elif state == 'filtered':
                        filtered_ports += 1
                    
                    # Track services
                    service = port_info['name']
                    if service:
                        services[service] = services.get(service, 0) + 1
            
            # Track operating systems
            if result.os_matches:
                os_name = result.os_matches[0]['name']
                operating_systems[os_name] = operating_systems.get(os_name, 0) + 1
        
        return {
            'total_hosts': total_hosts,
            'up_hosts': up_hosts,
            'down_hosts': down_hosts,
            'total_ports': total_ports,
            'open_ports': open_ports,
            'closed_ports': closed_ports,
            'filtered_ports': filtered_ports,
            'services': dict(sorted(services.items(), key=lambda x: x[1], reverse=True)),
            'operating_systems': operating_systems,
            'scan_duration': sum(r.scan_duration for r in results)
        }
    
    def _generate_summary_section(self, stats: Dict[str, Any]) -> str:
        """Generate summary statistics section."""
        return f"""
        <div class="summary-section">
            <h2>Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{stats.get('total_hosts', 0)}</h3>
                    <p>Total Hosts</p>
                </div>
                <div class="stat-card up">
                    <h3>{stats.get('up_hosts', 0)}</h3>
                    <p>Hosts Up</p>
                </div>
                <div class="stat-card down">
                    <h3>{stats.get('down_hosts', 0)}</h3>
                    <p>Hosts Down</p>
                </div>
                <div class="stat-card warning">
                    <h3>{stats.get('open_ports', 0)}</h3>
                    <p>Open Ports</p>
                </div>
                <div class="stat-card">
                    <h3>{stats.get('scan_duration', 0):.1f}s</h3>
                    <p>Scan Duration</p>
                </div>
            </div>
        </div>"""
    
    def _generate_host_details_section(self, results: List[ScanResult]) -> str:
        """Generate detailed host information section."""
        html = '<div class="hosts-section"><h2>Detailed Host Analysis</h2>'
        
        for result in results:
            state_class = "up" if result.state == 'up' else "down"
            hostname_display = f" ({result.hostname})" if result.hostname else ""
            
            html += f"""
            <div class="host-card">
                <div class="host-header">
                    <h3>Host: {result.host}{hostname_display}</h3>
                    <span class="badge {state_class}">{result.state.upper()}</span>
                </div>
                
                <div class="host-info">
                    <p><strong>Scan Time:</strong> {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Scan Duration:</strong> {result.scan_duration:.2f} seconds</p>
                    <p><strong>Scan Profile:</strong> {result.scan_profile}</p>
                </div>"""
            
            # OS Information
            if result.os_matches:
                html += '<div class="os-info"><h4>Operating System Detection</h4><ul>'
                for os_match in result.os_matches[:3]:  # Show top 3 matches
                    html += f"<li><strong>{os_match['name']}</strong> (Accuracy: {os_match['accuracy']}%)</li>"
                html += '</ul></div>'
            
            # Port Information
            for proto, ports in result.protocols.items():
                if not ports:
                    continue
                
                html += f"""
                <div class="protocol-section">
                    <h4>{proto.upper()} Protocol Details</h4>
                    <div class="table-container">
                        <table class="ports-table">
                            <thead>
                                <tr>
                                    <th>Port</th>
                                    <th>State</th>
                                    <th>Service</th>
                                    <th>Version</th>
                                    <th>Extra Info</th>
                                </tr>
                            </thead>
                            <tbody>"""
                
                for port in sorted(ports.keys()):
                    port_info = ports[port]
                    state_class = port_info['state'].lower()
                    
                    html += f"""
                                <tr>
                                    <td>{port}</td>
                                    <td><span class="badge {state_class}">{port_info['state']}</span></td>
                                    <td>{port_info['name']}</td>
                                    <td>{port_info['version']}</td>
                                    <td>{port_info.get('extrainfo', '')}</td>
                                </tr>"""
                
                html += """
                            </tbody>
                        </table>
                    </div>
                </div>"""
            
            html += '</div>'  # Close host-card
        
        html += '</div>'  # Close hosts-section
        return html
    
    def _generate_recommendations_section(self, results: List[ScanResult], stats: Dict[str, Any]) -> str:
        """Generate security recommendations section."""
        recommendations = []
        
        # Analyze results and generate recommendations
        open_ports = stats.get('open_ports', 0)
        
        if open_ports > 50:
            recommendations.append({
                'priority': 'high',
                'title': 'Excessive Open Ports Detected',
                'description': f'{open_ports} open ports were detected across all hosts. Consider closing unnecessary services to reduce attack surface.'
            })
        
        # Check for dangerous services
        dangerous_services = ['telnet', 'ftp', 'rsh', 'rlogin', 'snmp']
        found_dangerous = []
        
        for result in results:
            for ports in result.protocols.values():
                for port_info in ports.values():
                    if port_info['name'] in dangerous_services and port_info['state'] == 'open':
                        found_dangerous.append(port_info['name'])
        
        if found_dangerous:
            recommendations.append({
                'priority': 'critical',
                'title': 'Insecure Services Detected',
                'description': f'The following insecure services are running: {", ".join(set(found_dangerous))}. These should be replaced with secure alternatives.'
            })
        
        # Check for default credentials
        for result in results:
            for ports in result.protocols.values():
                for port_info in ports.values():
                    if 'default' in port_info.get('extrainfo', '').lower():
                        recommendations.append({
                            'priority': 'high',
                            'title': 'Default Credentials Possible',
                            'description': f'Service on port {port_info} may be using default credentials. Immediate investigation required.'
                        })
                        break
        
        if not recommendations:
            recommendations.append({
                'priority': 'info',
                'title': 'No Critical Issues Found',
                'description': 'No immediate security concerns were detected. Continue regular security monitoring.'
            })
        
        html = '<div class="recommendations-section"><h2>Security Recommendations</h2>'
        
        for rec in recommendations:
            priority_class = rec['priority']
            html += f"""
            <div class="recommendation-card {priority_class}">
                <div class="rec-header">
                    <h4>{rec['title']}</h4>
                    <span class="priority-badge {priority_class}">{rec['priority'].upper()}</span>
                </div>
                <p>{rec['description']}</p>
            </div>"""
        
        html += '</div>'
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the report."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .meta-info {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .meta-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .meta-label {
            font-weight: bold;
            color: #666;
        }
        
        .meta-value {
            color: #333;
        }
        
        .summary-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #6c757d;
        }
        
        .stat-card.up {
            border-left-color: #28a745;
        }
        
        .stat-card.down {
            border-left-color: #dc3545;
        }
        
        .stat-card.warning {
            border-left-color: #ffc107;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 5px;
            color: #333;
        }
        
        .hosts-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .host-card {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafbfc;
        }
        
        .host-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .badge.up {
            background-color: #28a745;
            color: white;
        }
        
        .badge.down {
            background-color: #dc3545;
            color: white;
        }
        
        .badge.open {
            background-color: #28a745;
            color: white;
        }
        
        .badge.closed {
            background-color: #dc3545;
            color: white;
        }
        
        .badge.filtered {
            background-color: #ffc107;
            color: #212529;
        }
        
        .protocol-section {
            margin-top: 20px;
        }
        
        .table-container {
            overflow-x: auto;
            margin-top: 10px;
        }
        
        .ports-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .ports-table th,
        .ports-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .ports-table th {
            background-color: #495057;
            color: white;
            font-weight: 600;
        }
        
        .ports-table tr:hover {
            background-color: #f8f9fa;
        }
        
        .recommendations-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .recommendation-card {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        .recommendation-card.critical {
            border-left: 4px solid #dc3545;
            background-color: #fdf2f2;
        }
        
        .recommendation-card.high {
            border-left: 4px solid #fd7e14;
            background-color: #fff8f0;
        }
        
        .recommendation-card.info {
            border-left: 4px solid #17a2b8;
            background-color: #f0f8f9;
        }
        
        .rec-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .priority-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .priority-badge.critical {
            background-color: #dc3545;
            color: white;
        }
        
        .priority-badge.high {
            background-color: #fd7e14;
            color: white;
        }
        
        .priority-badge.info {
            background-color: #17a2b8;
            color: white;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .disclaimer {
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }
        
        h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        h3, h4 {
            color: #495057;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .meta-grid,
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .host-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .rec-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features."""
        return """
        // Interactive features for the report
        document.addEventListener('DOMContentLoaded', function() {
            // Add smooth scrolling
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
            
            // Add table sorting functionality
            const tables = document.querySelectorAll('.ports-table');
            tables.forEach(table => {
                const headers = table.querySelectorAll('th');
                headers.forEach((header, index) => {
                    header.style.cursor = 'pointer';
                    header.addEventListener('click', () => {
                        sortTable(table, index);
                    });
                });
            });
        });
        
        function sortTable(table, columnIndex) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                const aText = a.children[columnIndex].textContent.trim();
                const bText = b.children[columnIndex].textContent.trim();
                
                // Try to sort numerically if possible
                const aNum = parseInt(aText);
                const bNum = parseInt(bText);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return aNum - bNum;
                }
                
                return aText.localeCompare(bText);
            });
            
            // Clear and re-append sorted rows
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        }
        """
    
    def _get_default_template(self) -> str:
        """Get the default HTML template content."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Security Scan Report - {{target}}</title>
    <style>
        /* Default styles will be injected here */
    </style>
</head>
<body>
    <div class="container">
        <!-- Report content will be injected here -->
    </div>
</body>
</html>
        """
