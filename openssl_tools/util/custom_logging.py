#!/usr/bin/env python3
"""
OpenSSL Tools Custom Logging
Based on ngapy-dev patterns for logging configuration
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openssl_tools.core.config import ConfigLoaderManager


def setup_logging_from_config(config_path: Optional[Path] = None) -> None:
    """Setup logging from configuration files following ngapy-dev patterns"""
    try:
        # Load configuration
        config_loader = ConfigLoaderManager()
        config = config_loader.get_configuration()
        
        # Get logging configuration
        if hasattr(config, 'logging'):
            logging_config = config.logging
        else:
            # Default logging configuration
            logging_config = {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'handlers': [
                    {'type': 'console'},
                    {'type': 'file', 'filename': 'openssl_tools.log', 'max_bytes': 10485760, 'backup_count': 5}
                ]
            }
        
        # Configure logging level
        level = getattr(logging, logging_config.get('level', 'INFO').upper())
        
        # Configure format
        log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(log_format)
        
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Setup handlers
        handlers = logging_config.get('handlers', [])
        for handler_config in handlers:
            handler_type = handler_config.get('type', 'console')
            
            if handler_type == 'console':
                handler = logging.StreamHandler(sys.stdout)
            elif handler_type == 'file':
                filename = handler_config.get('filename', 'openssl_tools.log')
                max_bytes = handler_config.get('max_bytes', 10485760)  # 10MB
                backup_count = handler_config.get('backup_count', 5)
                
                # Ensure log directory exists
                log_path = Path(filename)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                handler = logging.handlers.RotatingFileHandler(
                    filename, maxBytes=max_bytes, backupCount=backup_count
                )
            else:
                continue
            
            handler.setFormatter(formatter)
            handler.setLevel(level)
            root_logger.addHandler(handler)
        
        # Set root logger level
        root_logger.setLevel(level)
        
        # Log successful setup
        logger = logging.getLogger(__name__)
        logger.info("Logging configured successfully")
        
    except Exception as e:
        # Fallback to basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('openssl_tools.log')
            ]
        )
        logging.getLogger(__name__).warning(f"Failed to load logging configuration: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with proper naming"""
    return logging.getLogger(f'openssl_tools.{name}')


def setup_file_logging(log_file: Path, level: str = 'INFO', 
                      max_bytes: int = 10485760, backup_count: int = 5) -> logging.Logger:
    """Setup file logging for specific module"""
    logger = logging.getLogger(f'openssl_tools.{log_file.stem}')
    
    # Remove existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    
    # Create new file handler
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    
    # Set formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Set level
    handler.setLevel(getattr(logging, level.upper()))
    logger.setLevel(getattr(logging, level.upper()))
    
    # Add handler
    logger.addHandler(handler)
    
    return logger


def log_command_execution(command: str, return_code: int, output: str, 
                         error: str = "", logger: Optional[logging.Logger] = None) -> None:
    """Log command execution details"""
    if logger is None:
        logger = get_logger('command_execution')
    
    logger.info(f"Command: {command}")
    logger.info(f"Return code: {return_code}")
    
    if output:
        logger.debug(f"Output: {output}")
    
    if error:
        logger.error(f"Error: {error}")


def log_performance_metrics(operation: str, duration: float, 
                           additional_info: Optional[Dict[str, Any]] = None,
                           logger: Optional[logging.Logger] = None) -> None:
    """Log performance metrics"""
    if logger is None:
        logger = get_logger('performance')
    
    logger.info(f"Performance - {operation}: {duration:.2f}s")
    
    if additional_info:
        for key, value in additional_info.items():
            logger.debug(f"  {key}: {value}")


def log_security_event(event_type: str, details: str, 
                      severity: str = 'INFO',
                      logger: Optional[logging.Logger] = None) -> None:
    """Log security-related events"""
    if logger is None:
        logger = get_logger('security')
    
    level = getattr(logging, severity.upper(), logging.INFO)
    logger.log(level, f"Security Event - {event_type}: {details}")


def log_package_operation(operation: str, package_name: str, version: str = "",
                         success: bool = True, details: str = "",
                         logger: Optional[logging.Logger] = None) -> None:
    """Log package operations"""
    if logger is None:
        logger = get_logger('package_operations')
    
    status = "SUCCESS" if success else "FAILED"
    package_info = f"{package_name}/{version}" if version else package_name
    
    logger.info(f"Package {operation} - {package_info}: {status}")
    
    if details:
        logger.debug(f"  Details: {details}")


