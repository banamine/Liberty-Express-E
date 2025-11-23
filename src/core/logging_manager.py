"""
Structured Logging Module - Step 3 of refactoring
JSON-formatted logging for production systems
"""

import logging
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Format logs as structured JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_obj["user_id"] = record.user_id
        if hasattr(record, 'operation_id'):
            log_obj["operation_id"] = record.operation_id
        
        return json.dumps(log_obj)


class LoggingManager:
    """Configure structured logging across the application"""
    
    # Log levels
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @staticmethod
    def setup_logging(log_file: Optional[str] = None,
                     level: str = "INFO",
                     json_format: bool = True,
                     console: bool = True) -> logging.Logger:
        """
        Setup structured logging for the application
        
        Args:
            log_file: Path to log file (if None, console only)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            json_format: Use JSON formatting
            console: Also log to console
        
        Returns:
            Configured logger instance
        """
        # Create logs directory
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(LoggingManager.LEVELS.get(level, logging.INFO))
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatter
        if json_format:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(LoggingManager.LEVELS.get(level, logging.INFO))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(LoggingManager.LEVELS.get(level, logging.INFO))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        return root_logger
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger for a specific module"""
        return logging.getLogger(name)
    
    @staticmethod
    def log_operation(logger: logging.Logger, operation_id: str, 
                     action: str, details: Optional[dict] = None) -> None:
        """Log an operation with structured fields"""
        log_dict = {
            "action": action,
            "operation_id": operation_id
        }
        if details:
            log_dict.update(details)
        
        logger.info(f"Operation: {action}", extra={"operation_id": operation_id})
    
    @staticmethod
    def log_error_with_context(logger: logging.Logger, error: Exception,
                              context: Optional[dict] = None) -> None:
        """Log an error with context information"""
        context_str = json.dumps(context) if context else ""
        logger.error(f"{str(error)} | Context: {context_str}", exc_info=True)


# Global setup
def initialize_logging(config: Optional[dict] = None) -> None:
    """Initialize logging for the entire application"""
    log_file = config.get('logging', {}).get('file_path', 'logs/scheduleflow.log') if config else 'logs/scheduleflow.log'
    level = config.get('app', {}).get('log_level', 'INFO') if config else 'INFO'
    json_format = config.get('logging', {}).get('format', 'json') == 'json' if config else True
    
    LoggingManager.setup_logging(
        log_file=log_file,
        level=level,
        json_format=json_format,
        console=True
    )
