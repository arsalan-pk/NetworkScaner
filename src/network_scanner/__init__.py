"""
Network Scanner - Enterprise Network Security Assessment Tool

A professional-grade network scanning and security assessment application
with modular architecture and enterprise features.
"""

__version__ = "1.0.0"
__author__ = "Enterprise Security Team"
__email__ = "security@enterprise.com"

from .core.scanner import NetworkScanner
from .core.exceptions import NetworkScannerError
from .config.settings import Settings

__all__ = [
    "NetworkScanner",
    "NetworkScannerError", 
    "Settings"
]
