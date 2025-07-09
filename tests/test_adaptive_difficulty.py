#!/usr/bin/env python3
"""
Comprehensive test suite for the Adaptive Difficulty System

This test validates:
1. Difficulty assessment accuracy
2. User skill profile management
3. Personalized lesson recommendations
4. Performance tracking and adaptation
5. Integration with the unified engine
"""

import sys
import os
import time
import chess
import numpy as np
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chess_lesson_engine.adaptive_difficulty import (
    AdaptiveDifficultySystem, DifficultyAssessor, DifficultyMetrics, 
    UserSkillProfile
)
from chess_lesson_engine.tactical_detector import TacticalMoment
from chess_lesson_engine.unified_engine import ChessLessonEngine

def test_difficulty_assessment():
    """Test position difficulty assessment accuracy."""
    print("🎯 Test 1: Position Difficulty Assessment")
    
    assessor = DifficultyAssessor()
    
    # Test positions with known difficulty levels
    test_positions = [
        {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "expected_difficulty": 0.1,  # Starting position - very easy
            "description": "Starting position"
        },
        {
            "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
            "expected_difficulty": 0.4,  # Italian Game - moderate
            "description": "Italian Game opening"
        },
        {
            "fen": "r2q1rk1/ppp2ppp/2n1bn2/2bpp3/3PP3/2N2N2/PPP1BPPP/R1BQ1RK1 w - - 0 9",
            "expected_difficulty": 0.6,  # Complex middlegame
            "description": "Complex middlegame position"
        },
        {
            "fen": "8/8/8/8/8/2k5/2P5/2K5 w - - 0 1",
            "expected_difficulty": 0.8,  # King and pawn endgame - difficult
            "description": "King and pawn endgame"
        }
    ]
    
    results = []
    for test_pos in test_positions:
        position = chess.Board(test_pos["fen"])
        metrics = assessor.assess_position_difficulty(position)
        
        difficulty_error = abs(metrics.overall_difficulty - test_pos["expected_difficulty"])
        results.append({
            "position": test_pos["description"],
            "expected": test_pos["expected_difficulty"],
            "actual": metrics.overall_difficulty,
            "error": difficulty_error,
            "confidence": metrics.confidence
        })
        
        print(f"   📍 {test_pos['description']}: "
              f"Expected {test_pos['expected_difficulty']:.2f}, "
              f"Got {metrics.overall_difficulty:.2f} "
              f"(error: {difficulty_error:.3f}, confidence: {metrics.confidence:.2f})")
    
    average_error = np.mean([r["error"] for r in results])
    average_confidence = np.mean([r["confidence"] for r in results])
    
    print(f"   ✅ Average difficulty error: {average_error:.3f}")
    print(f"   ✅ Average confidence: {average_confidence:.2f}")
    
    return average_error < 0.3  # Accept if average error < 30%

def test_user_skill_profile():
    """Test user skill profile management and updates."""
    print("\n👤 Test 2: User Skill Profile Management")
    
    system = AdaptiveDifficultySystem()
    user_id = "test_user_001"
    
    # Test profile creation
    profile = system.get_user_profile(user_id)
    print(f"   📊 Created profile for {user_id}")
    print(f"      Initial rating: {profile.overall_rating:.2f}")
    print(f"      Initial success rate: {profile.success_rate:.2f}")
    
    # Simulate lesson performance
    performance_data = [
        (True, 45.0, 0.3),   # Easy lesson, correct, 45 seconds
        (True, 60.0, 0.4),   # Medium lesson, correct, 60 seconds
        (False, 120.0, 0.7), # Hard lesson, incorrect, 120 seconds
        (True, 30.0, 0.2),   # Very easy lesson, correct, 30 seconds
        (True, 90.0, 0.6),   # Medium-hard lesson, correct, 90 seconds
    ]
    
    initial_rating = profile.overall_rating
    
    for correct, time_taken, difficulty in performance_data:
        system.update_user_performance(user_id, correct, time_taken, difficulty)
        profile = system.get_user_profile(user_id)
        
        status = "✅ CORRECT" if correct else "❌ WRONG"
        print(f"      {status} - Difficulty: {difficulty:.1f}, "
              f"Time: {time_taken:.0f}s, New Rating: {profile.overall_rating:.3f}")
    
    final_profile = system.get_user_profile(user_id)
    
    print(f"   📈 Performance Summary:")
    print(f"      Total lessons: {final_profile.total_lessons}")
    print(f"      Success rate: {final_profile.success_rate:.2f}")
    print(f"      Recent success rate: {final_profile.get_recent_success_rate():.2f}")
    print(f"      Rating change: {final_profile.overall_rating - initial_rating:+.3f}")
    print(f"      Optimal difficulty: {final_profile.get_optimal_difficulty():.2f}")
    print(f"      Average time: {final_profile.average_time:.1f}s")
    print(f"      Current streak: {final_profile.streak_count}")
    
    # Validate profile updates
    assert final_profile.total_lessons == 5
    assert final_profile.total_correct == 4  # 4 out of 5 correct
    assert 0.0 <= final_profile.overall_rating <= 1.0
    assert 0.0 <= final_profile.success_rate <= 1.0
    
    return True

