"""Caching system for chess position evaluations."""

import hashlib
import json
import os
import time
from typing import Dict, Any, Optional, Tuple
from .config import config
from .logger import get_logger

logger = get_logger(__name__)

class PositionCache:
    """Cache for Stockfish position evaluations to improve performance."""
    
    def __init__(self, cache_file: str = "position_cache.json", max_age_hours: int = 24):
        self.cache_file = cache_file
        self.max_age_seconds = max_age_hours * 3600
        self._cache = self._load_cache()
        self._hits = 0
        self._misses = 0
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Clean expired entries
                    current_time = time.time()
                    cleaned_cache = {}
                    for key, value in cache_data.items():
                        if current_time - value.get('timestamp', 0) < self.max_age_seconds:
                            cleaned_cache[key] = value
                    logger.info(f"Loaded {len(cleaned_cache)} cached positions, "
                              f"removed {len(cache_data) - len(cleaned_cache)} expired entries")
                    return cleaned_cache
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load cache file {self.cache_file}: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except (IOError, NameError) as e:
            # NameError can occur during interpreter shutdown when 'open' is not available
            if hasattr(logger, 'warning'):
                logger.warning(f"Could not save cache file {self.cache_file}: {e}")
    
    def _generate_key(self, fen: str, time_limit: float, min_depth: int, multipv: int) -> str:
        """Generate a unique key for the position and evaluation parameters."""
        key_data = f"{fen}|{time_limit}|{min_depth}|{multipv}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, fen: str, time_limit: float, min_depth: int, multipv: int) -> Optional[Tuple[Optional[int], Optional[int], Dict[str, Any]]]:
        """Get cached evaluation result."""
        key = self._generate_key(fen, time_limit, min_depth, multipv)
        
        if key in self._cache:
            entry = self._cache[key]
            # Check if entry is still valid
            if time.time() - entry['timestamp'] < self.max_age_seconds:
                self._hits += 1
                logger.debug(f"Cache hit for position {fen[:20]}...")
                return entry['score'], entry['mate'], entry['info']
            else:
                # Remove expired entry
                del self._cache[key]
        
        self._misses += 1
        logger.debug(f"Cache miss for position {fen[:20]}...")
        return None
    
    def set(self, fen: str, time_limit: float, min_depth: int, multipv: int, 
            score: Optional[int], mate: Optional[int], info: Dict[str, Any]) -> None:
        """Cache evaluation result."""
        key = self._generate_key(fen, time_limit, min_depth, multipv)
        
        # Create a serializable copy of info
        serializable_info = {}
        for k, v in info.items():
            if k == 'pv':  # Principal variation moves
                serializable_info[k] = [str(move) for move in v] if v else []
            elif k == 'score':
                # Skip the score object as we store it separately
                continue
            else:
                try:
                    json.dumps(v)  # Test if serializable
                    serializable_info[k] = v
                except (TypeError, ValueError):
                    serializable_info[k] = str(v)
        
        self._cache[key] = {
            'fen': fen,
            'score': score,
            'mate': mate,
            'info': serializable_info,
            'timestamp': time.time()
        }
        
        logger.debug(f"Cached evaluation for position {fen[:20]}...")
        
        # Periodically save cache
        if len(self._cache) % 10 == 0:
            self._save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_positions': len(self._cache),
            'cache_file_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries."""
        current_time = time.time()
        initial_count = len(self._cache)
        
        expired_keys = [
            key for key, value in self._cache.items()
            if current_time - value.get('timestamp', 0) >= self.max_age_seconds
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        removed_count = initial_count - len(self._cache)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} expired cache entries")
            self._save_cache()
        
        return removed_count
    
    def __del__(self):
        """Save cache when object is destroyed."""
        try:
            # Check if we have cache data to save
            if hasattr(self, '_cache') and self._cache:
                self._save_cache()
        except (NameError, AttributeError, TypeError):
            # Silently ignore errors during interpreter shutdown
            # NameError: when built-ins like 'open' are not available
            # AttributeError: when attributes are None during shutdown
            # TypeError: when objects are in inconsistent state during shutdown
            pass

# Global cache instance
position_cache = PositionCache()