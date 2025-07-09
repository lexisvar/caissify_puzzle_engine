"""
Clean data models for ChessTutorAI lesson generation engine.
Defines the core data structures used throughout the system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class StepType(Enum):
    """Types of lesson steps."""
    INTRODUCTION = "introduction"
    EXAMPLE = "example"
    SOLUTION = "solution"
    SUMMARY = "summary"
    ANALYSIS = "analysis"


class DifficultyLevel(Enum):
    """Difficulty levels for lessons and puzzles."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LessonSource(Enum):
    """Sources for lesson generation."""
    PUZZLES = "puzzles"
    GAME_ANALYSIS = "game_analysis"
    MIXED = "mixed"
    CUSTOM = "custom"


@dataclass
class PuzzleExample:
    """Represents a curated puzzle example with analysis."""
    id: str
    fen: str
    solution_moves: List[str]
    themes: List[str]
    rating: int
    quality_score: float
    explanation: str = ""
    
    # Optional fields from database
    moves: Optional[str] = None
    pgn: Optional[str] = None
    game_url: Optional[str] = None
    popularity: Optional[int] = None
    nb_plays: Optional[int] = None
    
    # Processed fields
    primary_theme: Optional[str] = None
    difficulty_level: Optional[str] = None
    position_hash: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.primary_theme and self.themes:
            self.primary_theme = self.themes[0]
        
        if not self.explanation:
            self.explanation = f"A {self.primary_theme or 'tactical'} puzzle rated {self.rating}"


