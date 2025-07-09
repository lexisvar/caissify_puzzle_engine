#!/usr/bin/env python3
"""
Test script for ML-enhanced lesson generation integration.
"""

import json
import logging
from chess_lesson_engine.unified_engine import ChessLessonEngine
from chess_lesson_engine.tactical_detector import TacticalMoment

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_ml_lesson_integration():
    """Test the ML-enhanced lesson generation integration."""
    print("🚀 Testing ML-Enhanced Lesson Generation Integration")
    print("=" * 70)
    
    # Initialize the unified engine
    print("🔧 Initializing ChessLessonEngine...")
    engine = ChessLessonEngine()
    
    # Check ML capabilities
    print("\n📊 Checking ML Statistics...")
    ml_stats = engine.get_ml_statistics()
    print(f"   ML Enabled: {ml_stats.get('ml_enabled', False)}")
    print(f"   Models Loaded: {ml_stats.get('models_loaded', False)}")
    print(f"   Tactical Detector: {ml_stats.get('tactical_detector_available', False)}")
    print(f"   Lichess Client: {ml_stats.get('lichess_client_available', False)}")
    
    if not ml_stats.get('ml_enabled', False):
        print("❌ ML components not available, testing traditional generation only")
        test_traditional_generation(engine)
        return
    
    # Test 1: Traditional lesson generation (baseline)
    print("\n🎯 Test 1: Traditional Lesson Generation")
    try:
        traditional_lessons = engine.generate_lessons("pins", num_examples=2, skill_level="beginner")
        print(f"   ✅ Generated {len(traditional_lessons)} traditional lessons")
        
        for i, lesson in enumerate(traditional_lessons, 1):
            print(f"   📚 Lesson {i}: {lesson.get('topic', 'Unknown')} "
                  f"(attempts: {lesson.get('generation_attempts', 'N/A')})")
    except Exception as e:
        print(f"   ❌ Traditional generation failed: {e}")
    
    # Test 2: ML-enhanced lesson generation
    print("\n🧠 Test 2: ML-Enhanced Lesson Generation")
    try:
        ml_lessons = engine.generate_ml_lessons(
            topic="pins",
            num_examples=2,
            skill_level="intermediate",
            quality_threshold=0.5
        )
        print(f"   ✅ Generated {len(ml_lessons)} ML-enhanced lessons")
        
        for i, lesson in enumerate(ml_lessons, 1):
            print(f"   🎓 ML Lesson {i}:")
            print(f"      Title: {lesson.get('title', 'N/A')}")
            print(f"      Quality: {lesson.get('quality_score', 0):.2f}")
            print(f"      Complexity: {lesson.get('complexity_score', 0):.2f}")
            print(f"      Themes: {', '.join(lesson.get('tactical_themes', [])[:3])}")
            print(f"      ML Enhanced: {lesson.get('ml_enhanced', False)}")
            
    except Exception as e:
        print(f"   ❌ ML-enhanced generation failed: {e}")
    
    # Test 3: Adaptive recommendations
    print("\n🎯 Test 3: Adaptive Lesson Recommendations")
    try:
        # Test different skill levels
        skill_levels = [0.2, 0.5, 0.8]  # Beginner, Intermediate, Advanced
        
        for skill in skill_levels:
            recommendations = engine.get_adaptive_lesson_recommendations(
                user_skill_level=skill,
                completed_topics=["pins", "forks"],
                preferred_themes=["sacrifice", "mate_threat"]
            )
            
            skill_name = "Beginner" if skill < 0.4 else "Intermediate" if skill < 0.7 else "Advanced"
            print(f"   📈 {skill_name} (skill: {skill}):")
            print(f"      Recommendations: {', '.join(recommendations[:5])}")
            
    except Exception as e:
        print(f"   ❌ Adaptive recommendations failed: {e}")
    
    # Test 4: Synthetic tactical moment processing
    print("\n⚔️  Test 4: Synthetic Tactical Moment Processing")
    try:
        # Create a synthetic tactical moment for testing
        tactical_moment = TacticalMoment(
            game_id="test_game_1",
            move_number=8,
            fen_before="r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/3P1N2/PPP2PPP/RNB1K2R w KQkq - 0 4",
            fen_after="r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/3P1N2/PPP2PPP/RNB1K2R b KQkq - 0 4",
            move_played="Qh5",
            best_move="Qxf7#",
            evaluation_before=50,
            evaluation_after=32000,  # Mate
            evaluation_drop=31950,
            context_moves=["1. e4 e5", "2. Bc4 Nc6", "3. Nf3 Nf6", "4. Qh5"],
            player_to_move="white",
            tactical_theme="mate_threat,sacrifice,queen_move",
            quality_score=0.9,
            difficulty_score=0.7
        )
        
        if engine.ml_lesson_generator:
            enhanced_lesson = engine.ml_lesson_generator.generate_enhanced_lesson(tactical_moment)
            
            if enhanced_lesson:
                print("   ✅ Successfully processed synthetic tactical moment")
                print(f"      Title: {enhanced_lesson.lesson.title}")
                print(f"      Quality: {enhanced_lesson.metadata.quality_score:.2f}")
                print(f"      Themes: {', '.join(enhanced_lesson.metadata.tactical_themes[:3])}")
                print(f"      Steps: {len(enhanced_lesson.lesson.steps)}")
            else:
                print("   ❌ Failed to generate lesson from tactical moment")
        else:
            print("   ⚠️  ML lesson generator not available")
            
    except Exception as e:
        print(f"   ❌ Synthetic tactical moment processing failed: {e}")
    
    # Test 5: Performance comparison
    print("\n⚡ Test 5: Performance Comparison")
    try:
        import time
        
        # Time traditional generation
        start_time = time.time()
        traditional_lessons = engine.generate_lessons("forks", num_examples=1, skill_level="beginner")
        traditional_time = time.time() - start_time
        
        # Time ML generation (if available)
        if engine.ml_enabled:
            start_time = time.time()
            ml_lessons = engine.generate_ml_lessons("forks", num_examples=1, skill_level="beginner")
            ml_time = time.time() - start_time
            
            print(f"   ⏱️  Traditional generation: {traditional_time:.2f}s")
            print(f"   ⏱️  ML-enhanced generation: {ml_time:.2f}s")
            print(f"   📊 Performance ratio: {ml_time/traditional_time:.2f}x")
        else:
            print(f"   ⏱️  Traditional generation: {traditional_time:.2f}s")
            print("   ⚠️  ML generation not available for comparison")
            
    except Exception as e:
        print(f"   ❌ Performance comparison failed: {e}")
    
    # Test 6: Export functionality
    print("\n💾 Test 6: Lesson Export Functionality")
    try:
        if engine.ml_enabled and engine.ml_lesson_generator:
            # Create a simple tactical moment for export testing
            tactical_moment = TacticalMoment(
                game_id="test_game_2",
                move_number=1,
                fen_before="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                fen_after="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
                move_played="e4",
                best_move="e4",
                evaluation_before=0,
                evaluation_after=25,
                evaluation_drop=25,
                context_moves=["1. e4"],
                player_to_move="white",
                tactical_theme="opening,development",
                quality_score=0.3,
                difficulty_score=0.1
            )
            
            enhanced_lesson = engine.ml_lesson_generator.generate_enhanced_lesson(tactical_moment)
            
            if enhanced_lesson:
                export_data = engine.ml_lesson_generator.export_lesson_data(enhanced_lesson)
                print("   ✅ Successfully exported lesson data")
                print(f"      Export keys: {list(export_data.keys())}")
                print(f"      Lesson title: {export_data['lesson']['title']}")
                print(f"      ML prediction confidence: {export_data['ml_prediction']['confidence']:.2f}")
            else:
                print("   ❌ Failed to generate lesson for export")
        else:
            print("   ⚠️  ML components not available for export testing")
            
    except Exception as e:
        print(f"   ❌ Export functionality test failed: {e}")
    
    print(f"\n🎉 ML-Enhanced Lesson Generation Integration Test Complete!")

def test_traditional_generation(engine):
    """Test traditional lesson generation when ML is not available."""
    print("\n🔄 Testing Traditional Generation (ML Fallback)")
    
    try:
        lessons = engine.generate_lessons("pins", num_examples=1, skill_level="beginner")
        print(f"   ✅ Generated {len(lessons)} traditional lessons")
        
        if lessons:
            lesson = lessons[0]
            print(f"   📚 Topic: {lesson.get('topic', 'N/A')}")
            print(f"   🎯 Skill Level: {lesson.get('skill_level', 'N/A')}")
            print(f"   🔄 Attempts: {lesson.get('generation_attempts', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ Traditional generation failed: {e}")

if __name__ == "__main__":
    test_ml_lesson_integration()