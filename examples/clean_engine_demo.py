#!/usr/bin/env python3
"""
ChessTutorAI Clean Engine Demo

Demonstrates the new focused chess lesson generation engine.
This example shows how to use the simplified, powerful interface.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chess_lesson_engine import create_engine, DifficultyLevel

def main():
    """Demonstrate the clean chess lesson engine."""
    print("🏁 ChessTutorAI Clean Engine Demo")
    print("=" * 50)
    
    try:
        # Initialize the engine
        print("\n📚 Initializing chess lesson engine...")
        engine = create_engine()
        
        # Show available themes
        print("\n🎯 Available tactical themes:")
        themes = engine.get_available_themes()
        for theme_key, theme_info in list(themes.items())[:5]:  # Show first 5
            print(f"  • {theme_info['display_name']}: {theme_info['description'][:60]}...")
        print(f"  ... and {len(themes) - 5} more themes")
        
        # Generate a lesson
        print("\n🎓 Generating lesson: Pin tactics (Intermediate level)")
        lesson = engine.generate_lesson(
            theme='pin',
            difficulty=DifficultyLevel.INTERMEDIATE,
            num_examples=3,
            include_analysis=True
        )
        
        print(f"\n✅ Generated lesson: '{lesson.title}'")
        print(f"   📊 {lesson.metadata.example_count} examples")
        print(f"   ⏱️  {lesson.metadata.estimated_duration_minutes} minutes")
        print(f"   🎯 Average rating: {lesson.metadata.avg_rating:.0f}")
        
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
        
        # Export examples
        print(f"\n💾 Export examples:")
        
        # Export to JSON
        json_output = engine.export_lesson(lesson, format='json')
        print(f"   📄 JSON export: {len(json_output)} characters")
        
        # Export to Markdown
        markdown_output = engine.export_lesson(lesson, format='markdown')
        print(f"   📝 Markdown export: {len(markdown_output)} characters")
        
        # Search for examples
        print(f"\n🔍 Searching for fork examples (rating 1400-1800):")
        examples = engine.search_examples(
            theme='fork',
            min_rating=1400,
            max_rating=1800,
            limit=5
        )
        
        print(f"   Found {len(examples)} examples:")
        for example in examples:
            print(f"   • Rating {example.rating}: {', '.join(example.themes[:2])}")
        
        # Get lesson preview
        print(f"\n👀 Preview for advanced skewer lesson:")
        preview = engine.get_lesson_preview(
            theme='skewer',
            difficulty=DifficultyLevel.ADVANCED,
            num_examples=4
        )
        
        if 'error' not in preview:
            print(f"   📚 {preview['title']}")
            print(f"   📊 {preview['example_count']} examples, {preview['step_count']} steps")
            print(f"   ⭐ Average rating: {preview['avg_rating']:.0f}")
            print(f"   🏷️  Themes: {', '.join(preview['themes_covered'][:3])}")
        
        # Engine statistics
        print(f"\n📈 Engine statistics:")
        stats = engine.get_engine_statistics()
        if 'error' not in stats:
            print(f"   🎓 Lessons generated: {stats['engine_stats']['lessons_generated']}")
            print(f"   📝 Examples used: {stats['engine_stats']['examples_used']}")
            print(f"   🎯 Available themes: {stats['available_themes']}")
            if 'database_stats' in stats:
                db_stats = stats['database_stats']
                print(f"   💾 Database puzzles: {db_stats.get('total_puzzles', 'N/A')}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\n💡 The engine is now ready for integration into your chess application.")
        print(f"   Use 'from chess_lesson_engine import create_engine' to get started.")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print(f"   Make sure the puzzle database is available and AI providers are configured.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())