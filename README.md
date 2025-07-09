# ChessTutorAI - Tactical Lesson Engine

A **small but powerful** chess lesson generation engine focused on creating high-quality tactical lessons with smart example selection from real Lichess puzzles.

## 🎯 Core Features

- **Tactical Lesson Generation**: AI-powered lessons for 10+ tactical themes
- **Smart Example Selection**: Intelligent puzzle selection from 3M+ Lichess puzzles
- **Real Chess Positions**: All examples from actual games, not AI-generated
- **Multiple Export Formats**: JSON, Markdown, and PGN output
- **Clean Architecture**: Minimal, maintainable codebase
- **Django Integration Ready**: Designed for seamless API integration

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/chesstutorai.git
cd chesstutorai

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Download Lichess puzzle database (one-time setup)
python scripts/download_lichess_puzzles.py
```

### Basic Usage

```python
from chess_lesson_engine import ChessLessonEngine

# Initialize the engine
engine = ChessLessonEngine()

# Generate a lesson
lesson = engine.generate_lesson(
    theme="pin",
    difficulty="intermediate", 
    num_examples=5
)

# Export to different formats
engine.export_lesson(lesson, "my_lesson.json", format="json")
engine.export_lesson(lesson, "my_lesson.md", format="markdown")
engine.export_lesson(lesson, "my_lesson.pgn", format="pgn")
```

### Command Line Interface

```bash
# Generate a basic lesson
python scripts/generate_lesson.py --theme pin --difficulty intermediate

# Generate with custom settings
python scripts/generate_lesson.py \
    --theme fork \
    --difficulty advanced \
    --examples 8 \
    --output my_lesson.json \
    --format json

# Clean output (no AI analysis, faster generation)
python scripts/generate_lesson.py --theme skewer --clean

# List available themes
python scripts/generate_lesson.py --list-themes
```

## 📚 Available Tactical Themes

| Theme | Description | Difficulty Levels |
|-------|-------------|-------------------|
| **pin** | Pieces unable to move without exposing valuable pieces | Beginner, Intermediate, Advanced |
| **fork** | Single piece attacking multiple enemy pieces | Beginner, Intermediate, Advanced |
| **skewer** | Forcing valuable piece to move, exposing less valuable piece | Intermediate, Advanced |
| **discovered-attack** | Moving piece reveals attack from another piece | Intermediate, Advanced |
| **double-attack** | Simultaneous attacks on multiple targets | Beginner, Intermediate, Advanced |
| **deflection** | Forcing piece away from important duty | Intermediate, Advanced |
| **decoy** | Luring piece to unfavorable square | Intermediate, Advanced |
| **clearance** | Moving piece to clear path for another | Advanced |
| **interference** | Blocking opponent's piece coordination | Advanced |
| **x-ray** | Attack through another piece | Advanced |

## 🔧 Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional
export CHESS_TUTOR_DB_PATH="data/lichess_puzzles.db"
export CHESS_TUTOR_LOG_LEVEL="INFO"
export CHESS_TUTOR_CACHE_ENABLED="true"
```

### Configuration File

Create `config.json` in the project root:

```json
{
  "database_path": "data/lichess_puzzles.db",
  "openai": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "lesson_generation": {
    "default_examples": 5,
    "include_analysis": false,
    "cache_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file": "chess_lesson_engine.log"
  }
}
```

## 📖 API Reference

### ChessLessonEngine

The main engine class for generating tactical lessons.

```python
from chess_lesson_engine import ChessLessonEngine, LessonGenerationConfig

engine = ChessLessonEngine()
```

#### Methods

##### `generate_lesson(theme, difficulty, num_examples=5, **kwargs)`

Generate a tactical lesson for the specified theme and difficulty.

**Parameters:**
- `theme` (str): Tactical theme (see available themes above)
- `difficulty` (str): Difficulty level ("beginner", "intermediate", "advanced")
- `num_examples` (int): Number of puzzle examples to include (default: 5)
- `include_analysis` (bool): Include AI analysis of positions (default: False)
- `export_format` (str): Output format ("json", "markdown", "pgn")

