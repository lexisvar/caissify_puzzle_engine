"""
ChessTutorAI - Chess Lesson Generation Engine

A focused, powerful engine for generating educational chess lessons with AI-powered content.
Designed for easy integration into other chess applications and platforms.
"""

from .engine import ChessLessonEngine
from .models import (
    ChessLesson,
    LessonStep,
    PuzzleExample,
    LessonMetadata,
    LessonGenerationConfig,
    DifficultyLevel,
    StepType,
    TACTICAL_THEMES
)

# Main engine class - primary interface
__all__ = [
    'ChessLessonEngine',
    'ChessLesson',
    'LessonStep', 
    'PuzzleExample',
    'LessonMetadata',
    'LessonGenerationConfig',
    'DifficultyLevel',
    'StepType',
    'TACTICAL_THEMES'
]

# Version information
__version__ = "2.0.0"
__author__ = "ChessTutorAI Team"
__description__ = "Chess lesson generation engine with AI-powered content"

# Quick start function for convenience
def create_engine(database_path=None, ai_provider="openai", use_lichess_db=False):
    """
    Quick start function to create a chess lesson engine.
    
    Args:
        database_path: Path to puzzle database (optional)
        ai_provider: AI provider for content generation (default: "openai")
        use_lichess_db: Use the Lichess puzzle database if available (default: False)
    
    Returns:
        ChessLessonEngine: Initialized engine ready for lesson generation
    """
    if use_lichess_db and not database_path:
        # Try to use the Lichess database if it exists
        import os
        from pathlib import Path
        lichess_db = Path(__file__).parent.parent / "data" / "lichess_puzzles.db"
        if lichess_db.exists():
            database_path = str(lichess_db)
        else:
            print("⚠️  Lichess database not found. Run 'python scripts/download_lichess_puzzles.py' to download it.")
            print("📍 Using default database for now.")
    
    return ChessLessonEngine(database_path=database_path, ai_provider=ai_provider)

# Example usage documentation
USAGE_EXAMPLE = """
# Quick Start Example:

from chess_lesson_engine import create_engine

# Initialize the engine
engine = create_engine()

# Generate a lesson
lesson = engine.generate_lesson(
    theme='pin',
    difficulty='intermediate', 
    num_examples=5
)

# Export the lesson
json_output = engine.export_lesson(lesson, format='json')
markdown_output = engine.export_lesson(lesson, format='markdown')

# Get available themes
themes = engine.get_available_themes()

# Search for specific examples
examples = engine.search_examples(theme='fork', min_rating=1400, max_rating=1800)
"""
