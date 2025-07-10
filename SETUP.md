# Caissify Puzzle Engine - Setup Guide

## Quick Start

### 1. Clone and Install
```bash
git clone git@github.com:lexisvar/caissify_puzzle_engine.git
cd caissify_puzzle_engine
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Download Puzzle Database
The engine requires a Lichess puzzle database. You can either:

**Option A: Use existing database**
- Place your `lichess_puzzles.db` file in the `data/` directory

**Option B: Download fresh puzzles**
```bash
python scripts/download_lichess_puzzles.py --limit 100000
```

### 4. Test the Engine
```bash
# Quick test
python -c "from chess_lesson_engine import ChessLessonEngine; engine = ChessLessonEngine(); print('✅ Engine ready!')"

# Generate a lesson
python scripts/generate_lesson.py pin beginner --examples 2
```

## Usage Examples

### Python API
```python
from chess_lesson_engine import ChessLessonEngine

# Initialize engine
engine = ChessLessonEngine()

# Generate lesson
lesson = engine.generate_lesson("pin", "intermediate", num_examples=3)

# Export to different formats
json_data = engine.export_lesson(lesson, format="json")
markdown_content = engine.export_lesson(lesson, format="markdown")
pgn_content = engine.export_lesson(lesson, format="pgn")

# Get available themes
themes = engine.get_available_themes()
print(f"Available themes: {list(themes.keys())}")
```

### Command Line
```bash
# Generate lessons
python scripts/generate_lesson.py fork intermediate --examples 5
python scripts/generate_lesson.py mate beginner --examples 3 --output lesson.md

# Available themes: pin, fork, skewer, discoveredAttack, mate, deflection, decoy, attraction, sacrifice, tactics
```

## Django Integration

```python
# views.py
from chess_lesson_engine import ChessLessonEngine

class LessonGenerationView(APIView):
    def __init__(self):
        self.engine = ChessLessonEngine()
    
    def post(self, request):
        theme = request.data.get('theme')
        difficulty = request.data.get('difficulty')
        num_examples = request.data.get('num_examples', 5)
        
        lesson = self.engine.generate_lesson(theme, difficulty, num_examples)
        
        return Response({
            'lesson_id': lesson.id,
            'title': lesson.title,
            'content': self.engine.export_lesson(lesson, format="json")
        })
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI content generation
- `DATABASE_PATH`: Optional, defaults to `data/lichess_puzzles.db`

### Config File (Optional)
Copy `config.sample.json` to `config.json` and customize:
```json
{
  "openai": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 512
  },
  "lesson_generation": {
    "max_attempts": 5
  }
}
```

## Database Requirements

The engine requires a Lichess puzzle database with the following structure:
- **Size**: ~4GB for full database
- **Format**: SQLite with `lichess_puzzles` table
- **Fields**: puzzle_id, fen, moves, rating, themes, etc.

## Performance Notes

- **Lesson Generation**: ~30 seconds with AI content
- **Database Queries**: <1 second for puzzle selection
- **Memory Usage**: ~80MB typical runtime
- **Initialization**: <2 seconds

## Troubleshooting

### Common Issues

1. **"No suitable examples found"**
   - Ensure puzzle database is properly loaded
   - Check that the theme exists in the database
   - Try different difficulty levels

2. **OpenAI API errors**
   - Verify API key is set correctly
   - Check API quota and billing
   - Try reducing `max_tokens` in config

3. **Database connection issues**
   - Ensure `data/lichess_puzzles.db` exists
   - Check file permissions
   - Verify database integrity

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from chess_lesson_engine import ChessLessonEngine
engine = ChessLessonEngine()
```

## Support

For issues and questions:
- Check the comprehensive `README.md`
- Review `CLEANUP_COMPLETION_SUMMARY.md` for implementation details
- See `examples/` directory for usage patterns