"""Lichess API client for downloading chess games and tactical analysis."""

import time
import requests
import json
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
import chess.pgn
import io
from .logger import get_logger
from .config import config

logger = get_logger(__name__)

@dataclass
class GameFilters:
    """Filters for searching Lichess games."""
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    time_control: Optional[str] = None  # 'classical', 'rapid', 'blitz'
    opening: Optional[str] = None
    result: Optional[str] = None  # '1-0', '0-1', '1/2-1/2'
    min_moves: int = 20
    max_moves: int = 150
    rated: bool = True
    analyzed: bool = True  # Only games with computer analysis

@dataclass
class GameData:
    """Represents a chess game from Lichess."""
    game_id: str
    pgn: str
    white_player: str
    black_player: str
    white_rating: int
    black_rating: int
    time_control: str
    opening: str
    result: str
    date: datetime
    url: str
    has_analysis: bool = False
    analysis_data: Optional[Dict] = None

class RateLimiter:
    """Rate limiter for Lichess API requests."""
    
    def __init__(self, min_delay: float = 3.0, max_delay: float = 60.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.current_delay = min_delay
        self.consecutive_errors = 0
    
    def wait(self):
        """Wait appropriate time before next request."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.current_delay:
            sleep_time = self.current_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def on_success(self):
        """Called after successful request."""
        self.consecutive_errors = 0
        # Gradually reduce delay on success
        self.current_delay = max(self.min_delay, self.current_delay * 0.9)
    
    def on_error(self, status_code: int = None):
        """Called after failed request."""
        self.consecutive_errors += 1
        
        if status_code == 429:  # Too Many Requests
            self.current_delay = min(self.max_delay, self.current_delay * 2)
            logger.warning(f"Rate limited by Lichess. Increasing delay to {self.current_delay:.2f}s")
        else:
            # Exponential backoff for other errors
            self.current_delay = min(self.max_delay, self.current_delay * 1.5)
        
        logger.debug(f"Request failed. New delay: {self.current_delay:.2f}s")

class LichessClient:
    """Client for interacting with the Lichess API."""
    
    def __init__(self):
        self.base_url = "https://lichess.org/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChessTutorAI/1.0 (Educational Chess Analysis)',
            'Accept': 'application/json'
        })
        self.rate_limiter = RateLimiter(
            min_delay=config.get('lichess.min_delay', 3.0),
            max_delay=config.get('lichess.max_delay', 60.0)
        )
        
        # Configure session timeouts
        self.timeout = config.get('lichess.timeout', 30)
        
        logger.info("Lichess API client initialized")
    
    def _make_request(self, endpoint: str, params: Dict = None, stream: bool = False) -> requests.Response:
        """Make a rate-limited request to Lichess API."""
        self.rate_limiter.wait()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(
                url, 
                params=params or {}, 
                timeout=self.timeout,
                stream=stream
            )
            
            if response.status_code == 200:
                self.rate_limiter.on_success()
                return response
            else:
                self.rate_limiter.on_error(response.status_code)
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self.rate_limiter.on_error()
            logger.error(f"Request to {url} failed: {e}")
            raise
    
    def get_game(self, game_id: str, include_analysis: bool = True, include_moves: bool = True) -> GameData:
        """Download a single game by ID."""
        params = {
            'moves': 'true' if include_moves else 'false',
            'tags': 'true',
            'clocks': 'true',
            'evals': 'true' if include_analysis else 'false',
            'opening': 'true'
        }
        
        try:
            response = self._make_request(f"game/{game_id}", params)
            pgn_text = response.text
            
            # Parse PGN
            pgn_io = io.StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)
            
            if not game:
                raise ValueError(f"Could not parse PGN for game {game_id}")
            
            # Extract game metadata
            headers = game.headers
            
            game_data = GameData(
                game_id=game_id,
                pgn=pgn_text,
                white_player=headers.get('White', 'Unknown'),
                black_player=headers.get('Black', 'Unknown'),
                white_rating=int(headers.get('WhiteElo', 0)),
                black_rating=int(headers.get('BlackElo', 0)),
                time_control=headers.get('TimeControl', 'Unknown'),
                opening=headers.get('Opening', 'Unknown'),
                result=headers.get('Result', '*'),
                date=self._parse_date(headers.get('Date', '')),
                url=f"https://lichess.org/{game_id}",
                has_analysis=include_analysis and 'eval' in pgn_text
            )
            
            logger.debug(f"Successfully downloaded game {game_id}")
            return game_data
            
        except Exception as e:
            logger.error(f"Failed to download game {game_id}: {e}")
            raise
    
    def search_games(self, username: str, filters: GameFilters, max_games: int = 100) -> List[str]:
        """Search for games by a specific user with filters."""
        params = {
            'max': min(max_games, 300),  # Lichess API limit
            'rated': 'true' if filters.rated else 'false',
            'moves': 'false',  # We only want game IDs for now
            'tags': 'true',
            'opening': 'true'
        }
        
        # Add rating filters
        if filters.min_rating:
            params['ratingMin'] = filters.min_rating
        if filters.max_rating:
            params['ratingMax'] = filters.max_rating
        
        # Add time control filter
        if filters.time_control:
            perf_map = {
                'bullet': 'bullet',
                'blitz': 'blitz', 
                'rapid': 'rapid',
                'classical': 'classical'
            }
            if filters.time_control in perf_map:
                params['perfType'] = perf_map[filters.time_control]
        
        try:
            response = self._make_request(f"games/user/{username}", params, stream=True)
            
            game_ids = []
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    try:
                        game_data = json.loads(line)
                        game_id = game_data.get('id')
                        if game_id and self._passes_filters(game_data, filters):
                            game_ids.append(game_id)
                            
                            if len(game_ids) >= max_games:
                                break
                                
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"Found {len(game_ids)} games for user {username}")
            return game_ids
            
        except Exception as e:
            logger.error(f"Failed to search games for user {username}: {e}")
            raise
    
    def get_top_games(self, filters: GameFilters, max_games: int = 100) -> List[str]:
        """Get top-rated games from Lichess database."""
        # This would require implementing a more sophisticated search
        # For now, we'll use a known list of strong players
        strong_players = [
            'DrNykterstein',  # Magnus Carlsen
            'FairChess_on_YouTube',  # Hikaru Nakamura
            'GMWSO',  # Wesley So
            'GMHikaru',  # Hikaru (another account)
            'DanielNaroditsky',
            'GMBenjaminFinegold'
        ]
        
        all_game_ids = []
        games_per_player = max_games // len(strong_players) + 1
        
        for player in strong_players:
            try:
                game_ids = self.search_games(player, filters, games_per_player)
                all_game_ids.extend(game_ids)
                
                if len(all_game_ids) >= max_games:
                    break
                    
            except Exception as e:
                logger.warning(f"Failed to get games for {player}: {e}")
                continue
        
        return all_game_ids[:max_games]
    
    def batch_download_games(self, game_ids: List[str], include_analysis: bool = True) -> Iterator[GameData]:
        """Download multiple games with rate limiting."""
        total_games = len(game_ids)
        logger.info(f"Starting batch download of {total_games} games")
        
        for i, game_id in enumerate(game_ids, 1):
            try:
                game_data = self.get_game(game_id, include_analysis)
                yield game_data
                
                if i % 10 == 0:
                    logger.info(f"Downloaded {i}/{total_games} games ({i/total_games*100:.1f}%)")
                    
            except Exception as e:
                logger.error(f"Failed to download game {game_id}: {e}")
                continue
    
    def _passes_filters(self, game_data: Dict, filters: GameFilters) -> bool:
        """Check if a game passes the specified filters."""
        # Check move count
        moves = game_data.get('moves', '')
        move_count = len(moves.split()) if moves else 0
        
        if move_count < filters.min_moves or move_count > filters.max_moves:
            return False
        
        # Check if game is rated (if required)
        if filters.rated and not game_data.get('rated', False):
            return False
        
        # Check if game has analysis (if required)
        if filters.analyzed and not game_data.get('analysis', False):
            return False
        
        # Check opening
        if filters.opening:
            opening = game_data.get('opening', {}).get('name', '')
            if filters.opening.lower() not in opening.lower():
                return False
        
        # Check result
        if filters.result:
            if game_data.get('winner') != filters.result:
                return False
        
        return True
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from PGN header."""
        try:
            return datetime.strptime(date_str, '%Y.%m.%d')
        except ValueError:
            return datetime.now()
    
    def get_client_stats(self) -> Dict[str, Any]:
        """Get statistics about the client usage."""
        return {
            'current_delay': self.rate_limiter.current_delay,
            'consecutive_errors': self.rate_limiter.consecutive_errors,
            'min_delay': self.rate_limiter.min_delay,
            'max_delay': self.rate_limiter.max_delay
        }

# Global client instance
lichess_client = LichessClient()