#!/usr/bin/env python3
"""
ChessTutorAI Lesson Generator CLI

Command-line tool for generating chess lessons with the ChessTutorAI engine.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import chess_lesson_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

from chess_lesson_engine import create_engine

def main():
    parser = argparse.ArgumentParser(
        description="Generate chess lessons with ChessTutorAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a basic pin lesson (clean output, no AI analysis)
  python scripts/generate_lesson.py pin intermediate

  # Generate advanced fork lesson with 8 examples and AI analysis
  python scripts/generate_lesson.py fork advanced --examples 8 --analysis

  # Export to markdown file
  python scripts/generate_lesson.py skewer beginner --output lesson.md --format markdown

  # Use Lichess database with AI analysis
  python scripts/generate_lesson.py mate intermediate --lichess --analysis

Available themes:
  pin, fork, skewer, discovery, deflection, decoy, attraction, sacrifice,
  mate, mate_in_one, mate_in_two, tactics, endgame
        """
    )
    
    # Required arguments
    parser.add_argument("theme", help="Tactical theme (e.g., pin, fork, skewer)")
    parser.add_argument("difficulty", choices=["beginner", "intermediate", "advanced", "expert"],
                       help="Difficulty level")
    
    # Optional arguments
    parser.add_argument("--examples", "-e", type=int, default=5,
                       help="Number of examples (default: 5)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=["json", "markdown", "pgn"], default="markdown",
                       help="Output format (default: markdown)")
    parser.add_argument("--lichess", action="store_true",
                       help="Use Lichess puzzle database")
    parser.add_argument("--analysis", action="store_true",
                       help="Include detailed AI analysis (may be inaccurate)")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Minimal output")
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🚀 ChessTutorAI Lesson Generator")
        print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("💡 Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    try:
        # Initialize engine
        if not args.quiet:
            print(f"📚 Initializing engine...")
            if args.lichess:
                print("🔗 Using Lichess puzzle database")
        
        engine = create_engine(use_lichess_db=args.lichess)
        
        # Validate theme
        available_themes = engine.get_available_themes()
        if args.theme not in available_themes:
            print(f"❌ Error: Invalid theme '{args.theme}'")
            print(f"💡 Available themes: {', '.join(sorted(available_themes.keys()))}")
            return 1
        
        # Generate lesson
        if not args.quiet:
            print(f"🎓 Generating {args.theme} lesson ({args.difficulty}, {args.examples} examples)...")
        
        lesson = engine.generate_lesson(
            theme=args.theme,
            difficulty=args.difficulty,
            num_examples=args.examples,
            include_analysis=args.analysis
        )
        
        if not args.quiet:
            print(f"✅ Generated: '{lesson.title}'")
            print(f"   📊 {lesson.metadata.example_count} examples")
            print(f"   ⏱️  {lesson.metadata.estimated_duration_minutes} minutes")
            print(f"   🎯 Average rating: {lesson.metadata.avg_rating:.0f}")
        
        # Export lesson
        exported_content = engine.export_lesson(lesson, args.format)
        
        if args.output:
            # Write to file
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(exported_content)
            
            if not args.quiet:
                print(f"💾 Saved to: {args.output}")
                print(f"📄 Format: {args.format}")
                print(f"📏 Size: {len(exported_content):,} characters")
        else:
            # Print to stdout
            if not args.quiet:
                print(f"\n📖 Lesson Content ({args.format}):")
                print("=" * 50)
            print(exported_content)
        
        if not args.quiet:
            print("\n🎉 Lesson generation completed!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Generation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())