"""
Input validation and sanitization for Network Scanner.

This module provides comprehensive validation for user inputs including
IP addresses, domain names, and scan parameters.
"""

import re
import socket
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse
from .exceptions import ValidationError


class InputValidator:
    """
    Comprehensive input validation and sanitization.
    
    Provides methods to validate various types of network-related inputs
    with detailed error messages for user feedback.
    """
    
    # Regex patterns for validation
    IPV4_PATTERN = re.compile(
        r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    IPV6_PATTERN = re.compile(
        r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,7}:|'
        r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
        r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
        r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
        r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
        r':((:[0-9a-fA-F]{1,4}){1,7}|:)|'
        r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
        r'::(ffff(:0{1,4}){0,1}:){0,1}'
        r'((25[0-5]|(2[0-4]|1{0,1}[0-9])[0-9])\.){3,3}'
        r'(25[0-5]|(2[0-4]|1{0,1}[0-9])[0-9])|'
        r'([0-9a-fA-F]{1,4}:){1,4}:'
        r'((25[0-5]|(2[0-4]|1{0,1}[0-9])[0-9])\.){3,3}'
        r'(25[0-5]|(2[0-4]|1{0,1}[0-9])[0-9]))$'
    )
    
    DOMAIN_PATTERN = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
        r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    HOSTNAME_PATTERN = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
    )
    
    @classmethod
    def validate_target(cls, target: str) -> Tuple[bool, str]:
        """
        Validate network target (IP, domain, hostname, or CIDR).
        
        Args:
            target: Target string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not target or not target.strip():
            return False, "Target cannot be empty"
        
        target = target.strip()
        
        # Check for CIDR notation
        if '/' in target:
            return cls._validate_cidr(target)
        
        # Check for IP ranges
        if '-' in target:
            return cls._validate_ip_range(target)
        
        # Check for single IP
        if cls.is_valid_ipv4(target) or cls.is_valid_ipv6(target):
            return True, ""
        
        # Check for domain name
        if cls.is_valid_domain(target):
            return True, ""
        
        # Check for hostname
        if cls.is_valid_hostname(target):
            return True, ""
        
        return False, f"Invalid target format: {target}"
    
    @classmethod
    def _validate_cidr(cls, cidr: str) -> Tuple[bool, str]:
        """Validate CIDR notation."""
        try:
            if '/' not in cidr:
                return False, "Invalid CIDR format"
            
            ip, prefix = cidr.split('/', 1)
            
            # Validate IP part
            if not (cls.is_valid_ipv4(ip) or cls.is_valid_ipv6(ip)):
                return False, f"Invalid IP address in CIDR: {ip}"
            
            # Validate prefix
            try:
                prefix_num = int(prefix)
                if cls.is_valid_ipv4(ip):
                    if not 0 <= prefix_num <= 32:
                        return False, f"IPv4 prefix must be between 0-32, got {prefix_num}"
                else:
                    if not 0 <= prefix_num <= 128:
                        return False, f"IPv6 prefix must be between 0-128, got {prefix_num}"
            except ValueError:
                return False, f"Invalid prefix number: {prefix}"
            
            return True, ""
            
        except Exception:
            return False, f"Invalid CIDR format: {cidr}"
    
    @classmethod
    def _validate_ip_range(cls, ip_range: str) -> Tuple[bool, str]:
        """Validate IP range (e.g., 192.168.1.1-192.168.1.100)."""
        try:
            if '-' not in ip_range:
                return False, "Invalid IP range format"
            
            start_ip, end_ip = ip_range.split('-', 1)
            start_ip = start_ip.strip()
            end_ip = end_ip.strip()
            
            if not (cls.is_valid_ipv4(start_ip) and cls.is_valid_ipv4(end_ip)):
                return False, "Both start and end IPs must be valid IPv4 addresses"
            
            # Convert to integers for comparison
            start_int = cls._ipv4_to_int(start_ip)
            end_int = cls._ipv4_to_int(end_ip)
            
            if start_int >= end_int:
                return False, "Start IP must be less than end IP"
            
            return True, ""
            
        except Exception:
            return False, f"Invalid IP range format: {ip_range}"
    
    @classmethod
    def is_valid_ipv4(cls, ip: str) -> bool:
        """Check if string is a valid IPv4 address."""
        return bool(cls.IPV4_PATTERN.match(ip))
    
    @classmethod
    def is_valid_ipv6(cls, ip: str) -> bool:
        """Check if string is a valid IPv6 address."""
        return bool(cls.IPV6_PATTERN.match(ip))
    
    @classmethod
    def is_valid_domain(cls, domain: str) -> bool:
        """Check if string is a valid domain name."""
        if len(domain) > 253:
            return False
        
        if not cls.DOMAIN_PATTERN.match(domain):
            return False
        
        # Additional checks
        if domain.startswith('.') or domain.endswith('.'):
            return False
        
        if '..' in domain:
            return False
        
        return True
    
    @classmethod
    def is_valid_hostname(cls, hostname: str) -> bool:
        """Check if string is a valid hostname."""
        if len(hostname) > 63:
            return False
        
        return bool(cls.HOSTNAME_PATTERN.match(hostname))
    
    @classmethod
    def validate_scanner_name(cls, name: str) -> Tuple[bool, str]:
        """
        Validate scanner name input.
        
        Args:
            name: Scanner name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Scanner name cannot be empty"
        
        name = name.strip()
        
        if len(name) > 100:
            return False, "Scanner name cannot exceed 100 characters"
        
        # Check for potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '/', '\\', ';', '|']
        if any(char in name for char in dangerous_chars):
            return False, "Scanner name contains invalid characters"
        
        return True, ""
    
    @classmethod
    def validate_port_range(cls, port_str: str) -> Tuple[bool, str, List[int]]:
        """
        Validate and parse port range string.
        
        Args:
            port_str: Port range string (e.g., "80", "80-443", "22,80,443")
            
        Returns:
            Tuple of (is_valid, error_message, list_of_ports)
        """
        if not port_str or not port_str.strip():
            return False, "Port range cannot be empty", []
        
        ports = []
        parts = port_str.split(',')
        
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Port range
                try:
                    start, end = part.split('-', 1)
                    start_port = int(start.strip())
                    end_port = int(end.strip())
                    
                    if not (1 <= start_port <= 65535):
                        return False, f"Port {start_port} is out of valid range (1-65535)", []
                    
                    if not (1 <= end_port <= 65535):
                        return False, f"Port {end_port} is out of valid range (1-65535)", []
                    
                    if start_port >= end_port:
                        return False, f"Invalid port range: {start_port}-{end_port}", []
                    
                    ports.extend(range(start_port, end_port + 1))
                    
                except ValueError:
                    return False, f"Invalid port range format: {part}", []
            else:
                # Single port
                try:
                    port = int(part)
                    if not (1 <= port <= 65535):
                        return False, f"Port {port} is out of valid range (1-65535)", []
                    ports.append(port)
                except ValueError:
                    return False, f"Invalid port number: {part}", []
        
        # Remove duplicates and sort
        ports = sorted(list(set(ports)))
        
        # Check if too many ports
        if len(ports) > 10000:
            return False, "Port range too large (maximum 10,000 ports)", []
        
        return True, "", ports
    
    @classmethod
    def _ipv4_to_int(cls, ip: str) -> int:
        """Convert IPv4 address to integer for comparison."""
        octets = ip.split('.')
        return (int(octets[0]) << 24) + (int(octets[1]) << 16) + (int(octets[2]) << 8) + int(octets[3])
    
    @classmethod
    def sanitize_input(cls, input_str: str) -> str:
        """
        Sanitize user input by removing potentially dangerous characters.
        
        Args:
            input_str: Input string to sanitize
            
        Returns:
            Sanitized string
        """
        if not input_str:
            return ""
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in '\n\t')
        
        # Remove potentially dangerous characters for certain contexts
        dangerous_chars = ['\0', '\r']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
