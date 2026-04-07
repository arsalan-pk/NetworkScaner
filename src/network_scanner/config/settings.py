"""
Configuration management for Network Scanner.

This module provides centralized configuration management with support for
different environments and scan profiles.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from ..core.exceptions import ConfigurationError


class Settings:
    """
    Centralized configuration manager for the Network Scanner application.
    
    Handles loading and accessing configuration from YAML files with
    environment-specific overrides.
    """
    
    def __init__(self, config_dir: Optional[str] = None) -> None:
        """
        Initialize settings manager.
        
        Args:
            config_dir: Path to configuration directory. If None, uses default.
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / "config"
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML files."""
        try:
            # Load base configuration
            base_config_path = self.config_dir / "base_config.yaml"
            if base_config_path.exists():
                with open(base_config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            
            # Load environment-specific configuration
            env = os.getenv('NETWORK_SCANNER_ENV', 'development')
            env_config_path = self.config_dir / f"{env}_config.yaml"
            if env_config_path.exists():
                with open(env_config_path, 'r', encoding='utf-8') as f:
                    env_config = yaml.safe_load(f) or {}
                    self._merge_config(self._config, env_config)
            
            # Set defaults if not in config
            self._set_defaults()
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {str(e)}",
                details={"config_dir": str(self.config_dir)}
            )
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        defaults = {
            "app": {
                "name": "Network Scanner",
                "version": "1.0.0",
                "debug": False
            },
            "ui": {
                "theme": "dark",
                "window_width": 850,
                "window_height": 700,
                "bg_color": "#2b2b2b",
                "fg_color": "#e0e0e0",
                "accent_color": "#4a90e2"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "network_scanner.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "scanning": {
                "timeout": 300,
                "max_threads": 10,
                "default_profile": "intense_scan"
            }
        }
        
        self._merge_config(self._config, defaults)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key using dot notation.
        
        Args:
            key: Configuration key (e.g., 'ui.theme')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key using dot notation.
        
        Args:
            key: Configuration key (e.g., 'ui.theme')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.get('app.name', 'Network Scanner')
    
    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.get('app.version', '1.0.0')
    
    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return self.get('app.debug', False)


class ScanProfiles:
    """
    Scan profile definitions and management.
    
    Provides predefined scan configurations that can be easily
    extended and customized.
    """
    
    PROFILES = {
        "intense_scan": {
            "name": "Intense Scan (OS, Services, Default Scripts)",
            "args": "-A -T4",
            "description": "Comprehensive scan with OS detection, version detection, script scanning, and traceroute"
        },
        "quick_scan": {
            "name": "Quick Scan",
            "args": "-T4 -F",
            "description": "Fast scan of fewer ports"
        },
        "ping_scan": {
            "name": "Ping Scan (Host Discovery)",
            "args": "-sn",
            "description": "Ping scan only - discovers if hosts are online"
        },
        "syn_scan": {
            "name": "SYN Scan (Stealth)",
            "args": "-sS -T4",
            "description": "TCP SYN scan - stealthy and fast"
        },
        "udp_scan": {
            "name": "UDP Scan",
            "args": "-sU -T4",
            "description": "UDP port scan"
        },
        "version_scan": {
            "name": "Version Detection",
            "args": "-sV -T4",
            "description": "Detect service versions on open ports"
        },
        "os_scan": {
            "name": "OS Detection",
            "args": "-O -T4",
            "description": "Detect operating system"
        },
        "aggressive_scan": {
            "name": "Aggressive Scan",
            "args": "-A -T4 -v",
            "description": "Intense scan with verbose output"
        }
    }
    
    @classmethod
    def get_profile(cls, profile_name: str) -> Optional[Dict[str, str]]:
        """
        Get scan profile by name.
        
        Args:
            profile_name: Name of the scan profile
            
        Returns:
            Profile dictionary or None if not found
        """
        return cls.PROFILES.get(profile_name)
    
    @classmethod
    def get_all_profiles(cls) -> Dict[str, Dict[str, str]]:
        """Get all available scan profiles."""
        return cls.PROFILES.copy()
    
    @classmethod
    def get_profile_names(cls) -> list:
        """Get list of all profile names."""
        return list(cls.PROFILES.keys())
    
    @classmethod
    def add_profile(cls, name: str, profile: Dict[str, str]) -> None:
        """
        Add a new scan profile.
        
        Args:
            name: Profile name
            profile: Profile configuration
        """
        cls.PROFILES[name] = profile