@dataclass
class LessonStep:
    """Individual step in a chess lesson."""
    step_type: StepType
    title: str
    content: str
    step_number: int = 0
    id: Optional[str] = None
    position: Optional[str] = None
    fen: Optional[str] = None
    move_annotation: Optional[str] = None
    example: Optional['PuzzleExample'] = None
    solution_moves: Optional[List[str]] = None
    order: int = 0
    
    # Optional fields for enhanced steps
    key_points: List[str] = field(default_factory=list)
    variations: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Ensure step_type is StepType enum."""
        if isinstance(self.step_type, str):
            self.step_type = StepType(self.step_type)


@dataclass
class LessonMetadata:
    """Metadata for generated lessons."""
    example_count: int
    avg_rating: float
    avg_quality_score: float
    estimated_duration_minutes: int
    themes_covered: List[str] = field(default_factory=list)
    includes_analysis: bool = True
    progressive_difficulty: bool = True
    generation_config: Optional['LessonGenerationConfig'] = None
    
    # Additional fields
    generation_time: str = ""
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    source: LessonSource = LessonSource.PUZZLES
    ai_provider: Optional[str] = None
    generation_duration: Optional[float] = None
    content_quality_score: Optional[float] = None
    educational_value_score: Optional[float] = None
    source_game_id: Optional[str] = None
    source_themes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.source, str):
            self.source = LessonSource(self.source)
        
        if not self.generation_time:
            self.generation_time = datetime.now().isoformat()


@dataclass
class ChessLesson:
    """Complete chess lesson with examples and structured content."""
    title: str
    theme: str
    difficulty: DifficultyLevel
    introduction: str
    steps: List[LessonStep]
    summary: str
    metadata: LessonMetadata
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # Optional lesson enhancements
    description: str = ""
    examples: List[PuzzleExample] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    follow_up_topics: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # minutes
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.difficulty, str):
            self.difficulty = DifficultyLevel(self.difficulty)
        
        # Ensure steps are properly numbered
        for i, step in enumerate(self.steps, 1):
            if step.step_number != i:
                step.step_number = i
        
        # Set default learning objectives if not provided
        if not self.learning_objectives:
            self.learning_objectives = [
                f"Understand {self.theme} tactical patterns",
                f"Recognize {self.theme} opportunities in games",
                f"Execute {self.theme} tactics accurately"
            ]
    
    def get_step_by_type(self, step_type: StepType) -> List[LessonStep]:
        """Get all steps of a specific type."""
        return [step for step in self.steps if step.step_type == step_type]
    
    def get_introduction_step(self) -> Optional[LessonStep]:
        """Get the introduction step."""
        intro_steps = self.get_step_by_type(StepType.INTRODUCTION)
        return intro_steps[0] if intro_steps else None
    
    def get_summary_step(self) -> Optional[LessonStep]:
        """Get the summary step."""
        summary_steps = self.get_step_by_type(StepType.SUMMARY)
        return summary_steps[0] if summary_steps else None
    
    def get_example_steps(self) -> List[LessonStep]:
        """Get all example steps."""
        return self.get_step_by_type(StepType.EXAMPLE)
    
    def get_solution_steps(self) -> List[LessonStep]:
        """Get all solution steps."""
        return self.get_step_by_type(StepType.SOLUTION)


@dataclass
class LessonGenerationConfig:
    """Configuration for lesson generation."""
    theme: str
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    num_examples: int = 5
    example_count: int = 5  # Keep both for compatibility
    min_quality_threshold: float = 0.7
    enable_progressive_difficulty: bool = True
    include_variations: bool = True
    include_analysis: bool = True
    progressive_difficulty: bool = True
    
    # AI content generation settings
    ai_provider: str = "openai"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 1000
    
    # Example selection weights
    quality_weight: float = 0.4
    rating_weight: float = 0.3
    diversity_weight: float = 0.3
    
    # Rating range (optional - will use difficulty defaults if not set)
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    
    # Content customization
    include_common_mistakes: bool = True
    include_key_points: bool = True
    include_follow_up_suggestions: bool = True
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.difficulty, str):
            self.difficulty = DifficultyLevel(self.difficulty)
        
        # Sync num_examples and example_count for compatibility
        if self.num_examples != self.example_count:
            # If num_examples was explicitly set, use it for example_count
            self.example_count = self.num_examples
        
        # Set default rating ranges based on difficulty if not specified
        if self.min_rating is None or self.max_rating is None:
            rating_ranges = {
                DifficultyLevel.BEGINNER: (600, 1200),
                DifficultyLevel.INTERMEDIATE: (1200, 1800),
                DifficultyLevel.ADVANCED: (1800, 2400),
                DifficultyLevel.EXPERT: (2400, 3000)
            }
            
            if self.difficulty in rating_ranges:
                default_min, default_max = rating_ranges[self.difficulty]
                self.min_rating = self.min_rating or default_min
                self.max_rating = self.max_rating or default_max


@dataclass
class GameAnalysisConfig:
    """Configuration for game-based lesson generation."""
    pgn: str
    focus: str = "tactical_moments"
    example_count: int = 3
    min_evaluation_drop: float = 150.0
    max_evaluation_drop: float = 2000.0
    
    # Analysis settings
    analysis_depth: int = 20
    time_per_position: float = 2.0
    
    # Lesson generation settings
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    ai_provider: str = "openai"
    include_context_moves: bool = True
    context_move_count: int = 3


@dataclass
class ThemeInfo:
    """Information about a tactical theme."""
    name: str
    display_name: str
    description: str
    key_concepts: List[str]
    difficulty_modifier: float = 0.0
    
    # Learning progression
    prerequisites: List[str] = field(default_factory=list)
    follow_up_themes: List[str] = field(default_factory=list)
    difficulty_range: List[str] = field(default_factory=lambda: ["beginner", "intermediate", "advanced", "expert"])
    
    # Content templates
    title_template: str = "{display_name} - {difficulty} Level"
    intro_template: str = "Learn to master {display_name} in your chess games."


# Predefined theme information
THEME_REGISTRY: Dict[str, ThemeInfo] = {
    'fork': ThemeInfo(
        name='fork',
        display_name='Fork Tactics',
        description='Master the art of attacking two pieces simultaneously',
        key_concepts=['double_attack', 'piece_coordination', 'material_gain'],
        difficulty_modifier=0.0,
        follow_up_themes=['royal_fork', 'family_fork']
    ),
    'pin': ThemeInfo(
        name='pin',
        display_name='Pin Tactics',
        description='Learn to immobilize opponent pieces effectively',
        key_concepts=['absolute_pin', 'relative_pin', 'pin_breaking'],
        difficulty_modifier=0.1,
        follow_up_themes=['skewer', 'x_ray_attack']
    ),
    'skewer': ThemeInfo(
        name='skewer',
        display_name='Skewer Tactics',
        description='Force valuable pieces to move and capture what\'s behind',
        key_concepts=['x_ray_attack', 'piece_alignment', 'forcing_moves'],
        difficulty_modifier=0.2,
        prerequisites=['pin']
    ),
    'discoveredAttack': ThemeInfo(
        name='discoveredAttack',
        display_name='Discovered Attack',
        description='Unleash hidden power by moving blocking pieces',
        key_concepts=['discovery', 'double_threat', 'piece_coordination'],
        difficulty_modifier=0.3
    ),
    'mate': ThemeInfo(
        name='mate',
        display_name='Checkmate Patterns',
        description='Deliver decisive checkmate attacks',
        key_concepts=['mating_patterns', 'king_safety', 'forcing_sequences'],
        difficulty_modifier=0.4
    ),
    'mateIn1': ThemeInfo(
        name='mateIn1',
        display_name='Mate in One',
        description='Find immediate checkmate opportunities',
        key_concepts=['pattern_recognition', 'tactical_vision', 'quick_calculation'],
        difficulty_modifier=0.2,
        follow_up_themes=['mateIn2']
    ),
    'mateIn2': ThemeInfo(
        name='mateIn2',
        display_name='Mate in Two',
        description='Execute two-move checkmate sequences',
        key_concepts=['calculation', 'forcing_moves', 'mating_nets'],
        difficulty_modifier=0.4,
        prerequisites=['mateIn1']
    ),
    'sacrifice': ThemeInfo(
        name='sacrifice',
        display_name='Tactical Sacrifices',
        description='Invest material for decisive advantage',
        key_concepts=['material_investment', 'compensation', 'calculation'],
        difficulty_modifier=0.6
    ),
    'deflection': ThemeInfo(
        name='deflection',
        display_name='Deflection Tactics',
        description='Remove key defending pieces',
        key_concepts=['overloaded_pieces', 'defensive_duties', 'tactical_shots'],
        difficulty_modifier=0.4
    ),
    'attraction': ThemeInfo(
        name='attraction',
        display_name='Attraction Tactics',
        description='Lure pieces to vulnerable squares',
        key_concepts=['piece_misdirection', 'tactical_themes', 'decoy_sacrifice'],
        difficulty_modifier=0.5
    )
}


def get_theme_info(theme: str) -> ThemeInfo:
    """Get theme information, with fallback for unknown themes."""
    return THEME_REGISTRY.get(theme, ThemeInfo(
        name=theme,
        display_name=theme.replace('_', ' ').title(),
        description=f"Learn {theme.replace('_', ' ')} tactical patterns",
        key_concepts=['pattern_recognition', 'calculation', 'tactical_vision']
    ))


def get_available_themes() -> List[str]:
    """Get list of all available themes."""
    return list(THEME_REGISTRY.keys())


def get_themes_by_difficulty(difficulty: DifficultyLevel) -> List[str]:
    """Get themes appropriate for a difficulty level."""
    difficulty_thresholds = {
        DifficultyLevel.BEGINNER: 0.2,
        DifficultyLevel.INTERMEDIATE: 0.4,
        DifficultyLevel.ADVANCED: 0.6,
        DifficultyLevel.EXPERT: 1.0
    }
    
    max_modifier = difficulty_thresholds.get(difficulty, 0.4)
    
    return [
        theme for theme, info in THEME_REGISTRY.items()
        if info.difficulty_modifier <= max_modifier
    ]


# Export TACTICAL_THEMES for backward compatibility and easy access
TACTICAL_THEMES = THEME_REGISTRY