"""
Custom exceptions for Network Scanner.

This module defines the exception hierarchy used throughout the application
for better error handling and debugging.
"""

from typing import Optional, Any


class NetworkScannerError(Exception):
    """
    Base exception class for all Network Scanner errors.
    
    Attributes:
        message (str): Human-readable error description
        error_code (str): Machine-readable error code
        details (Optional[dict]): Additional error context
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERIC_ERROR",
        details: Optional[dict] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ConfigurationError(NetworkScannerError):
    """
    Raised when there are issues with application configuration.
    
    Examples: Missing config files, invalid settings, etc.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details
        )


class ValidationError(NetworkScannerError):
    """
    Raised when user input validation fails.
    
    Examples: Invalid IP addresses, malformed domain names, etc.
    """
    
    def __init__(self, message: str, field: str = "", details: Optional[dict] = None) -> None:
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ScanError(NetworkScannerError):
    """
    Raised when network scanning operations fail.
    
    Examples: Nmap not found, scan timeouts, permission issues, etc.
    """
    
    def __init__(self, message: str, target: str = "", details: Optional[dict] = None) -> None:
        details = details or {}
        if target:
            details["target"] = target
        super().__init__(
            message=message,
            error_code="SCAN_ERROR",
            details=details
        )


class ReportGenerationError(NetworkScannerError):
    """
    Raised when report generation fails.
    
    Examples: File write errors, template issues, data formatting problems, etc.
    """
    
    def __init__(self, message: str, report_type: str = "", details: Optional[dict] = None) -> None:
        details = details or {}
        if report_type:
            details["report_type"] = report_type
        super().__init__(
            message=message,
            error_code="REPORT_ERROR",
            details=details
        )


class UIError(NetworkScannerError):
    """
    Raised when UI-related operations fail.
    
    Examples: Widget creation errors, theme issues, etc.
    """
    
    def __init__(self, message: str, component: str = "", details: Optional[dict] = None) -> None:
        details = details or {}
        if component:
            details["component"] = component
        super().__init__(
            message=message,
            error_code="UI_ERROR",
            details=details
        )
