"""
Core network scanning engine for Network Scanner.
"""

import threading
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass
from .exceptions import ScanError, ValidationError
from .validator import InputValidator
from ..config.settings import ScanProfiles


@dataclass
class ScanResult:
    """
    Data class representing scan results for a single host.
    """
    host: str
    hostname: str
    state: str
    protocols: Dict[str, Dict[int, Dict[str, str]]]
    os_matches: List[Dict[str, str]]
    scan_time: datetime
    scan_duration: float
    scan_profile: str


@dataclass
class ScanRequest:
    """
    Data class representing a scan request.
    """
    target: str
    scanner_name: str
    profile: str
    custom_args: Optional[str] = None
    ports: Optional[str] = None
    timeout: int = 300


class NetworkScanner:
    """
    Network scanning engine.
    """
    
    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Initialize the network scanner.
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.progress_callback = progress_callback
        self._scanner = None
        self._is_scanning = False
        self._scan_thread: Optional[threading.Thread] = None
        self._results: List[ScanResult] = []
        
        self._initialize_nmap()
    
    def _initialize_nmap(self) -> None:
        """Initialize nmap scanner with proper error handling."""
        try:
            import nmap
            self._scanner = nmap.PortScanner()
            self._log("Nmap scanner initialized successfully")
        except ImportError:
            raise ScanError(
                "nmap Python package is not installed. Install with: pip install python-nmap",
                details={"error": "python-nmap package missing"}
            )
        except Exception as e:
            if "nmap" in str(e).lower() or "not found" in str(e).lower():
                raise ScanError(
                    "Nmap is not installed or not in PATH. Install from: https://nmap.org/download.html",
                    details={"error": str(e)}
                )
            else:
                raise ScanError(
                    f"Failed to initialize nmap scanner: {str(e)}",
                    details={"error": str(e)}
                )
    
    def _log(self, message: str) -> None:
        """Log message using callback if available."""
        if self.progress_callback:
            self.progress_callback(message)
    
    def validate_scan_request(self, request: ScanRequest) -> None:
        """
        Validate scan request parameters.
        
        Args:
            request: Scan request to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate target
        is_valid, error_msg = InputValidator.validate_target(request.target)
        if not is_valid:
            raise ValidationError(f"Invalid target: {error_msg}", field="target")
        
        # Validate scanner name
        is_valid, error_msg = InputValidator.validate_scanner_name(request.scanner_name)
        if not is_valid:
            raise ValidationError(f"Invalid scanner name: {error_msg}", field="scanner_name")
        
        # Validate scan profile
        if request.profile not in ScanProfiles.get_profile_names():
            raise ValidationError(
                f"Invalid scan profile: {request.profile}",
                field="profile",
                details={"available_profiles": ScanProfiles.get_profile_names()}
            )
        
        # Validate custom ports if provided
        if request.ports:
            is_valid, error_msg, ports = InputValidator.validate_port_range(request.ports)
            if not is_valid:
                raise ValidationError(f"Invalid port range: {error_msg}", field="ports")
    
    def scan(self, request: ScanRequest) -> List[ScanResult]:
        """
        Perform network scan with the given request.
        
        Args:
            request: Scan request containing all parameters
            
        Returns:
            List of scan results
            
        Raises:
            ScanError: If scan fails
            ValidationError: If request validation fails
        """
        if self._is_scanning:
            raise ScanError("Another scan is already in progress")
        
        # Validate request
        self.validate_scan_request(request)
        
        # Start scan in thread
        self._is_scanning = True
        self._results = []
        
        try:
            self._scan_thread = threading.Thread(
                target=self._execute_scan,
                args=(request,),
                daemon=True
            )
            self._scan_thread.start()
            
            # Wait for scan completion
            self._scan_thread.join(timeout=request.timeout)
            
            if self._scan_thread.is_alive():
                raise ScanError(
                    f"Scan timeout after {request.timeout} seconds",
                    target=request.target
                )
            
            return self._results
            
        finally:
            self._is_scanning = False
    
    def scan_async(self, request: ScanRequest, 
                   completion_callback: Optional[Callable[[List[ScanResult]], None]] = None,
                   error_callback: Optional[Callable[[ScanError], None]] = None) -> None:
        """
        Perform network scan asynchronously.
        
        Args:
            request: Scan request containing all parameters
            completion_callback: Callback called when scan completes successfully
            error_callback: Callback called when scan fails
        """
        if self._is_scanning:
            if error_callback:
                error_callback(ScanError("Another scan is already in progress"))
            return
        
        # Validate request
        try:
            self.validate_scan_request(request)
        except ValidationError as e:
            if error_callback:
                error_callback(ScanError(f"Validation failed: {e.message}"))
            return
        
        # Start async scan
        self._is_scanning = True
        self._results = []
        
        def scan_wrapper():
            try:
                self._execute_scan(request)
                if completion_callback:
                    completion_callback(self._results)
            except Exception as e:
                if error_callback:
                    error_callback(ScanError(f"Scan failed: {str(e)}", target=request.target))
            finally:
                self._is_scanning = False
        
        self._scan_thread = threading.Thread(target=scan_wrapper, daemon=True)
        self._scan_thread.start()
    
    def _execute_scan(self, request: ScanRequest) -> None:
        """
        Execute the actual scan operation.
        
        Args:
            request: Scan request containing all parameters
        """
        if not self._scanner:
            raise ScanError("Scanner not initialized")
        
        start_time = time.time()
        
        try:
            # Get scan profile
            profile = ScanProfiles.get_profile(request.profile)
            if not profile:
                raise ScanError(f"Unknown scan profile: {request.profile}")
            
            # Build nmap arguments
            args = profile["args"]
            if request.custom_args:
                args += f" {request.custom_args}"
            
            if request.ports:
                args += f" -p {request.ports}"
            
            self._log(f"[*] Starting scan on target: {request.target}")
            self._log(f"[*] Profile: {profile['name']}")
            self._log(f"[*] Arguments: {args}")
            self._log(f"[*] Initiated by: {request.scanner_name}")
            self._log(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._log("-" * 60)
            
            # Execute scan
            self._scanner.scan(hosts=request.target, arguments=args)
            
            # Process results
            scan_duration = time.time() - start_time
            
            if not self._scanner.all_hosts():
                self._log("[!] Target seems down or blocking probe packets.")
            else:
                for host in self._scanner.all_hosts():
                    result = self._process_host_result(
                        host, 
                        self._scanner[host], 
                        scan_duration, 
                        request.profile
                    )
                    self._results.append(result)
            
            self._log(f"[*] Scan completed in {scan_duration:.2f} seconds")
            
        except Exception as e:
            self._log(f"[!] Scan error: {str(e)}")
            raise ScanError(
                f"Scan failed: {str(e)}",
                target=request.target,
                details={"profile": request.profile, "duration": time.time() - start_time}
            )
    
    def _process_host_result(self, host: str, host_data: Any, 
                           scan_duration: float, profile: str) -> ScanResult:
        """
        Process scan results for a single host.
        
        Args:
            host: Host IP address
            host_data: Nmap host data
            scan_duration: Total scan duration
            profile: Scan profile used
            
        Returns:
            ScanResult object
        """
        # Extract hostname
        hostname = host_data.hostname() or ""
        
        # Extract state
        state = host_data.state()
        
        # Extract protocols and ports
        protocols = {}
        for proto in host_data.all_protocols():
            protocols[proto] = {}
            ports = host_data[proto].keys()
            for port in sorted(ports):
                port_info = host_data[proto][port]
                protocols[proto][port] = {
                    'state': port_info['state'],
                    'name': port_info['name'],
                    'version': port_info['version'],
                    'extrainfo': port_info.get('extrainfo', '')
                }
        
        # Extract OS matches
        os_matches = []
        if 'osmatch' in host_data and host_data['osmatch']:
            for os_match in host_data['osmatch']:
                os_matches.append({
                    'name': os_match['name'],
                    'accuracy': os_match['accuracy'],
                    'line': os_match['line']
                })
        
        # Create result object
        result = ScanResult(
            host=host,
            hostname=hostname,
            state=state,
            protocols=protocols,
            os_matches=os_matches,
            scan_time=datetime.now(),
            scan_duration=scan_duration,
            scan_profile=profile
        )
        
        # Log host results
        self._log(f"\n[+] Host: {host} ({hostname})")
        self._log(f"[+] State: {state}")
        
        if os_matches:
            self._log(f"[+] Detected OS: {os_matches[0]['name']} (accuracy: {os_matches[0]['accuracy']}%)")
        else:
            self._log("[-] OS Detection Note: Run with 'sudo' for accurate OS detection.")
        
        for proto in protocols:
            self._log(f"========== Protocol: {proto.upper()} ==========")
            for port, port_info in protocols[proto].items():
                info = (f"Port: {port}\tState: {port_info['state']}\t"
                       f"Service: {port_info['name']}\t"
                       f"Version: {port_info['version']} {port_info['extrainfo']}").strip()
                self._log(info)
        
        return result
    
    def stop_scan(self) -> None:
        """Stop the current scan operation."""
        if self._is_scanning and self._scan_thread:
            self._is_scanning = False
            self._log("[!] Scan stopped by user")
    
    def get_scan_results(self) -> List[ScanResult]:
        """Get the results from the last scan."""
        return self._results.copy()
    
    def is_scanning(self) -> bool:
        """Check if a scan is currently in progress."""
        return self._is_scanning
    
    def get_nmap_version(self) -> str:
        """Get the nmap version information."""
        if not self._scanner:
            return "Not initialized"
        
        try:
            return self._scanner.nmap_version()
        except Exception:
            return "Unknown"
    
    def get_scan_stats(self) -> Dict[str, Any]:
        """Get scanning statistics."""
        if not self._results:
            return {}
        
        total_hosts = len(self._results)
        up_hosts = len([r for r in self._results if r.state == 'up'])
        total_ports = sum(len(ports) for result in self._results for ports in result.protocols.values())
        open_ports = sum(
            len([p for p in ports.values() if p['state'] == 'open'])
            for result in self._results for ports in result.protocols.values()
        )
        
        return {
            'total_hosts': total_hosts,
            'up_hosts': up_hosts,
            'down_hosts': total_hosts - up_hosts,
            'total_ports_scanned': total_ports,
            'open_ports': open_ports,
            'scan_duration': sum(r.scan_duration for r in self._results),
            'scan_profile': self._results[0].scan_profile if self._results else None
        }
