"""
Example Selector for ChessTutorAI lesson generation engine.
Intelligently selects high-quality puzzle examples from the database.
"""

import random
from typing import List, Dict, Optional, Tuple
from .models import (
    PuzzleExample, LessonGenerationConfig, DifficultyLevel, 
    get_theme_info, ThemeInfo
)
from .puzzle_database import PuzzleDatabase
from .logger import get_logger

logger = get_logger(__name__)


class ExampleSelector:
    """Selects high-quality examples from puzzle database for lesson generation."""
    
    def __init__(self, puzzle_db: PuzzleDatabase):
        """Initialize the example selector."""
        self.puzzle_db = puzzle_db
        self._initialize_selection_weights()
        logger.info("Example selector initialized")
    
    def _initialize_selection_weights(self):
        """Initialize weights for example selection scoring."""
        self.selection_weights = {
            'quality_score': 0.4,
            'rating_appropriateness': 0.3,
            'theme_relevance': 0.2,
            'diversity_bonus': 0.1
        }
        
        # Rating ranges for difficulty levels
        self.difficulty_ranges = {
            DifficultyLevel.BEGINNER: {'min': 600, 'max': 1200, 'optimal': 900},
            DifficultyLevel.INTERMEDIATE: {'min': 1200, 'max': 1800, 'optimal': 1500},
            DifficultyLevel.ADVANCED: {'min': 1800, 'max': 2400, 'optimal': 2100},
            DifficultyLevel.EXPERT: {'min': 2400, 'max': 3000, 'optimal': 2700}
        }
    
    def select_examples(self, config: LessonGenerationConfig) -> List[PuzzleExample]:
        """Select best examples for a lesson based on configuration."""
        try:
            logger.info(f"Selecting {config.example_count} examples for theme '{config.theme}' "
                       f"at {config.difficulty.value} level")
            
            # Get difficulty range
            difficulty_range = self.difficulty_ranges.get(
                config.difficulty, 
                self.difficulty_ranges[DifficultyLevel.INTERMEDIATE]
            )
            
            # Use config rating range if specified, otherwise use difficulty defaults
            min_rating = config.min_rating or difficulty_range['min']
            max_rating = config.max_rating or difficulty_range['max']
            
            # Search for candidate puzzles (get more than needed for selection)
            search_limit = max(config.example_count * 3, 50)
            candidates = self._search_candidate_puzzles(
                config.theme, min_rating, max_rating, 
                config.min_quality_threshold, search_limit
            )
            
            if not candidates:
                logger.warning(f"No puzzles found for theme '{config.theme}' "
                             f"in rating range {min_rating}-{max_rating}")
                return []
            
            # Convert database results to PuzzleExample objects
            puzzle_examples = [self._db_result_to_puzzle_example(puzzle) for puzzle in candidates]
            
            # Select best examples using scoring algorithm
            if config.enable_progressive_difficulty:
                selected = self._select_progressive_examples(
                    puzzle_examples, config, difficulty_range
                )
            else:
                selected = self._select_best_examples(puzzle_examples, config)
            
            logger.info(f"Selected {len(selected)} examples with average rating "
                       f"{sum(p.rating for p in selected) / len(selected):.0f}")
            
            return selected
            
        except Exception as e:
            logger.error(f"Failed to select examples: {e}")
            return []
    
    def select_from_position(self, fen: str, theme: str, count: int, 
                           difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> List[PuzzleExample]:
        """Find examples similar to a given position."""
        try:
            logger.info(f"Finding {count} examples similar to position for theme '{theme}'")
            
            # For now, we'll search by theme and difficulty
            # In the future, we could implement position similarity matching
            config = LessonGenerationConfig(
                theme=theme,
                difficulty=difficulty,
                example_count=count,
                min_quality_threshold=0.6
            )
            
            return self.select_examples(config)
            
        except Exception as e:
            logger.error(f"Failed to select examples from position: {e}")
            return []
    
    def _search_candidate_puzzles(self, theme: str, min_rating: int, max_rating: int,
                                min_quality: float, limit: int) -> List[Dict]:
        """Search for candidate puzzles in the database."""
        try:
            # Use the puzzle database search method
            puzzles = self.puzzle_db.search_puzzles(
                theme=theme,
                min_rating=min_rating,
                max_rating=max_rating,
                min_quality=min_quality,
                limit=limit
            )
            
            logger.debug(f"Found {len(puzzles)} candidate puzzles for theme '{theme}'")
            return puzzles
            
        except Exception as e:
            logger.error(f"Failed to search candidate puzzles: {e}")
            return []
    
    def _db_result_to_puzzle_example(self, db_result: Dict) -> PuzzleExample:
        """Convert database result to PuzzleExample object."""
        try:
            # Extract solution moves from the moves field
            moves_str = db_result.get('moves', '')
            solution_moves = moves_str.split() if moves_str else []
            
            # Extract themes
            themes = db_result.get('theme_list', [])
            if isinstance(themes, str):
                # If it's still a string, try to parse it
                import json
                try:
                    themes = json.loads(themes)
                except:
                    themes = themes.split() if themes else []
            
            return PuzzleExample(
                id=db_result.get('puzzle_id', ''),
                fen=db_result.get('fen', ''),
                solution_moves=solution_moves,
                themes=themes,
                rating=db_result.get('rating', 1500),
                quality_score=db_result.get('quality_score', 0.5),
                explanation="",  # Will be generated later
                
                # Optional fields
                moves=db_result.get('moves'),
                pgn=db_result.get('pgn'),
                game_url=db_result.get('game_url'),
                popularity=db_result.get('popularity'),
                nb_plays=db_result.get('nb_plays'),
                primary_theme=db_result.get('primary_theme'),
                difficulty_level=db_result.get('difficulty_level'),
                position_hash=db_result.get('position_hash')
            )
            
        except Exception as e:
            logger.error(f"Failed to convert database result to PuzzleExample: {e}")
            # Return a minimal example to avoid breaking the flow
            return PuzzleExample(
                id=db_result.get('puzzle_id', 'unknown'),
                fen=db_result.get('fen', ''),
                solution_moves=[],
                themes=[],
                rating=1500,
                quality_score=0.5,
                explanation="Error loading puzzle data"
            )
    
    def _select_best_examples(self, candidates: List[PuzzleExample], 
                            config: LessonGenerationConfig) -> List[PuzzleExample]:
        """Select the best examples using scoring algorithm."""
        if len(candidates) <= config.example_count:
            return candidates
        
        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_selection_score(candidate, config)
            scored_candidates.append((score, candidate))
        
        # Sort by score and select top examples
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        selected = [candidate for _, candidate in scored_candidates[:config.example_count]]
        
        return selected
    
    def _select_progressive_examples(self, candidates: List[PuzzleExample], 
                                   config: LessonGenerationConfig,
                                   difficulty_range: Dict) -> List[PuzzleExample]:
        """Select examples with progressive difficulty."""
        if len(candidates) <= config.example_count:
            return sorted(candidates, key=lambda x: x.rating)
        
        # Group candidates by rating ranges
        min_rating = difficulty_range['min']
        max_rating = difficulty_range['max']
        rating_span = max_rating - min_rating
        
        # Create 3 difficulty buckets
        buckets = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        
        for candidate in candidates:
            rating_position = (candidate.rating - min_rating) / rating_span
            if rating_position < 0.33:
                buckets['easy'].append(candidate)
            elif rating_position < 0.67:
                buckets['medium'].append(candidate)
            else:
                buckets['hard'].append(candidate)
        
        # Select examples from each bucket
        examples_per_bucket = config.example_count // 3
        remainder = config.example_count % 3
        
        selected = []
        
        # Select from each bucket
        for i, (bucket_name, bucket_candidates) in enumerate(buckets.items()):
            bucket_count = examples_per_bucket + (1 if i < remainder else 0)
            
            if bucket_candidates:
                # Score and select best from this bucket
                scored = [(self._calculate_selection_score(c, config), c) for c in bucket_candidates]
                scored.sort(key=lambda x: x[0], reverse=True)
                
                bucket_selected = [candidate for _, candidate in scored[:bucket_count]]
                selected.extend(bucket_selected)
        
        # If we don't have enough examples, fill from the best remaining
        if len(selected) < config.example_count:
            remaining_candidates = [c for c in candidates if c not in selected]
            scored_remaining = [(self._calculate_selection_score(c, config), c) for c in remaining_candidates]
            scored_remaining.sort(key=lambda x: x[0], reverse=True)
            
            needed = config.example_count - len(selected)
            additional = [candidate for _, candidate in scored_remaining[:needed]]
            selected.extend(additional)
        
        # Sort final selection by rating for progressive difficulty
        selected.sort(key=lambda x: x.rating)
        
        return selected[:config.example_count]
    
    def _calculate_selection_score(self, puzzle: PuzzleExample, 
                                 config: LessonGenerationConfig) -> float:
        """Calculate selection score for a puzzle example."""
        score = 0.0
        
        # Quality score component
        quality_component = puzzle.quality_score * self.selection_weights['quality_score']
        score += quality_component
        
        # Rating appropriateness component
        difficulty_range = self.difficulty_ranges.get(
            config.difficulty, 
            self.difficulty_ranges[DifficultyLevel.INTERMEDIATE]
        )
        optimal_rating = difficulty_range['optimal']
        rating_distance = abs(puzzle.rating - optimal_rating)
        max_distance = max(
            optimal_rating - difficulty_range['min'],
            difficulty_range['max'] - optimal_rating
        )
        
        rating_appropriateness = 1.0 - (rating_distance / max_distance)
        rating_component = rating_appropriateness * self.selection_weights['rating_appropriateness']
        score += rating_component
        
        # Theme relevance component
        theme_relevance = 1.0 if config.theme in puzzle.themes else 0.5
        if puzzle.primary_theme == config.theme:
            theme_relevance = 1.0
        
        theme_component = theme_relevance * self.selection_weights['theme_relevance']
        score += theme_component
        
        # Diversity bonus (based on popularity - less popular puzzles get bonus)
        if puzzle.popularity:
            # Normalize popularity (assuming max popularity around 1000)
            normalized_popularity = min(puzzle.popularity / 1000.0, 1.0)
            diversity_bonus = (1.0 - normalized_popularity) * self.selection_weights['diversity_bonus']
            score += diversity_bonus
        
        return score
    
    def calculate_example_quality(self, puzzle: PuzzleExample) -> float:
        """Calculate overall quality score for an example."""
        # This is a comprehensive quality assessment
        quality_factors = []
        
        # Base quality score from database
        quality_factors.append(puzzle.quality_score)
        
        # Rating reliability (puzzles with more plays are more reliable)
        if puzzle.nb_plays:
            play_reliability = min(puzzle.nb_plays / 1000.0, 1.0)
            quality_factors.append(play_reliability)
        
        # Theme clarity (puzzles with fewer themes are clearer)
        theme_clarity = max(0.5, 1.0 - (len(puzzle.themes) - 1) * 0.1)
        quality_factors.append(theme_clarity)
        
        # Solution length (prefer puzzles with 1-3 moves)
        solution_length = len(puzzle.solution_moves)
        if 1 <= solution_length <= 3:
            length_score = 1.0
        elif solution_length == 4:
            length_score = 0.8
        else:
            length_score = 0.6
        quality_factors.append(length_score)
        
        # Calculate weighted average
        return sum(quality_factors) / len(quality_factors)
    
    def get_selection_statistics(self, examples: List[PuzzleExample]) -> Dict:
        """Get statistics about selected examples."""
        if not examples:
            return {}
        
        ratings = [ex.rating for ex in examples]
        qualities = [ex.quality_score for ex in examples]
        themes = [theme for ex in examples for theme in ex.themes]
        
        return {
            'count': len(examples),
            'avg_rating': sum(ratings) / len(ratings),
            'min_rating': min(ratings),
            'max_rating': max(ratings),
            'avg_quality': sum(qualities) / len(qualities),
            'min_quality': min(qualities),
            'max_quality': max(qualities),
            'unique_themes': len(set(themes)),
            'theme_distribution': {theme: themes.count(theme) for theme in set(themes)}
        }
    
    def validate_examples(self, examples: List[PuzzleExample]) -> Tuple[bool, List[str]]:
        """Validate selected examples for lesson quality."""
        issues = []
        
        if not examples:
            issues.append("No examples selected")
            return False, issues
        
        # Check for minimum quality
        low_quality = [ex for ex in examples if ex.quality_score < 0.5]
        if low_quality:
            issues.append(f"{len(low_quality)} examples have quality score < 0.5")
        
        # Check for rating distribution
        ratings = [ex.rating for ex in examples]
        rating_span = max(ratings) - min(ratings)
        if len(examples) > 3 and rating_span < 200:
            issues.append("Rating span too narrow for good progression")
        
        # Check for theme consistency
        primary_themes = [ex.primary_theme for ex in examples if ex.primary_theme]
        if len(set(primary_themes)) > 2:
            issues.append("Too many different primary themes")
        
        # Check for duplicate positions
        fens = [ex.fen for ex in examples]
        if len(set(fens)) != len(fens):
            issues.append("Duplicate positions found")
        
        return len(issues) == 0, issues