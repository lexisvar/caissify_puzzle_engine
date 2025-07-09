"""Database for storing and querying Lichess puzzles."""

import sqlite3
import json
import hashlib
from typing import List, Dict, Optional, Iterator, Tuple
from dataclasses import dataclass
from .logger import get_logger

@dataclass
class PuzzleData:
    """Simple data class for puzzle information."""
    puzzle_id: str
    fen: str
    moves: str
    rating: int
    themes: List[str]
    game_url: Optional[str] = None
    rating_deviation: Optional[int] = None
    popularity: Optional[int] = None
    nb_plays: Optional[int] = None
    opening_tags: Optional[str] = None
    pgn: Optional[str] = None
    difficulty_level: Optional[str] = None
    primary_theme: Optional[str] = None
    quality_score: Optional[float] = None
    position_hash: Optional[str] = None

logger = get_logger(__name__)

class PuzzleDatabase:
    """Database for puzzle storage and querying."""
    
    def __init__(self, db_path: str = "data/lichess_puzzles.db"):
        self.db_path = db_path
        self._create_puzzle_tables()
        logger.info(f"Puzzle database initialized: {db_path}")
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def _create_puzzle_tables(self):
        """Create puzzle-specific tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
        
        # Main puzzle table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lichess_puzzles (
                puzzle_id TEXT PRIMARY KEY,
                fen TEXT NOT NULL,
                moves TEXT NOT NULL,
                rating INTEGER NOT NULL,
                rating_deviation INTEGER DEFAULT 0,
                popularity INTEGER DEFAULT 0,
                nb_plays INTEGER DEFAULT 0,
                themes TEXT NOT NULL,
                game_url TEXT,
                opening_tags TEXT,
                
                -- Processed fields
                pgn TEXT,
                solution_moves INTEGER,
                difficulty_level TEXT,
                primary_theme TEXT,
                theme_list TEXT,
                quality_score REAL,
                
                -- Integration fields
                position_hash TEXT,
                is_imported BOOLEAN DEFAULT TRUE,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Puzzle themes table (normalized for efficient querying)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS puzzle_themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puzzle_id TEXT,
                theme TEXT,
                is_primary BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (puzzle_id) REFERENCES lichess_puzzles(puzzle_id)
            )
        ''')
        
        # Puzzle statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS puzzle_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_puzzles INTEGER DEFAULT 0,
                last_import_date TIMESTAMP,
                import_batch_size INTEGER DEFAULT 0,
                avg_quality_score REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for efficient querying
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_puzzle_rating ON lichess_puzzles(rating)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_difficulty ON lichess_puzzles(difficulty_level)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_primary_theme ON lichess_puzzles(primary_theme)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_quality ON lichess_puzzles(quality_score)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_position_hash ON lichess_puzzles(position_hash)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_themes_theme ON puzzle_themes(theme)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_themes_puzzle_id ON puzzle_themes(puzzle_id)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_rating_quality ON lichess_puzzles(rating, quality_score)',
            'CREATE INDEX IF NOT EXISTS idx_puzzle_theme_difficulty ON lichess_puzzles(primary_theme, difficulty_level)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("Puzzle database tables and indexes created successfully")
    
    def import_puzzles(self, puzzles: Iterator[PuzzleData], batch_size: int = 1000) -> int:
        """Import puzzles into database with batch processing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
        batch = []
        theme_batch = []
        total_imported = 0
        
        logger.info("Starting puzzle import...")
        
        try:
            for puzzle in puzzles:
                puzzle_tuple = self._puzzle_to_tuple(puzzle)
                batch.append(puzzle_tuple)
                
                # Prepare theme entries
                for theme in puzzle.themes:
                    theme_batch.append((
                        puzzle.puzzle_id,
                        theme,
                        theme == puzzle.primary_theme
                    ))
                
                if len(batch) >= batch_size:
                    imported = self._insert_puzzle_batch(cursor, batch, theme_batch)
                    total_imported += imported
                    batch = []
                    theme_batch = []
                    
                    if total_imported % 10000 == 0:
                        logger.info(f"Imported {total_imported} puzzles...")
            
            # Insert remaining puzzles
            if batch:
                imported = self._insert_puzzle_batch(cursor, batch, theme_batch)
                total_imported += imported
            
            # Update statistics
            self._update_puzzle_stats(cursor, total_imported)
            
            conn.commit()
            logger.info(f"Successfully imported {total_imported} puzzles")
            return total_imported
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to import puzzles: {e}")
            raise
    
    def _puzzle_to_tuple(self, puzzle: PuzzleData) -> tuple:
        """Convert PuzzleData to database tuple."""
        return (
            puzzle.puzzle_id,
            puzzle.fen,
            puzzle.moves,
            puzzle.rating,
            puzzle.rating_deviation or 0,
            puzzle.popularity or 0,
            puzzle.nb_plays or 0,
            ' '.join(puzzle.themes),
            puzzle.game_url,
            puzzle.opening_tags,
            puzzle.pgn,
            len(puzzle.moves.split()) if puzzle.moves else 0,
            puzzle.difficulty_level,
            puzzle.primary_theme,
            json.dumps(puzzle.themes),
            puzzle.quality_score,
            puzzle.position_hash
        )
    
    def _insert_puzzle_batch(self, cursor, puzzle_batch: List[tuple], theme_batch: List[tuple]) -> int:
        """Insert batch of puzzles and themes."""
        try:
            # Insert puzzles
            cursor.executemany('''
                INSERT OR REPLACE INTO lichess_puzzles (
                    puzzle_id, fen, moves, rating, rating_deviation,
                    popularity, nb_plays, themes, game_url, opening_tags,
                    pgn, solution_moves, difficulty_level, primary_theme,
                    theme_list, quality_score, position_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', puzzle_batch)
            
            # Insert themes
            cursor.executemany('''
                INSERT OR REPLACE INTO puzzle_themes (puzzle_id, theme, is_primary)
                VALUES (?, ?, ?)
            ''', theme_batch)
            
            return len(puzzle_batch)
            
        except Exception as e:
            logger.error(f"Failed to insert puzzle batch: {e}")
            raise
    
    def _update_puzzle_stats(self, cursor, imported_count: int):
        """Update puzzle statistics."""
        cursor.execute('''
            INSERT OR REPLACE INTO puzzle_stats (
                id, total_puzzles, last_import_date, import_batch_size,
                avg_quality_score, updated_at
            ) VALUES (
                1,
                (SELECT COUNT(*) FROM lichess_puzzles),
                CURRENT_TIMESTAMP,
                ?,
                (SELECT AVG(quality_score) FROM lichess_puzzles),
                CURRENT_TIMESTAMP
            )
        ''', (imported_count,))
    
    def search_puzzles(self, 
                      theme: Optional[str] = None,
                      difficulty: Optional[str] = None,
                      min_rating: Optional[int] = None,
                      max_rating: Optional[int] = None,
                      min_quality: float = 0.5,
                      limit: int = 100,
                      offset: int = 0) -> List[Dict]:
        """Search puzzles with comprehensive filters."""
        
        query = """
            SELECT p.* FROM lichess_puzzles p
            WHERE p.quality_score >= ?
        """
        params = [min_quality]
        
        # Theme filter
        if theme:
            query += " AND (p.primary_theme = ? OR p.themes LIKE ?)"
            params.extend([theme, f"%{theme}%"])
        
        # Difficulty filter
        if difficulty:
            query += " AND p.difficulty_level = ?"
            params.append(difficulty)
        
        # Rating filters
        if min_rating:
            query += " AND p.rating >= ?"
            params.append(min_rating)
        
        if max_rating:
            query += " AND p.rating <= ?"
            params.append(max_rating)
        
        # Order by quality and rating
        query += " ORDER BY p.quality_score DESC, p.rating DESC"
        
        # Pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse theme_list JSON
        for result in results:
            if result.get('theme_list'):
                try:
                    result['theme_list'] = json.loads(result['theme_list'])
                except json.JSONDecodeError:
                    result['theme_list'] = []
        
        return results
    
    def get_puzzle_by_id(self, puzzle_id: str) -> Optional[Dict]:
        """Get a specific puzzle by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lichess_puzzles WHERE puzzle_id = ?", (puzzle_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        # Parse theme_list JSON
        if result.get('theme_list'):
            try:
                result['theme_list'] = json.loads(result['theme_list'])
            except json.JSONDecodeError:
                result['theme_list'] = []
        
        return result
    
    def get_puzzles_by_theme(self, theme: str, limit: int = 50) -> List[Dict]:
        """Get puzzles for a specific theme."""
        return self.search_puzzles(theme=theme, limit=limit)
    
    def get_puzzles_by_difficulty(self, difficulty: str, limit: int = 50) -> List[Dict]:
        """Get puzzles for a specific difficulty level."""
        return self.search_puzzles(difficulty=difficulty, limit=limit)
    
    def get_random_puzzles(self, count: int = 10, min_quality: float = 0.6) -> List[Dict]:
        """Get random high-quality puzzles."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lichess_puzzles
                WHERE quality_score >= ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (min_quality, count))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse theme_list JSON
        for result in results:
            if result.get('theme_list'):
                try:
                    result['theme_list'] = json.loads(result['theme_list'])
                except json.JSONDecodeError:
                    result['theme_list'] = []
        
        return results
    
    def get_puzzle_statistics(self) -> Dict:
        """Get comprehensive puzzle database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
        
        stats = {}
        
        # Total puzzles
        cursor.execute("SELECT COUNT(*) FROM lichess_puzzles")
        stats['total_puzzles'] = cursor.fetchone()[0]
        
        # By difficulty
        cursor.execute("""
            SELECT difficulty_level, COUNT(*) 
            FROM lichess_puzzles 
            GROUP BY difficulty_level
            ORDER BY COUNT(*) DESC
        """)
        stats['by_difficulty'] = dict(cursor.fetchall())
        
        # Top themes
        cursor.execute("""
            SELECT primary_theme, COUNT(*) 
            FROM lichess_puzzles 
            GROUP BY primary_theme 
            ORDER BY COUNT(*) DESC 
            LIMIT 20
        """)
        stats['top_themes'] = dict(cursor.fetchall())
        
        # Rating distribution
        cursor.execute("""
            SELECT 
                MIN(rating) as min_rating,
                MAX(rating) as max_rating,
                AVG(rating) as avg_rating,
                AVG(quality_score) as avg_quality
            FROM lichess_puzzles
        """)
        row = cursor.fetchone()
        stats['rating_stats'] = {
            'min_rating': row[0],
            'max_rating': row[1],
            'avg_rating': round(row[2], 1) if row[2] else 0,
            'avg_quality': round(row[3], 3) if row[3] else 0
        }
        
        # Quality distribution
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN quality_score >= 0.8 THEN 1 END) as high_quality,
                COUNT(CASE WHEN quality_score >= 0.6 AND quality_score < 0.8 THEN 1 END) as medium_quality,
                COUNT(CASE WHEN quality_score < 0.6 THEN 1 END) as low_quality
            FROM lichess_puzzles
        """)
        row = cursor.fetchone()
        stats['quality_distribution'] = {
            'high_quality': row[0],
            'medium_quality': row[1],
            'low_quality': row[2]
        }
        
        # Import statistics
        cursor.execute("SELECT * FROM puzzle_stats WHERE id = 1")
        import_stats = cursor.fetchone()
        if import_stats:
            stats['import_info'] = {
                'last_import_date': import_stats[2],
                'last_batch_size': import_stats[3]
            }
        
        return stats
    
    def get_theme_statistics(self) -> Dict[str, int]:
        """Get statistics for all themes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT theme, COUNT(*)
                FROM puzzle_themes
                GROUP BY theme
                ORDER BY COUNT(*) DESC
            """)
            return dict(cursor.fetchall())
    
    def find_similar_puzzles(self, puzzle_id: str, limit: int = 10) -> List[Dict]:
        """Find puzzles similar to the given puzzle."""
        # Get the reference puzzle
        reference = self.get_puzzle_by_id(puzzle_id)
        if not reference:
            return []
        
        # Find puzzles with similar rating and themes
        rating_range = 100
        return self.search_puzzles(
            theme=reference['primary_theme'],
            min_rating=reference['rating'] - rating_range,
            max_rating=reference['rating'] + rating_range,
            min_quality=reference['quality_score'] - 0.1,
            limit=limit + 1  # +1 to exclude the reference puzzle
        )
    
    def get_progressive_puzzles(self, 
                              theme: str, 
                              start_rating: int = 1000, 
                              count_per_level: int = 5) -> Dict[str, List[Dict]]:
        """Get puzzles in progressive difficulty for a theme."""
        levels = {
            'easy': (start_rating, start_rating + 300),
            'medium': (start_rating + 200, start_rating + 600),
            'hard': (start_rating + 500, start_rating + 900)
        }
        
        result = {}
        for level, (min_rating, max_rating) in levels.items():
            puzzles = self.search_puzzles(
                theme=theme,
                min_rating=min_rating,
                max_rating=max_rating,
                min_quality=0.6,
                limit=count_per_level
            )
            result[level] = puzzles
        
        return result
    
    def cleanup_duplicate_puzzles(self) -> int:
        """Remove duplicate puzzles based on position hash."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find duplicates
            cursor.execute("""
                DELETE FROM lichess_puzzles
                WHERE puzzle_id NOT IN (
                    SELECT MIN(puzzle_id)
                    FROM lichess_puzzles
                    GROUP BY position_hash
                )
            """)
            
            deleted_count = cursor.rowcount
            
            # Clean up orphaned themes
            cursor.execute("""
                DELETE FROM puzzle_themes
                WHERE puzzle_id NOT IN (
                    SELECT puzzle_id FROM lichess_puzzles
                )
            """)
            
            conn.commit()
            logger.info(f"Cleaned up {deleted_count} duplicate puzzles")
            return deleted_count
    
    def get_puzzle_count(self) -> int:
        """Get total number of puzzles in database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM lichess_puzzles")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get puzzle count: {e}")
            return 0
    
    def export_puzzles_to_csv(self, output_path: str, limit: Optional[int] = None):
        """Export puzzles to CSV format."""
        import csv
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM lichess_puzzles ORDER BY quality_score DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                columns = [desc[0] for desc in cursor.description]
                writer.writerow(columns)
                
                # Write data
                for row in cursor.fetchall():
                    writer.writerow(row)
            
            logger.info(f"Exported puzzles to {output_path}")

# Note: Create PuzzleDatabase instances as needed in your code
# Example: puzzle_db = PuzzleDatabase()