"""
ChessTutorAI Lesson Generation Engine
Main interface for generating chess lessons with AI-powered content.
"""

from typing import List, Dict, Optional, Union
from pathlib import Path
import json

from .models import (
    ChessLesson, PuzzleExample, LessonGenerationConfig, 
    DifficultyLevel, get_theme_info, TACTICAL_THEMES
)
from .example_selector import ExampleSelector
from .content_generator import ContentGenerator
from .lesson_builder import LessonBuilder
from .puzzle_database import PuzzleDatabase
from .logger import get_logger

logger = get_logger(__name__)


class ChessLessonEngine:
    """
    Main chess lesson generation engine.
    
    This is the primary interface for generating chess lessons. It orchestrates
    the example selection, content generation, and lesson assembly processes.
    """
    
    def __init__(self, database_path: Optional[str] = None, ai_provider: str = "openai"):
        """
        Initialize the chess lesson engine.
        
        Args:
            database_path: Path to the puzzle database (optional)
            ai_provider: AI provider to use for content generation
        """
        try:
            # Initialize database
            if database_path:
                self.database = PuzzleDatabase(database_path)
            else:
                # Use the default database path from PuzzleDatabase
                self.database = PuzzleDatabase()
            
            # Initialize components
            self.example_selector = ExampleSelector(self.database)
            self.content_generator = ContentGenerator(ai_provider)
            self.lesson_builder = LessonBuilder(self.example_selector, self.content_generator)
            
            # Engine state
            self._initialized = True
            self._stats = {
                'lessons_generated': 0,
                'examples_used': 0,
                'themes_covered': set()
            }
            
            logger.info(f"Chess lesson engine initialized with {ai_provider} provider")
            
        except Exception as e:
            logger.error(f"Failed to initialize chess lesson engine: {e}")
            self._initialized = False
            raise
    
    def generate_lesson(self, theme: str, difficulty: Union[str, DifficultyLevel], 
                       num_examples: int = 5, include_analysis: bool = True,
                       progressive_difficulty: bool = True) -> ChessLesson:
        """
        Generate a complete chess lesson for a specific theme.
        
        Args:
            theme: Tactical theme (e.g., 'pin', 'fork', 'skewer')
            difficulty: Difficulty level ('beginner', 'intermediate', 'advanced', 'expert')
            num_examples: Number of examples to include (default: 5)
            include_analysis: Whether to include detailed analysis (default: True)
            progressive_difficulty: Whether examples should increase in difficulty (default: True)
        
        Returns:
            ChessLesson: Complete lesson with introduction, examples, and summary
        
        Raises:
            ValueError: If theme is invalid or no examples found
            RuntimeError: If engine is not properly initialized
        """
        if not self._initialized:
            raise RuntimeError("Engine not properly initialized")
        
        try:
            # Validate and convert difficulty
            if isinstance(difficulty, str):
                difficulty = DifficultyLevel(difficulty.lower())
            
            # Validate theme
            if theme not in TACTICAL_THEMES:
                available_themes = ', '.join(sorted(TACTICAL_THEMES.keys()))
                raise ValueError(f"Invalid theme '{theme}'. Available themes: {available_themes}")
            
            # Create configuration
            config = LessonGenerationConfig(
                theme=theme,
                difficulty=difficulty,
                num_examples=num_examples,
                include_analysis=include_analysis,
                progressive_difficulty=progressive_difficulty
            )
            
            logger.info(f"Generating lesson: {theme} ({difficulty.value}, {num_examples} examples)")
            
            # Generate the lesson
            lesson = self.lesson_builder.build_lesson(config)
            
            # Update statistics
            self._update_stats(lesson)
            
            logger.info(f"Successfully generated lesson: {lesson.title}")
            return lesson
            
        except Exception as e:
            logger.error(f"Failed to generate lesson: {e}")
            raise
    
    def generate_lesson_from_game(self, pgn: str, theme: Optional[str] = None,
                                difficulty: Union[str, DifficultyLevel] = "intermediate",
                                max_examples: int = 8) -> ChessLesson:
        """
        Generate a lesson based on tactical moments from a chess game.
        
        Args:
            pgn: PGN string of the chess game
            theme: Specific theme to focus on (optional, will detect automatically)
            difficulty: Target difficulty level
            max_examples: Maximum number of examples to extract
        
        Returns:
            ChessLesson: Lesson based on the game's tactical moments
        
        Raises:
            ValueError: If PGN is invalid or no tactical moments found
        """
        if not self._initialized:
            raise RuntimeError("Engine not properly initialized")
        
        try:
            # Convert difficulty
            if isinstance(difficulty, str):
                difficulty = DifficultyLevel(difficulty.lower())
            
            logger.info(f"Generating lesson from game (theme: {theme or 'auto-detect'})")
            
            # Extract tactical moments from the game
            # This would use the existing tactical_detector.py functionality
            from .tactical_detector import TacticalDetector
            detector = TacticalDetector()
            
            tactical_moments = detector.analyze_game(pgn)
            
            if not tactical_moments:
                raise ValueError("No tactical moments found in the provided game")
            
            # Convert tactical moments to puzzle examples
            examples = self._convert_tactical_moments_to_examples(tactical_moments, max_examples)
            
            # Determine theme if not specified
            if not theme:
                theme = self._detect_primary_theme(examples)
            
            # Create configuration
            config = LessonGenerationConfig(
                theme=theme,
                difficulty=difficulty,
                num_examples=len(examples),
                include_analysis=True,
                progressive_difficulty=False  # Game-based lessons don't need artificial progression
            )
            
            # Build lesson from the extracted examples
            lesson = self.lesson_builder.build_lesson_from_examples(examples, config)
            
            # Update title to reflect game origin
            lesson.title = f"Tactical Moments: {get_theme_info(theme).display_name}"
            
            # Update statistics
            self._update_stats(lesson)
            
            logger.info(f"Successfully generated game-based lesson with {len(examples)} examples")
            return lesson
            
        except Exception as e:
            logger.error(f"Failed to generate lesson from game: {e}")
            raise
    
    def get_lesson_preview(self, theme: str, difficulty: Union[str, DifficultyLevel],
                          num_examples: int = 5) -> Dict:
        """
        Get a preview of what a lesson would contain without generating full content.
        
        Args:
            theme: Tactical theme
            difficulty: Difficulty level
            num_examples: Number of examples
        
        Returns:
            Dict: Preview information including statistics and example details
        """
        try:
            # Convert difficulty
            if isinstance(difficulty, str):
                difficulty = DifficultyLevel(difficulty.lower())
            
            # Create configuration
            config = LessonGenerationConfig(
                theme=theme,
                difficulty=difficulty,
                num_examples=num_examples,
                include_analysis=True,
                progressive_difficulty=True
            )
            
            # Get preview from lesson builder
            preview = self.lesson_builder.get_lesson_preview(config)
            
            return preview
            
        except Exception as e:
            logger.error(f"Failed to generate lesson preview: {e}")
            return {'error': str(e)}
    
    def get_available_themes(self) -> Dict[str, Dict]:
        """
        Get all available tactical themes with their information.
        
        Returns:
            Dict: Theme information including display names and descriptions
        """
        themes = {}
        for theme_key in TACTICAL_THEMES:
            theme_info = get_theme_info(theme_key)
            themes[theme_key] = {
                'display_name': theme_info.display_name,
                'description': theme_info.description,
                'key_concepts': theme_info.key_concepts,
                'difficulty_range': theme_info.difficulty_range
            }
        
        return themes
    
    def get_theme_statistics(self, theme: str) -> Dict:
        """
        Get statistics about available examples for a specific theme.
        
        Args:
            theme: Tactical theme to analyze
        
        Returns:
            Dict: Statistics including example counts, rating distribution, etc.
        """
        try:
            if theme not in TACTICAL_THEMES:
                raise ValueError(f"Invalid theme: {theme}")
            
            stats = self.database.get_theme_statistics(theme)
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get theme statistics: {e}")
            return {'error': str(e)}
    
    def search_examples(self, theme: Optional[str] = None, 
                       min_rating: Optional[int] = None,
                       max_rating: Optional[int] = None,
                       limit: int = 20) -> List[PuzzleExample]:
        """
        Search for puzzle examples with specific criteria.
        
        Args:
            theme: Tactical theme to filter by (optional)
            min_rating: Minimum puzzle rating (optional)
            max_rating: Maximum puzzle rating (optional)
            limit: Maximum number of results
        
        Returns:
            List[PuzzleExample]: Matching puzzle examples
        """
        try:
            examples = self.example_selector.search_examples(
                theme=theme,
                min_rating=min_rating,
                max_rating=max_rating,
                limit=limit
            )
            
            return examples
            
        except Exception as e:
            logger.error(f"Failed to search examples: {e}")
            return []
    
    def create_custom_lesson(self, title: str, theme: str, 
                           difficulty: Union[str, DifficultyLevel],
                           example_ids: List[str]) -> ChessLesson:
        """
        Create a custom lesson from specific puzzle examples.
        
        Args:
            title: Custom lesson title
            theme: Tactical theme
            difficulty: Difficulty level
            example_ids: List of puzzle IDs to include
        
        Returns:
            ChessLesson: Custom lesson with specified examples
        """
        try:
            # Convert difficulty
            if isinstance(difficulty, str):
                difficulty = DifficultyLevel(difficulty.lower())
            
            # Get examples by IDs
            examples = []
            for puzzle_id in example_ids:
                example = self.database.get_puzzle_by_id(puzzle_id)
                if example:
                    examples.append(example)
                else:
                    logger.warning(f"Puzzle not found: {puzzle_id}")
            
            if not examples:
                raise ValueError("No valid examples found for the provided IDs")
            
            # Build custom lesson
            lesson = self.lesson_builder.build_custom_lesson(
                title=title,
                theme=theme,
                difficulty=difficulty,
                examples=examples,
                include_analysis=True
            )
            
            # Update statistics
            self._update_stats(lesson)
            
            logger.info(f"Created custom lesson: {title}")
            return lesson
            
        except Exception as e:
            logger.error(f"Failed to create custom lesson: {e}")
            raise
    
    def export_lesson(self, lesson: ChessLesson, format: str = "json") -> str:
        """
        Export a lesson to various formats.
        
        Args:
            lesson: Lesson to export
            format: Export format ('json', 'markdown', 'pgn')
        
        Returns:
            str: Exported lesson content
        """
        try:
            if format.lower() == "json":
                return self._export_lesson_json(lesson)
            elif format.lower() == "markdown":
                return self._export_lesson_markdown(lesson)
            elif format.lower() == "pgn":
                return self._export_lesson_pgn(lesson)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export lesson: {e}")
            raise
    
    def get_engine_statistics(self) -> Dict:
        """
        Get comprehensive engine statistics.
        
        Returns:
            Dict: Engine usage statistics and component information
        """
        try:
            database_stats = self.database.get_database_statistics()
            builder_stats = self.lesson_builder.get_builder_statistics()
            
            return {
                'engine_stats': dict(self._stats),
                'database_stats': database_stats,
                'builder_stats': builder_stats,
                'available_themes': len(TACTICAL_THEMES),
                'initialized': self._initialized
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine statistics: {e}")
            return {'error': str(e)}
    
    def _update_stats(self, lesson: ChessLesson) -> None:
        """Update engine usage statistics."""
        self._stats['lessons_generated'] += 1
        self._stats['examples_used'] += lesson.metadata.example_count
        self._stats['themes_covered'].add(lesson.theme)
    
    def _convert_tactical_moments_to_examples(self, tactical_moments: List, 
                                            max_examples: int) -> List[PuzzleExample]:
        """Convert tactical moments from game analysis to puzzle examples."""
        # This would integrate with the existing tactical detection system
        # For now, return a placeholder implementation
        examples = []
        
        for i, moment in enumerate(tactical_moments[:max_examples]):
            # Convert tactical moment to PuzzleExample
            # This would use the actual tactical_detector output format
            example = PuzzleExample(
                id=f"game_moment_{i}",
                fen=moment.get('fen', ''),
                solution_moves=moment.get('solution', []),
                themes=moment.get('themes', []),
                rating=moment.get('rating', 1500),
                quality_score=moment.get('quality', 0.8)
            )
            examples.append(example)
        
        return examples
    
    def _detect_primary_theme(self, examples: List[PuzzleExample]) -> str:
        """Detect the primary tactical theme from a list of examples."""
        theme_counts = {}
        
        for example in examples:
            for theme in example.themes:
                if theme in TACTICAL_THEMES:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        if theme_counts:
            return max(theme_counts, key=theme_counts.get)
        else:
            return 'tactics'  # Default fallback
    
    def _export_lesson_json(self, lesson: ChessLesson) -> str:
        """Export lesson as JSON."""
        lesson_dict = {
            'id': lesson.id,
            'title': lesson.title,
            'theme': lesson.theme,
            'difficulty': lesson.difficulty.value,
            'introduction': lesson.introduction,
            'steps': [
                {
                    'id': step.id,
                    'type': step.step_type.value,
                    'title': step.title,
                    'content': step.content,
                    'position': step.position,
                    'solution_moves': step.solution_moves,
                    'order': step.order
                }
                for step in lesson.steps
            ],
            'summary': lesson.summary,
            'metadata': {
                'example_count': lesson.metadata.example_count,
                'avg_rating': lesson.metadata.avg_rating,
                'estimated_duration_minutes': lesson.metadata.estimated_duration_minutes,
                'themes_covered': lesson.metadata.themes_covered
            },
            'created_at': lesson.created_at.isoformat()
        }
        
        return json.dumps(lesson_dict, indent=2)
    
    def _export_lesson_markdown(self, lesson: ChessLesson) -> str:
        """Export lesson as Markdown."""
        md_content = f"""# {lesson.title}

**Theme:** {get_theme_info(lesson.theme).display_name}  
**Difficulty:** {lesson.difficulty.value.title()}  
**Examples:** {lesson.metadata.example_count}  
**Estimated Duration:** {lesson.metadata.estimated_duration_minutes} minutes

## Introduction

{lesson.introduction}

## Examples

"""
        
        current_example = 0
        for step in lesson.steps:
            if step.step_type.value == 'example':
                current_example += 1
                md_content += f"### Example {current_example}\n\n"
            
            md_content += f"#### {step.title}\n\n"
            md_content += f"{step.content}\n\n"
            
            if step.position:
                md_content += f"**Position (FEN):** `{step.position}`\n\n"
            
            if step.solution_moves:
                md_content += f"**Solution:** {' '.join(step.solution_moves[:3])}\n\n"
        
        md_content += f"""## Summary

{lesson.summary}

---

*Generated by ChessTutorAI on {lesson.created_at.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return md_content
    
    def _export_lesson_pgn(self, lesson: ChessLesson) -> str:
        """Export lesson as PGN with annotations."""
        pgn_content = f"""[Event "ChessTutorAI Lesson: {lesson.title}"]
[Site "ChessTutorAI"]
[Date "{lesson.created_at.strftime('%Y.%m.%d')}"]
[Round "?"]
[White "Student"]
[Black "Exercise"]
[Result "*"]
[Theme "{lesson.theme}"]
[Difficulty "{lesson.difficulty.value}"]
[Examples "{lesson.metadata.example_count}"]

"""
        
        for i, step in enumerate(lesson.steps):
            if step.step_type.value == 'example' and step.position:
                pgn_content += f"; Example {i//2 + 1}: {step.title}\n"
                pgn_content += f"; FEN: {step.position}\n"
                if step.solution_moves:
                    pgn_content += f"; Solution: {' '.join(step.solution_moves[:3])}\n"
                pgn_content += f"; {step.content[:100]}...\n\n"
        
        pgn_content += "*\n"
        return pgn_content