def test_lesson_recommendations():
    """Test personalized lesson recommendation system."""
    print("\n🎯 Test 3: Personalized Lesson Recommendations")
    
    system = AdaptiveDifficultySystem()
    
    # Create test users with different skill levels
    test_users = [
        {"id": "beginner_user", "skill": 0.2, "description": "Beginner"},
        {"id": "intermediate_user", "skill": 0.5, "description": "Intermediate"},
        {"id": "advanced_user", "skill": 0.8, "description": "Advanced"}
    ]
    
    # Create sample lessons with different difficulties
    available_lessons = []
    topics = ["pins", "forks", "skewers", "discovered_attack", "sacrifice", "mate_threat"]
    difficulties = [0.2, 0.4, 0.6, 0.8]
    
    for topic in topics:
        for difficulty in difficulties:
            available_lessons.append({
                "topic": topic,
                "difficulty": difficulty,
                "themes": [topic],
                "learning_value": 0.7,
                "id": f"{topic}_{difficulty}"
            })
    
    print(f"   📚 Created {len(available_lessons)} sample lessons")
    
    # Test recommendations for each user type
    for user in test_users:
        user_id = user["id"]
        
        # Set up user profile with target skill level
        profile = system.get_user_profile(user_id)
        profile.overall_rating = user["skill"]
        profile.preferred_difficulty = user["skill"]
        
        # Get recommendations
        recommendations = system.recommend_lesson_sequence(
            user_id, available_lessons, count=5
        )
        
        print(f"\n   👤 {user['description']} User (skill: {user['skill']:.1f}):")
        
        recommended_difficulties = []
        for i, lesson in enumerate(recommendations, 1):
            recommended_difficulties.append(lesson["difficulty"])
            print(f"      {i}. {lesson['topic']} (difficulty: {lesson['difficulty']:.1f})")
        
        # Validate recommendations are appropriate for skill level
        avg_difficulty = np.mean(recommended_difficulties)
        difficulty_range = max(recommended_difficulties) - min(recommended_difficulties)
        
        print(f"      📊 Average difficulty: {avg_difficulty:.2f}")
        print(f"      📊 Difficulty range: {difficulty_range:.2f}")
        
        # Check that recommendations are reasonably close to user skill level
        skill_difference = abs(avg_difficulty - user["skill"])
        assert skill_difference < 0.4, f"Recommendations too far from skill level: {skill_difference:.2f}"
    
    return True

