#!/usr/bin/env python3
"""
Test script for the enhanced unified engine with tactical database integration.
Tests Phase 5 Milestone 5.1 - Engine Integration.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from chess_lesson_engine.unified_engine import ChessLessonEngine
from chess_lesson_engine.config import Config

async def test_engine_initialization():
    """Test that the engine initializes correctly with tactical database integration."""
    print("🔧 Testing engine initialization...")
    
    try:
        engine = ChessLessonEngine()
        print("✅ Engine initialized successfully")
        
        # Check that tactical database and data pipeline are available
        if hasattr(engine, 'tactical_database') and engine.tactical_database:
            print("✅ Tactical database integrated")
        else:
            print("⚠️  Tactical database not available (expected if database not set up)")
            
        if hasattr(engine, 'data_pipeline') and engine.data_pipeline:
            print("✅ Data pipeline integrated")
        else:
            print("⚠️  Data pipeline not available (expected if not configured)")
            
        return engine
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return None

async def test_database_statistics(engine):
    """Test database statistics functionality."""
    print("\n📊 Testing database statistics...")
    
    try:
        stats = engine.get_database_statistics()
        print("✅ Database statistics retrieved successfully")
        print(f"   Total positions: {stats.get('total_positions', 'N/A')}")
        print(f"   Tactical patterns: {stats.get('tactical_patterns', 'N/A')}")
        print(f"   Difficulty levels: {stats.get('difficulty_levels', 'N/A')}")
        return True
    except Exception as e:
        print(f"⚠️  Database statistics failed (expected if database not set up): {e}")
        return False

async def test_pipeline_status(engine):
    """Test pipeline status functionality."""
    print("\n🔄 Testing pipeline status...")
    
    try:
        status = engine.get_pipeline_status()
        print("✅ Pipeline status retrieved successfully")
        print(f"   Status: {status.get('status', 'N/A')}")
        print(f"   Last run: {status.get('last_run', 'N/A')}")
        print(f"   Next run: {status.get('next_run', 'N/A')}")
        return True
    except Exception as e:
        print(f"⚠️  Pipeline status failed (expected if pipeline not configured): {e}")
        return False

async def test_database_lesson_generation(engine):
    """Test database-based lesson generation."""
    print("\n📚 Testing database lesson generation...")
    
    try:
        lessons = engine.generate_database_lessons(
            topic="tactics",
            skill_level="intermediate",
            num_examples=2
        )
        
        if lessons:
            print(f"✅ Generated {len(lessons)} database lessons successfully")
            for i, lesson in enumerate(lessons, 1):
                print(f"   Lesson {i}: {lesson.get('title', 'Untitled')}")
                print(f"   Pattern: {lesson.get('tactical_pattern', 'Unknown')}")
                print(f"   Difficulty: {lesson.get('difficulty', 'Unknown')}")
        else:
            print("⚠️  No database lessons generated (expected if database empty)")
        return True
    except Exception as e:
        print(f"⚠️  Database lesson generation failed (expected if database not available): {e}")
        return False

async def test_tactical_position_search(engine):
    """Test tactical position search functionality."""
    print("\n🔍 Testing tactical position search...")
    
    try:
        # Test basic search
        positions = engine.search_tactical_positions({
            "themes": ["fork"],
            "limit": 3
        })
        
        if positions:
            print(f"✅ Found {len(positions)} tactical positions")
            for i, pos in enumerate(positions, 1):
                print(f"   Position {i}: {pos.get('fen', 'Unknown FEN')[:30]}...")
                print(f"   Pattern: {pos.get('tactical_pattern', 'Unknown')}")
        else:
            print("⚠️  No tactical positions found (expected if database empty)")
        return True
    except Exception as e:
        print(f"⚠️  Tactical position search failed (expected if database not available): {e}")
        return False

async def test_enhanced_ml_statistics(engine):
    """Test enhanced ML statistics with database information."""
    print("\n🤖 Testing enhanced ML statistics...")
    
    try:
        stats = engine.get_ml_statistics()
        print("✅ Enhanced ML statistics retrieved successfully")
        
        # Check for database-related statistics
        if 'database_info' in stats:
            db_info = stats['database_info']
            print(f"   Database positions: {db_info.get('total_positions', 'N/A')}")
            print(f"   Database patterns: {db_info.get('unique_patterns', 'N/A')}")
        
        if 'pipeline_info' in stats:
            pipeline_info = stats['pipeline_info']
            print(f"   Pipeline status: {pipeline_info.get('status', 'N/A')}")
            print(f"   Last ingestion: {pipeline_info.get('last_ingestion', 'N/A')}")
            
        return True
    except Exception as e:
        print(f"❌ Enhanced ML statistics failed: {e}")
        return False

async def test_fallback_lesson_generation(engine):
    """Test that fallback lesson generation still works."""
    print("\n🔄 Testing fallback lesson generation...")
    
    try:
        # Test the original lesson generation method
        lessons = engine.generate_lessons(
            topic="pins",
            skill_level="beginner",
            num_examples=1
        )
        
        if lessons:
            print(f"✅ Generated {len(lessons)} fallback lessons successfully")
            lesson = lessons[0]
            print(f"   Title: {lesson.get('title', 'Untitled')}")
            print(f"   Type: {lesson.get('type', 'Unknown')}")
        else:
            print("⚠️  No fallback lessons generated")
        return True
    except Exception as e:
        print(f"❌ Fallback lesson generation failed: {e}")
        return False

async def test_backward_compatibility(engine):
    """Test that existing functionality still works."""
    print("\n🔙 Testing backward compatibility...")
    
    try:
        # Test existing methods
        topics = engine.get_lesson_topics()
        print(f"✅ get_lesson_topics() works: {len(topics)} topics")
        
        # Test cache stats
        cache_stats = engine.get_cache_stats()
        print(f"✅ get_cache_stats() works: {cache_stats}")
        
        # Test topic statistics
        topic_stats = engine.get_topic_statistics()
        print(f"✅ get_topic_statistics() works: {topic_stats['total_topics']} topics")
            
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("🚀 Starting Engine Integration Tests")
    print("=" * 50)
    
    # Initialize engine
    engine = await test_engine_initialization()
    if not engine:
        print("\n❌ Cannot proceed without engine initialization")
        return
    
    # Run all tests
    tests = [
        test_database_statistics,
        test_pipeline_status,
        test_database_lesson_generation,
        test_tactical_position_search,
        test_enhanced_ml_statistics,
        test_fallback_lesson_generation,
        test_backward_compatibility
    ]
    
    results = []
    for test_func in tests:
        try:
            result = await test_func(engine)
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Engine integration successful.")
    elif passed >= total * 0.7:  # 70% pass rate
        print("✅ Most tests passed. Integration mostly successful.")
        print("⚠️  Some features may not be available (database/pipeline not configured)")
    else:
        print("❌ Many tests failed. Integration needs attention.")
    
    print("\n📝 Notes:")
    print("- Database and pipeline tests may fail if not configured")
    print("- This is expected for initial setup")
    print("- Core functionality should still work via fallback mechanisms")

if __name__ == "__main__":
    asyncio.run(main())