def log_build_event(event_type: str, details: str, 
                   build_id: Optional[str] = None,
                   logger: Optional[logging.Logger] = None) -> None:
    """Log build-related events"""
    if logger is None:
        logger = get_logger('build')
    
    build_info = f" [{build_id}]" if build_id else ""
    logger.info(f"Build Event{build_info} - {event_type}: {details}")


def log_artifactory_operation(operation: str, repository: str, 
                             success: bool = True, details: str = "",
                             logger: Optional[logging.Logger] = None) -> None:
    """Log Artifactory operations"""
    if logger is None:
        logger = get_logger('artifactory')
    
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Artifactory {operation} - {repository}: {status}")
    
    if details:
        logger.debug(f"  Details: {details}")


def log_configuration_change(config_file: str, changes: Dict[str, Any],
                           logger: Optional[logging.Logger] = None) -> None:
    """Log configuration changes"""
    if logger is None:
        logger = get_logger('configuration')
    
    logger.info(f"Configuration changed - {config_file}")
    
    for key, value in changes.items():
        logger.debug(f"  {key}: {value}")


def log_error_with_context(error: Exception, context: str = "",
                          logger: Optional[logging.Logger] = None) -> None:
    """Log error with additional context"""
    if logger is None:
        logger = get_logger('errors')
    
    context_info = f" - {context}" if context else ""
    logger.error(f"Error{context_info}: {type(error).__name__}: {error}")
    
    # Log stack trace at debug level
    import traceback
    logger.debug(f"Stack trace:\n{traceback.format_exc()}")


def log_memory_usage(operation: str, logger: Optional[logging.Logger] = None) -> None:
    """Log memory usage for operations"""
    if logger is None:
        logger = get_logger('memory')
    
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        logger.debug(f"Memory usage for {operation}: {memory_mb:.2f} MB")
    except ImportError:
        logger.debug(f"Memory usage logging not available (psutil not installed)")


def log_disk_usage(path: Path, logger: Optional[logging.Logger] = None) -> None:
    """Log disk usage for path"""
    if logger is None:
        logger = get_logger('disk_usage')
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        
        logger.info(f"Disk usage for {path}: {used_gb:.2f}GB used / {total_gb:.2f}GB total ({free_gb:.2f}GB free)")
    except Exception as e:
        logger.warning(f"Failed to get disk usage for {path}: {e}")


def setup_console_logging(level: str = 'INFO') -> None:
    """Setup console-only logging for simple scripts"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def setup_quiet_logging() -> None:
    """Setup quiet logging (errors only)"""
    logging.basicConfig(
        level=logging.ERROR,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def setup_debug_logging() -> None:
    """Setup debug logging with detailed output"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('debug.log')
        ]
    )


# Convenience functions for common logging patterns
def log_startup(module_name: str, version: str = "", logger: Optional[logging.Logger] = None) -> None:
    """Log module startup"""
    if logger is None:
        logger = get_logger('startup')
    
    version_info = f" v{version}" if version else ""
    logger.info(f"Starting {module_name}{version_info}")


def log_shutdown(module_name: str, logger: Optional[logging.Logger] = None) -> None:
    """Log module shutdown"""
    if logger is None:
        logger = get_logger('shutdown')
    
    logger.info(f"Shutting down {module_name}")


def log_feature_usage(feature: str, user: str = "", logger: Optional[logging.Logger] = None) -> None:
    """Log feature usage for analytics"""
    if logger is None:
        logger = get_logger('feature_usage')
    
    user_info = f" by {user}" if user else ""
    logger.info(f"Feature used: {feature}{user_info}")


def log_api_call(endpoint: str, method: str, status_code: int, 
                duration: float, logger: Optional[logging.Logger] = None) -> None:
    """Log API calls"""
    if logger is None:
        logger = get_logger('api_calls')
    
    logger.info(f"API {method} {endpoint} - {status_code} ({duration:.2f}s)")


def log_cache_operation(operation: str, key: str, hit: bool = True, 
                      logger: Optional[logging.Logger] = None) -> None:
    """Log cache operations"""
    if logger is None:
        logger = get_logger('cache')
    
    status = "HIT" if hit else "MISS"
    logger.debug(f"Cache {operation} - {key}: {status}")


def log_validation_result(validator: str, target: str, valid: bool, 
                         details: str = "", logger: Optional[logging.Logger] = None) -> None:
    """Log validation results"""
    if logger is None:
        logger = get_logger('validation')
    
    status = "VALID" if valid else "INVALID"
    logger.info(f"Validation {validator} - {target}: {status}")
    
    if details:
        logger.debug(f"  Details: {details}")