**Returns:**
- `ChessLesson`: Generated lesson object

**Example:**
```python
lesson = engine.generate_lesson(
    theme="fork",
    difficulty="intermediate",
    num_examples=8,
    include_analysis=True
)
```

##### `export_lesson(lesson, filename, format="json")`

Export lesson to file in specified format.

**Parameters:**
- `lesson` (ChessLesson): Lesson object to export
- `filename` (str): Output filename
- `format` (str): Export format ("json", "markdown", "pgn")

##### `get_available_themes()`

Get list of all available tactical themes.

**Returns:**
- `List[str]`: List of theme names

##### `get_theme_info(theme)`

Get detailed information about a specific theme.

**Parameters:**
- `theme` (str): Theme name

**Returns:**
- `dict`: Theme information including description and difficulty levels

### LessonGenerationConfig

Configuration class for customizing lesson generation.

```python
from chess_lesson_engine import LessonGenerationConfig

config = LessonGenerationConfig(
    theme="pin",
    difficulty="intermediate",
    num_examples=5,
    include_analysis=False,
    min_rating=1400,
    max_rating=2000
)

lesson = engine.generate_lesson_with_config(config)
```

#### Configuration Options

- `theme` (str): Tactical theme
- `difficulty` (str): Difficulty level
- `num_examples` (int): Number of examples
- `include_analysis` (bool): Include AI position analysis
- `min_rating` (int): Minimum puzzle rating
- `max_rating` (int): Maximum puzzle rating
- `min_popularity` (int): Minimum puzzle popularity
- `exclude_themes` (List[str]): Themes to exclude from selection

### ChessLesson

Lesson data structure containing generated content.

```python
# Access lesson data
print(lesson.title)           # Lesson title
print(lesson.introduction)    # AI-generated introduction
print(lesson.summary)         # AI-generated summary

# Access examples
for example in lesson.examples:
    print(f"Position: {example.fen}")
    print(f"Solution: {example.solution}")
    print(f"Rating: {example.rating}")
```

#### Properties

- `title` (str): Lesson title
- `theme` (str): Tactical theme
- `difficulty` (str): Difficulty level
- `introduction` (str): AI-generated introduction
- `summary` (str): AI-generated summary
- `examples` (List[PuzzleExample]): List of puzzle examples
- `metadata` (dict): Additional lesson metadata

## 🔌 Django Integration

ChessTutorAI is designed for seamless integration with Django APIs.

### Basic Integration

```python
# views.py
from django.http import JsonResponse
from chess_lesson_engine import ChessLessonEngine

engine = ChessLessonEngine()

def generate_lesson_api(request):
    theme = request.GET.get('theme', 'pin')
    difficulty = request.GET.get('difficulty', 'intermediate')
    
    lesson = engine.generate_lesson(theme=theme, difficulty=difficulty)
    
    return JsonResponse({
        'title': lesson.title,
        'introduction': lesson.introduction,
        'examples': [
            {
                'fen': ex.fen,
                'solution': ex.solution,
                'rating': ex.rating
            }
            for ex in lesson.examples
        ],
        'summary': lesson.summary
    })
```

### Advanced Integration with User Analytics

```python
# models.py
from django.db import models
from chess_lesson_engine import ChessLessonEngine

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skill_level = models.CharField(max_length=20)
    preferred_themes = models.JSONField(default=list)

class LessonAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson_theme = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=20)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

# services.py
class PersonalizedLessonService:
    def __init__(self):
        self.engine = ChessLessonEngine()
    
    def generate_personalized_lesson(self, user):
        profile = user.userprofile
        
        # Analyze user performance
        recent_attempts = LessonAttempt.objects.filter(
            user=user
        ).order_by('-completed_at')[:10]
        
        # Determine optimal difficulty and theme
        difficulty = self._calculate_optimal_difficulty(recent_attempts)
        theme = self._select_optimal_theme(profile, recent_attempts)
        
        # Generate lesson
        return self.engine.generate_lesson(
            theme=theme,
            difficulty=difficulty,
            num_examples=self._calculate_optimal_examples(profile)
        )
```

