"""
Lesson Builder for ChessTutorAI lesson generation engine.
Assembles lessons from examples and AI-generated content.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid

from .models import (
    ChessLesson, LessonStep, PuzzleExample, LessonMetadata, 
    LessonGenerationConfig, DifficultyLevel, StepType,
    get_theme_info, ThemeInfo
)
from .example_selector import ExampleSelector
from .content_generator import ContentGenerator
from .logger import get_logger

logger = get_logger(__name__)


class LessonBuilder:
    """Builds structured chess lessons from examples and content."""
    
    def __init__(self, example_selector: ExampleSelector, content_generator: ContentGenerator):
        """Initialize the lesson builder."""
        self.example_selector = example_selector
        self.content_generator = content_generator
        logger.info("Lesson builder initialized")
    
    def build_lesson(self, config: LessonGenerationConfig) -> ChessLesson:
        """Build a complete chess lesson from configuration."""
        try:
            logger.info(f"Building lesson: {config.theme} ({config.difficulty.value})")
            
            # Get theme information
            theme_info = get_theme_info(config.theme)
            
            # Select examples for the lesson
            examples = self.example_selector.select_examples(config)
            if not examples:
                raise ValueError(f"No suitable examples found for {config.theme}")
            
            logger.info(f"Selected {len(examples)} examples for lesson")
            
            # Generate lesson content
            introduction = self.content_generator.generate_introduction(
                config.theme, config.difficulty, examples
            )
            
            # Build lesson steps
            steps = self._build_lesson_steps(examples, config, theme_info)
            
            # Generate summary
            summary = self.content_generator.generate_summary(
                config.theme, config.difficulty, examples
            )
            
            # Create lesson metadata
            metadata = self._create_lesson_metadata(config, examples, theme_info)
            
            # Assemble the complete lesson
            lesson = ChessLesson(
                id=str(uuid.uuid4()),
                title=self._generate_lesson_title(config, theme_info),
                theme=config.theme,
                difficulty=config.difficulty,
                introduction=introduction,
                steps=steps,
                summary=summary,
                metadata=metadata,
                created_at=datetime.now()
            )
            
            # Validate the lesson
            self._validate_lesson(lesson)
            
            logger.info(f"Successfully built lesson with {len(steps)} steps")
            return lesson
            
        except Exception as e:
            logger.error(f"Failed to build lesson: {e}")
            raise
    
    def build_lesson_from_examples(self, examples: List[PuzzleExample], 
                                 config: LessonGenerationConfig) -> ChessLesson:
        """Build a lesson from pre-selected examples."""
        try:
            logger.info(f"Building lesson from {len(examples)} provided examples")
            
            # Get theme information
            theme_info = get_theme_info(config.theme)
            
            # Generate lesson content
            introduction = self.content_generator.generate_introduction(
                config.theme, config.difficulty, examples
            )
            
            # Build lesson steps
            steps = self._build_lesson_steps(examples, config, theme_info)
            
            # Generate summary
            summary = self.content_generator.generate_summary(
                config.theme, config.difficulty, examples
            )
            
            # Create lesson metadata
            metadata = self._create_lesson_metadata(config, examples, theme_info)
            
            # Assemble the complete lesson
            lesson = ChessLesson(
                id=str(uuid.uuid4()),
                title=self._generate_lesson_title(config, theme_info),
                theme=config.theme,
                difficulty=config.difficulty,
                introduction=introduction,
                steps=steps,
                summary=summary,
                metadata=metadata,
                created_at=datetime.now()
            )
            
            # Validate the lesson
            self._validate_lesson(lesson)
            
            logger.info(f"Successfully built lesson from provided examples")
            return lesson
            
        except Exception as e:
            logger.error(f"Failed to build lesson from examples: {e}")
            raise
    
    def _build_lesson_steps(self, examples: List[PuzzleExample], 
                          config: LessonGenerationConfig, 
                          theme_info: ThemeInfo) -> List[LessonStep]:
        """Build the sequence of lesson steps."""
        steps = []
        
        for i, example in enumerate(examples):
            try:
                # Determine step structure based on configuration
                if config.include_analysis:
                    # Full structure: Example -> Solution -> Analysis
                    example_step = self._create_example_step(example, i, config, theme_info)
                    solution_step = self._create_solution_step(example, i, config, theme_info)
                    analysis_step = self._create_analysis_step(example, i, config, theme_info)
                    
                    steps.extend([example_step, solution_step, analysis_step])
                else:
                    # Simple structure: Example -> Solution
                    example_step = self._create_example_step(example, i, config, theme_info)
                    solution_step = self._create_solution_step(example, i, config, theme_info)
                    
                    steps.extend([example_step, solution_step])
                
            except Exception as e:
                logger.warning(f"Failed to create steps for example {i}: {e}")
                continue
        
        logger.debug(f"Created {len(steps)} lesson steps")
        return steps
    
    def _create_example_step(self, example: PuzzleExample, index: int,
                           config: LessonGenerationConfig, theme_info: ThemeInfo) -> LessonStep:
        """Create an example presentation step."""
        if config.include_analysis:
            content = self.content_generator.generate_step_content(
                example, StepType.EXAMPLE, config.difficulty, theme_info
            )
        else:
            content = f"Find the best move for {'Black' if 'b' in example.fen.split()[1] else 'White'} in this position."
        
        return LessonStep(
            id=str(uuid.uuid4()),
            step_type=StepType.EXAMPLE,
            title=f"Example {index + 1}: Find the Best Move",
            content=content,
            position=example.fen,
            example=example,
            order=index * 3 + 1 if config.include_analysis else index * 2 + 1
        )
    
    def _create_solution_step(self, example: PuzzleExample, index: int,
                            config: LessonGenerationConfig, theme_info: ThemeInfo) -> LessonStep:
        """Create a solution presentation step."""
        if config.include_analysis:
            content = self.content_generator.generate_step_content(
                example, StepType.SOLUTION, config.difficulty, theme_info
            )
        else:
            # Simple solution without AI explanation
            solution_moves = ' '.join(example.solution_moves[:3])
            content = f"The solution is: {solution_moves}"
        
        return LessonStep(
            id=str(uuid.uuid4()),
            step_type=StepType.SOLUTION,
            title=f"Example {index + 1}: Solution",
            content=content,
            position=example.fen,
            example=example,
            solution_moves=example.solution_moves,
            order=index * 3 + 2 if config.include_analysis else index * 2 + 2
        )
    
    def _create_analysis_step(self, example: PuzzleExample, index: int,
                            config: LessonGenerationConfig, theme_info: ThemeInfo) -> LessonStep:
        """Create an analysis step."""
        content = self.content_generator.generate_step_content(
            example, StepType.ANALYSIS, config.difficulty, theme_info
        )
        
        return LessonStep(
            id=str(uuid.uuid4()),
            step_type=StepType.ANALYSIS,
            title=f"Example {index + 1}: Analysis",
            content=content,
            position=example.fen,
            example=example,
            solution_moves=example.solution_moves,
            order=index * 3 + 3
        )
    
    def _create_lesson_metadata(self, config: LessonGenerationConfig, 
                              examples: List[PuzzleExample], 
                              theme_info: ThemeInfo) -> LessonMetadata:
        """Create comprehensive lesson metadata."""
        # Calculate statistics
        ratings = [ex.rating for ex in examples]
        quality_scores = [ex.quality_score for ex in examples]
        
        # Collect all themes from examples
        all_themes = set()
        for example in examples:
            all_themes.update(example.themes)
        
        # Calculate estimated duration (rough estimate)
        base_time = 5  # minutes per example
        if config.include_analysis:
            base_time = 8  # more time with analysis
        
        estimated_duration = len(examples) * base_time
        
        return LessonMetadata(
            example_count=len(examples),
            avg_rating=sum(ratings) / len(ratings) if ratings else 1500,
            min_rating=min(ratings) if ratings else 1500,
            max_rating=max(ratings) if ratings else 1500,
            avg_quality_score=sum(quality_scores) / len(quality_scores) if quality_scores else 0.5,
            themes_covered=list(all_themes),
            estimated_duration_minutes=estimated_duration,
            includes_analysis=config.include_analysis,
            progressive_difficulty=config.progressive_difficulty,
            generation_config=config
        )
    
    def _generate_lesson_title(self, config: LessonGenerationConfig, 
                             theme_info: ThemeInfo) -> str:
        """Generate an appropriate lesson title."""
        difficulty_titles = {
            DifficultyLevel.BEGINNER: "Introduction to",
            DifficultyLevel.INTERMEDIATE: "Mastering",
            DifficultyLevel.ADVANCED: "Advanced",
            DifficultyLevel.EXPERT: "Expert-Level"
        }
        
        prefix = difficulty_titles.get(config.difficulty, "")
        return f"{prefix} {theme_info.display_name}".strip()
    
    def _validate_lesson(self, lesson: ChessLesson) -> None:
        """Validate the constructed lesson."""
        # Check basic structure
        if not lesson.title or not lesson.introduction or not lesson.summary:
            raise ValueError("Lesson missing required content")
        
        if not lesson.steps:
            raise ValueError("Lesson has no steps")
        
        # Validate steps
        for i, step in enumerate(lesson.steps):
            if not step.title or not step.content:
                raise ValueError(f"Step {i} missing required content")
            
            if not step.position:
                raise ValueError(f"Step {i} missing chess position")
        
        # Check step ordering
        orders = [step.order for step in lesson.steps]
        if len(set(orders)) != len(orders):
            logger.warning("Duplicate step orders detected")
        
        # Validate metadata
        if lesson.metadata.example_count != len([s for s in lesson.steps if s.step_type == StepType.EXAMPLE]):
            logger.warning("Metadata example count mismatch")
        
        logger.debug("Lesson validation passed")
    
    def get_lesson_preview(self, config: LessonGenerationConfig) -> Dict:
        """Get a preview of what the lesson would contain."""
        try:
            theme_info = get_theme_info(config.theme)
            examples = self.example_selector.select_examples(config)
            
            if not examples:
                return {
                    'error': f"No suitable examples found for {config.theme}",
                    'theme': config.theme,
                    'difficulty': config.difficulty.value
                }
            
            # Calculate preview statistics
            ratings = [ex.rating for ex in examples]
            quality_scores = [ex.quality_score for ex in examples]
            
            all_themes = set()
            for example in examples:
                all_themes.update(example.themes)
            
            step_count = len(examples) * (3 if config.include_analysis else 2)
            estimated_duration = len(examples) * (8 if config.include_analysis else 5)
            
            return {
                'title': self._generate_lesson_title(config, theme_info),
                'theme': theme_info.display_name,
                'difficulty': config.difficulty.value,
                'example_count': len(examples),
                'step_count': step_count,
                'avg_rating': sum(ratings) / len(ratings),
                'rating_range': [min(ratings), max(ratings)],
                'avg_quality': sum(quality_scores) / len(quality_scores),
                'themes_covered': sorted(list(all_themes)),
                'estimated_duration_minutes': estimated_duration,
                'includes_analysis': config.include_analysis,
                'progressive_difficulty': config.progressive_difficulty
            }
            
        except Exception as e:
            logger.error(f"Failed to generate lesson preview: {e}")
            return {
                'error': str(e),
                'theme': config.theme,
                'difficulty': config.difficulty.value
            }
    
    def build_custom_lesson(self, title: str, theme: str, difficulty: DifficultyLevel,
                          examples: List[PuzzleExample], include_analysis: bool = True) -> ChessLesson:
        """Build a custom lesson with specific parameters."""
        try:
            # Create custom configuration
            config = LessonGenerationConfig(
                theme=theme,
                difficulty=difficulty,
                num_examples=len(examples),
                include_analysis=include_analysis,
                progressive_difficulty=False  # Custom lessons don't need progression
            )
            
            # Get theme information
            theme_info = get_theme_info(theme)
            
            # Generate content
            introduction = self.content_generator.generate_introduction(
                theme, difficulty, examples
            )
            
            # Build steps
            steps = self._build_lesson_steps(examples, config, theme_info)
            
            # Generate summary
            summary = self.content_generator.generate_summary(
                theme, difficulty, examples
            )
            
            # Create metadata
            metadata = self._create_lesson_metadata(config, examples, theme_info)
            
            # Create lesson with custom title
            lesson = ChessLesson(
                id=str(uuid.uuid4()),
                title=title,
                theme=theme,
                difficulty=difficulty,
                introduction=introduction,
                steps=steps,
                summary=summary,
                metadata=metadata,
                created_at=datetime.now()
            )
            
            # Validate
            self._validate_lesson(lesson)
            
            logger.info(f"Built custom lesson: {title}")
            return lesson
            
        except Exception as e:
            logger.error(f"Failed to build custom lesson: {e}")
            raise
    
    def get_builder_statistics(self) -> Dict:
        """Get statistics about the lesson builder."""
        return {
            'example_selector_stats': self.example_selector.get_selection_statistics(),
            'content_generator_provider': self.content_generator.ai_provider,
            'supported_step_types': [step_type.value for step_type in StepType],
            'supported_difficulties': [diff.value for diff in DifficultyLevel]
        }