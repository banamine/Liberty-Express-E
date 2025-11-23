"""
Configuration Management Module - Step 8 of refactoring
Handles YAML configuration files with fallback to defaults
"""

import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration container"""
    raw_config: Dict[str, Any]
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'api.host')"""
        keys = key_path.split('.')
        value = self.raw_config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key_path: str, value: Any) -> None:
        """Set config value using dot notation"""
        keys = key_path.split('.')
        config = self.raw_config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value


class ConfigManager:
    """Load and manage configuration files"""
    
    # Default configuration
    DEFAULTS = {
        "app": {
            "name": "ScheduleFlow",
            "version": "2.1.0",
            "environment": "development",
            "debug": False,
            "log_level": "INFO"
        },
        "storage": {
            "schedules_dir": "schedules",
            "backups_dir": "backups",
            "stripped_media_dir": "stripped_media",
            "logs_dir": "logs",
            "cache_dir": ".cache",
            "backup_enabled": True,
            "backup_retention_days": 30,
            "versioning_enabled": True
        },
        "scheduling": {
            "cooldown_hours": 48,
            "timezone": "UTC",
            "max_events_batch": 1000,
            "auto_fill": True
        },
        "media_stripper": {
            "enabled": True,
            "respect_robots_txt": True,
            "use_selenium": True,
            "rate_limit_requests_per_second": 2
        },
        "validation": {
            "validate_on_import": True,
            "detect_overlaps": True,
            "detect_duplicates": True
        },
        "threading": {
            "enabled": True,
            "max_workers": 4,
            "catch_thread_exceptions": True,
            "retry_failed_tasks": True,
            "max_retries": 3
        },
        "api": {
            "host": "0.0.0.0",
            "port": 3000,
            "rate_limit_enabled": True,
            "rate_limit_requests_per_minute": 100
        },
        "logging": {
            "format": "json",
            "console": True,
            "file": True,
            "file_path": "logs/scheduleflow.log"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager
        
        Args:
            config_path: Path to YAML config file. If None, uses defaults + environment.
        """
        self.config_path = Path(config_path) if config_path else Path("config/scheduleflow.yaml")
        self.config = self._load_config()
        self.raw_config = self.config.raw_config  # Expose raw_config directly
    
    def _load_config(self) -> Config:
        """Load configuration from file with fallback to defaults"""
        config_data = self.DEFAULTS.copy()
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                    self._deep_merge(config_data, file_config)
                    logger.info(f"Loaded configuration from {self.config_path}")
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML config: {e}")
                logger.warning("Using default configuration")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                logger.warning("Using default configuration")
        else:
            logger.info(f"Config file not found at {self.config_path}, using defaults")
        
        return Config(config_data)
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> None:
        """Recursively merge override into base"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key_path, default)
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value"""
        self.config.set(key_path, value)
    
    def save(self, output_path: Optional[str] = None) -> bool:
        """Save current configuration to YAML file"""
        path = Path(output_path) if output_path else self.config_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                yaml.dump(self.config.raw_config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate required configuration values"""
        required_keys = [
            "app.name",
            "storage.schedules_dir",
            "scheduling.cooldown_hours",
            "api.host",
            "api.port"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                logger.error(f"Required config key missing: {key}")
                return False
        
        return True


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get or create global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