## 🗄️ Database Schema

ChessTutorAI uses a single SQLite database with optimized schema:

```sql
-- Lichess puzzles table
CREATE TABLE puzzles (
    id TEXT PRIMARY KEY,              -- Lichess puzzle ID
    fen TEXT NOT NULL,                -- Position FEN
    moves TEXT NOT NULL,              -- Solution moves
    rating INTEGER,                   -- Puzzle rating
    themes TEXT,                      -- Comma-separated themes
    game_url TEXT,                    -- Source game URL
    popularity INTEGER,               -- Puzzle popularity
    nb_plays INTEGER,                 -- Number of plays
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimized indexes for fast queries
CREATE INDEX idx_puzzles_themes ON puzzles(themes);
CREATE INDEX idx_puzzles_rating ON puzzles(rating);
CREATE INDEX idx_puzzles_popularity ON puzzles(popularity);
CREATE INDEX idx_puzzles_theme_rating ON puzzles(themes, rating);
```

### Database Statistics

- **Total Puzzles**: 3,000,000+
- **Themes Covered**: 30+ tactical themes
- **Rating Range**: 600-3000
- **Database Size**: ~45MB (compressed)
- **Query Performance**: <50ms average

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_engine.py          # Core engine tests
python -m pytest tests/test_example_selector.py # Example selection tests
python -m pytest tests/test_content_generator.py # AI content tests

# Run with coverage
python -m pytest --cov=chess_lesson_engine
```

## 📊 Performance

### Lesson Generation Performance

| Configuration | Generation Time | API Calls | Database Queries |
|---------------|----------------|-----------|------------------|
| Clean Mode (default) | ~6 seconds | 2 | 3-5 |
| With Analysis | ~45 seconds | 17+ | 3-5 |
| Cached Results | ~2 seconds | 0-2 | 1-2 |

### Memory Usage

- **Engine Initialization**: ~50MB
- **Lesson Generation**: ~20MB additional
- **Database Cache**: ~10MB
- **Total Runtime**: ~80MB typical

## 🔍 Troubleshooting

### Common Issues

#### "No puzzles found for theme"
```bash
# Check available themes
python scripts/generate_lesson.py --list-themes

# Verify database
ls -la data/lichess_puzzles.db

# Re-download if needed
python scripts/download_lichess_puzzles.py --force
```

#### "OpenAI API key not found"
```bash
# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Or create config.json with API key
echo '{"openai": {"api_key": "your-key-here"}}' > config.json
```

#### "Slow lesson generation"
```bash
# Use clean mode (default)
python scripts/generate_lesson.py --theme pin --clean

# Enable caching
export CHESS_TUTOR_CACHE_ENABLED="true"

# Reduce examples
python scripts/generate_lesson.py --theme pin --examples 3
```

### Debug Mode

Enable debug logging for detailed information:

```bash
export CHESS_TUTOR_LOG_LEVEL="DEBUG"
python scripts/generate_lesson.py --theme pin
```

## 🤝 Contributing

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/chesstutorai.git
cd chesstutorai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

### Code Style

We use Black for code formatting and flake8 for linting:

```bash
# Format code
black chess_lesson_engine/

# Check linting
flake8 chess_lesson_engine/

# Type checking
mypy chess_lesson_engine/
```

### Adding New Themes

1. Add theme to `THEME_REGISTRY` in `chess_lesson_engine/models.py`
2. Create theme-specific prompts in `chess_lesson_engine/prompts.py`
3. Add theme detection logic in `chess_lesson_engine/example_selector.py`
4. Update tests and documentation

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Lichess**: For providing the excellent puzzle database
- **OpenAI**: For GPT models used in content generation
- **Python Chess**: For chess position handling
- **Contributors**: All developers who helped improve this project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/chesstutorai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/chesstutorai/discussions)
- **Email**: support@chesstutorai.com

---

**ChessTutorAI** - Making chess tactical training accessible through intelligent lesson generation.