#!/usr/bin/env python3
"""
Lichess Puzzle Database Demo

This script demonstrates how to download and use the Lichess puzzle database
with the ChessTutorAI engine.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import chess_lesson_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

from chess_lesson_engine import create_engine

def main():
    print("🚀 ChessTutorAI - Lichess Puzzle Database Demo")
    print("=" * 60)
    
    # Check if Lichess database exists
    lichess_db_path = Path(__file__).parent.parent / "data" / "lichess_puzzles.db"
    
    if not lichess_db_path.exists():
        print("📥 Lichess puzzle database not found!")
        print("🔄 To download the full Lichess puzzle database (~5M puzzles):")
        print("   python scripts/download_lichess_puzzles.py")
        print()
        print("🚀 For a quick setup with 50k high-quality puzzles:")
        print("   python scripts/download_lichess_puzzles.py --quick")
        print()
        print("📍 Using default database for now...")
        
        # Use default database
        engine = create_engine()
    else:
        print("✅ Lichess puzzle database found!")
        print(f"📁 Database: {lichess_db_path}")
        
        # Use Lichess database
        engine = create_engine(use_lichess_db=True)
    
    # Show available themes
    print("\n🎯 Available tactical themes:")
    themes = engine.get_available_themes()
    for i, (theme_key, theme_info) in enumerate(list(themes.items())[:10]):
        print(f"  • {theme_info['display_name']}: {theme_info['description'][:60]}...")
    
    if len(themes) > 10:
        print(f"  ... and {len(themes) - 10} more themes")
    
    # Try to generate a lesson
    print("\n🎓 Generating sample lesson...")
    try:
        lesson = engine.generate_lesson('pin', 'intermediate', 3)
        print(f"✅ Generated lesson: '{lesson.title}'")
        print(f"   📊 {lesson.metadata.example_count} examples")
        print(f"   ⏱️  {lesson.metadata.estimated_duration_minutes} minutes")
        print(f"   🎯 Average rating: {lesson.metadata.avg_rating}")
        
        # Show lesson structure
        print(f"\n📋 Lesson structure ({len(lesson.steps)} steps):")
        for i, step in enumerate(lesson.steps[:6]):  # Show first 6 steps
            print(f"   {i+1}. {step.step_type.value.title()}: {step.title}")
        
        if len(lesson.steps) > 6:
            print(f"   ... and {len(lesson.steps) - 6} more steps")
        
        # Show introduction preview
        print(f"\n📖 Introduction preview:")
        intro_preview = lesson.introduction[:200] + "..." if len(lesson.introduction) > 200 else lesson.introduction
        print(f"   {intro_preview}")
        
    except Exception as e:
        print(f"❌ Failed to generate lesson: {e}")
    
    # Show engine statistics
    print("\n📈 Engine statistics:")
    try:
        stats = engine.get_engine_statistics()
        if 'database_stats' in stats:
            db_stats = stats['database_stats']
            print(f"   📍 Total puzzles: {db_stats.get('total_puzzles', 'Unknown')}")
            print(f"   ⭐ Average quality: {db_stats.get('avg_quality', 'Unknown')}")
        else:
            print("   📊 Statistics not available")
    except Exception as e:
        print(f"   ⚠️  Could not get statistics: {e}")
    
    print("\n💡 Next steps:")
    if not lichess_db_path.exists():
        print("1. Download Lichess puzzles: python scripts/download_lichess_puzzles.py --quick")
        print("2. Re-run this demo to see the difference!")
    else:
        print("1. Generate more lessons with different themes and difficulties")
        print("2. Export lessons to JSON, Markdown, or PGN formats")
        print("3. Search for specific puzzle examples")
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    main()