def test_adaptive_learning():
    """Test adaptive learning and difficulty adjustment."""
    print("\n🧠 Test 4: Adaptive Learning System")
    
    system = AdaptiveDifficultySystem()
    user_id = "adaptive_learner"
    
    # Start with moderate skill
    profile = system.get_user_profile(user_id)
    profile.overall_rating = 0.5
    profile.preferred_difficulty = 0.5
    
    print(f"   📊 Initial user state:")
    print(f"      Rating: {profile.overall_rating:.2f}")
    print(f"      Preferred difficulty: {profile.preferred_difficulty:.2f}")
    
    # Simulate learning progression
    learning_sessions = [
        # Session 1: Struggling with current difficulty
        [(False, 180.0, 0.5), (False, 200.0, 0.5), (True, 150.0, 0.5)],
        
        # Session 2: System should reduce difficulty
        [(True, 90.0, 0.4), (True, 80.0, 0.4), (True, 70.0, 0.4)],
        
        # Session 3: Doing well, system should increase difficulty
        [(True, 60.0, 0.5), (True, 55.0, 0.5), (True, 50.0, 0.6)],
        
        # Session 4: Ready for harder challenges
        [(True, 80.0, 0.7), (False, 120.0, 0.8), (True, 100.0, 0.7)]
    ]
    
    session_ratings = [profile.overall_rating]
    session_optimal_difficulties = [profile.get_optimal_difficulty()]
    
    for session_num, session_data in enumerate(learning_sessions, 1):
        print(f"\n   📚 Learning Session {session_num}:")
        
        for correct, time_taken, difficulty in session_data:
            system.update_user_performance(user_id, correct, time_taken, difficulty)
            profile = system.get_user_profile(user_id)
            
            status = "✅" if correct else "❌"
            print(f"      {status} Difficulty: {difficulty:.1f}, "
                  f"Time: {time_taken:.0f}s, Rating: {profile.overall_rating:.3f}")
        
        # Check adaptation
        current_optimal = profile.get_optimal_difficulty()
        recent_success = profile.get_recent_success_rate()
        
        session_ratings.append(profile.overall_rating)
        session_optimal_difficulties.append(current_optimal)
        
        print(f"      📈 Session summary:")
        print(f"         Recent success rate: {recent_success:.2f}")
        print(f"         Optimal difficulty: {current_optimal:.2f}")
        print(f"         Overall rating: {profile.overall_rating:.3f}")
    
    # Analyze learning progression
    rating_improvement = session_ratings[-1] - session_ratings[0]
    difficulty_adaptation = session_optimal_difficulties[-1] - session_optimal_difficulties[0]
    
    print(f"\n   📊 Learning Analysis:")
    print(f"      Rating improvement: {rating_improvement:+.3f}")
    print(f"      Difficulty adaptation: {difficulty_adaptation:+.3f}")
    print(f"      Final success rate: {profile.success_rate:.2f}")
    
    # Validate adaptive behavior
    assert rating_improvement > -0.1, "Rating should not decrease significantly"
    assert abs(difficulty_adaptation) > 0.05, "System should adapt difficulty"
    
    return True

