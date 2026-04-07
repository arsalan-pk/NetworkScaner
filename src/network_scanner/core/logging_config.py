"""
Logging configuration for Network Scanner.

This module provides centralized logging configuration with support
for different log levels, file rotation, and structured logging.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional
from pathlib import Path
from .exceptions import ConfigurationError


class LoggerSetup:
    """
    Centralized logging configuration manager.
    
    Provides professional logging setup with file rotation,
    console output, and proper formatting.
    """
    
    @staticmethod
    def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        max_size: str = "10MB",
        backup_count: int = 5,
        console_output: bool = True,
        format_string: Optional[str] = None
    ) -> None:
        """
        Setup logging configuration for the application.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            max_size: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            console_output: Whether to output logs to console
            format_string: Custom log format string
            
        Raises:
            ConfigurationError: If logging setup fails
        """
        try:
            # Convert log level string to logging constant
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            
            # Default format
            if not format_string:
                format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            
            formatter = logging.Formatter(format_string)
            
            # Get root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(numeric_level)
            
            # Clear existing handlers
            root_logger.handlers.clear()
            
            # Console handler
            if console_output:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(numeric_level)
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)
            
            # File handler with rotation
            if log_file:
                # Create log directory if it doesn't exist
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Parse max_size
                max_bytes = LoggerSetup._parse_size(max_size)
                
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(numeric_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            
            # Set specific logger levels
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('requests').setLevel(logging.WARNING)
            
            # Log initialization
            logger = logging.getLogger(__name__)
            logger.info(f"Logging initialized at level: {log_level}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to setup logging: {str(e)}",
                details={
                    "log_level": log_level,
                    "log_file": log_file,
                    "max_size": max_size
                }
            )
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """
        Parse size string to bytes.
        
        Args:
            size_str: Size string (e.g., "10MB", "1GB")
            
        Returns:
            Size in bytes
        """
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            # Assume bytes if no unit specified
            return int(size_str)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


# Convenience function for easy logger access
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
