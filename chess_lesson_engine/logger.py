"""Logging configuration for chess_lesson_engine."""

import logging
import logging.handlers
import os
from typing import Optional
from .config import config

class ChessLessonLogger:
    """Centralized logging for the chess lesson engine."""
    
    _loggers = {}
    _configured = False
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance with proper configuration."""
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Create and configure a logger."""
        if not cls._configured:
            cls._configure_logging()
            cls._configured = True
        
        logger = logging.getLogger(name)
        return logger
    
    @classmethod
    def _configure_logging(cls):
        """Configure the root logging settings."""
        log_level = getattr(logging, config.get('logging.level', 'INFO').upper())
        log_format = config.get('logging.format', 
                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = config.get('logging.file', 'chess_lesson_engine.log')
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file:
            try:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=10*1024*1024, backupCount=5
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except (OSError, IOError) as e:
                print(f"Warning: Could not create log file {log_file}: {e}")

# Convenience function for getting loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return ChessLessonLogger.get_logger(name)