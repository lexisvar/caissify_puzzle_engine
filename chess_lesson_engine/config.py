"""Configuration management for chess_lesson_engine."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the chess lesson engine."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "stockfish": {
                "path": self._find_stockfish_path(),
                "time_limit": 3.0,
                "min_depth": 25,
                "multipv": 3
            },
            "openai": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 512,
                "max_retries": 5
            },
            "lesson_generation": {
                "max_attempts": 5,
                "fork_evaluation_threshold": 300
            },
            "difficulty": {
                "mate_in_1_threshold": 500,
                "winning_advantage_threshold": 1000,
                "intermediate_threshold": 500,
                "advanced_threshold": 200
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "chess_lesson_engine.log"
            },
            "lichess": {
                "min_delay": 3.0,
                "max_delay": 60.0,
                "timeout": 30,
                "max_games_per_request": 300,
                "default_filters": {
                    "min_rating": 1600,
                    "max_rating": 2800,
                    "min_moves": 20,
                    "max_moves": 150,
                    "rated": True,
                    "analyzed": True
                }
            },
            "tactical_detection": {
                "evaluation_threshold": 100,
                "min_drop": 150,
                "max_drop": 2000,
                "context_moves": 3,
                "quality_threshold": 0.5,
                "max_moments_per_game": 10
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    return self._merge_configs(default_config, user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                print("Using default configuration.")
        
        return default_config
    
    def _find_stockfish_path(self) -> str:
        """Try to find Stockfish binary in common locations."""
        possible_paths = [
            "/opt/homebrew/bin/stockfish",  # macOS Homebrew
            "/usr/local/bin/stockfish",     # Linux/macOS manual install
            "/usr/bin/stockfish",           # Linux package manager
            "stockfish",                    # In PATH
            "stockfish.exe"                 # Windows
        ]
        
        for path in possible_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
            # Check if it's in PATH
            import shutil
            if shutil.which(path):
                return path
        
        # Default fallback
        return "/opt/homebrew/bin/stockfish"
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'stockfish.path')."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def create_sample_config(self, filename: str = "config.sample.json") -> None:
        """Create a sample configuration file."""
        with open(filename, 'w') as f:
            json.dump(self._config, f, indent=2)
        print(f"Sample configuration created: {filename}")

# Global config instance
config = Config()