def test_engine_integration():
    """Test integration with the unified chess lesson engine."""
    print("\n🔧 Test 5: Engine Integration")
    
    try:
        engine = ChessLessonEngine()
        
        # Test ML statistics
        ml_stats = engine.get_ml_statistics()
        print(f"   📊 ML Statistics:")
        print(f"      ML enabled: {ml_stats.get('ml_enabled', False)}")
        print(f"      Adaptive difficulty available: {ml_stats.get('adaptive_difficulty_available', False)}")
        
        if ml_stats.get('adaptive_difficulty_available'):
            # Test difficulty assessment
            test_fen = "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3"
            difficulty_metrics = engine.assess_lesson_difficulty(test_fen)
            
            print(f"   🎯 Difficulty Assessment:")
            print(f"      Overall difficulty: {difficulty_metrics.overall_difficulty:.3f}")
            print(f"      Confidence: {difficulty_metrics.confidence:.3f}")
            print(f"      Tactical complexity: {difficulty_metrics.tactical_complexity:.3f}")
            
            # Test user profile management
            test_user = "integration_test_user"
            profile_data = engine.get_user_skill_profile(test_user)
            
            print(f"   👤 User Profile:")
            print(f"      User ID: {profile_data['user_id']}")
            print(f"      Overall rating: {profile_data['overall_rating']:.3f}")
            print(f"      ML enabled: {profile_data['ml_enabled']}")
            
            # Test performance update
            engine.update_user_performance(test_user, True, 75.0, 0.6)
            updated_profile = engine.get_user_skill_profile(test_user)
            
            print(f"   📈 After performance update:")
            print(f"      Total lessons: {updated_profile['total_lessons']}")
            print(f"      Success rate: {updated_profile['success_rate']:.3f}")
            
            # Test adaptive recommendations
            recommendations = engine.get_adaptive_lesson_recommendations(test_user, count=3)
            
            print(f"   🎯 Adaptive Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"      {i}. {rec['topic']} (difficulty: {rec.get('difficulty', 'N/A')})")
            
            return True
        else:
            print("   ⚠️  Adaptive difficulty system not available - ML components not loaded")
            return False
            
    except Exception as e:
        print(f"   ❌ Engine integration test failed: {e}")
        return False

def test_performance_benchmarks():
    """Test system performance and scalability."""
    print("\n⚡ Test 6: Performance Benchmarks")
    
    system = AdaptiveDifficultySystem()
    assessor = DifficultyAssessor()
    
    # Test difficulty assessment speed
    test_positions = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4",
        "r2q1rk1/ppp2ppp/2n1bn2/2bpp3/3PP3/2N2N2/PPP1BPPP/R1BQ1RK1 w - - 0 9"
    ]
    
    # Benchmark difficulty assessment
    start_time = time.time()
    assessment_times = []
    
    for fen in test_positions * 10:  # Test 30 positions total
        pos_start = time.time()
        position = chess.Board(fen)
        metrics = assessor.assess_position_difficulty(position)
        pos_time = time.time() - pos_start
        assessment_times.append(pos_time)
    
    total_time = time.time() - start_time
    avg_assessment_time = np.mean(assessment_times)
    
    print(f"   ⏱️  Difficulty Assessment Performance:")
    print(f"      Total positions: {len(assessment_times)}")
    print(f"      Total time: {total_time:.2f}s")
    print(f"      Average time per position: {avg_assessment_time*1000:.1f}ms")
    print(f"      Positions per second: {len(assessment_times)/total_time:.1f}")
    
    # Benchmark user profile operations
    start_time = time.time()
    
    # Create multiple users and simulate activity
    for i in range(100):
        user_id = f"perf_test_user_{i}"
        profile = system.get_user_profile(user_id)
        
        # Simulate some lesson activity
        for j in range(5):
            correct = j % 3 != 0  # 2/3 success rate
            time_taken = 60.0 + (j * 10)
            difficulty = 0.3 + (j * 0.1)
            system.update_user_performance(user_id, correct, time_taken, difficulty)
    
    profile_time = time.time() - start_time
    
    print(f"   ⏱️  User Profile Performance:")
    print(f"      Created 100 users with 5 lessons each")
    print(f"      Total time: {profile_time:.2f}s")
    print(f"      Time per user: {profile_time/100*1000:.1f}ms")
    print(f"      Time per lesson update: {profile_time/500*1000:.1f}ms")
    
    # Get system statistics
    stats = system.get_difficulty_statistics()
    print(f"   📊 System Statistics:")
    print(f"      Total users: {stats['total_users']}")
    print(f"      Average rating: {stats['average_rating']:.3f}")
    print(f"      Average success rate: {stats['average_success_rate']:.3f}")
    print(f"      Total lessons completed: {stats['total_lessons_completed']}")
    
    # Performance validation
    assert avg_assessment_time < 1.0, f"Assessment too slow: {avg_assessment_time:.3f}s"
    assert profile_time/500 < 0.01, f"Profile updates too slow: {profile_time/500:.3f}s per update"
    
    return True

def main():
    """Run all adaptive difficulty system tests."""
    print("🧪 Adaptive Difficulty System - Comprehensive Test Suite")
    print("=" * 70)
    
    tests = [
        ("Difficulty Assessment", test_difficulty_assessment),
        ("User Skill Profiles", test_user_skill_profile),
        ("Lesson Recommendations", test_lesson_recommendations),
        ("Adaptive Learning", test_adaptive_learning),
        ("Engine Integration", test_engine_integration),
        ("Performance Benchmarks", test_performance_benchmarks)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*70}")
            result = test_func()
            results.append((test_name, result, None))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ ERROR in {test_name}: {e}")
    
    # Summary
    total_time = time.time() - start_time
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"🎉 Test Suite Complete!")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Adaptive difficulty system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        for test_name, result, error in results:
            if not result:
                status = "ERROR" if error else "FAILED"
                print(f"   - {test_name}: {status}")
                if error:
                    print(f"     Error: {error}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)