#!/usr/bin/env python3
"""Test script for Lichess API integration and tactical detection."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chess_lesson_engine.lichess_client import LichessClient, GameFilters
from chess_lesson_engine.tactical_detector import TacticalDetector
from chess_lesson_engine.logger import get_logger

logger = get_logger(__name__)

def test_lichess_client():
    """Test basic Lichess API functionality."""
    print("🔍 Testing Lichess API Client...")
    
    client = LichessClient()
    
    # Test downloading a specific game
    try:
        print("📥 Testing game download...")
        game_data = client.get_game("5IrD6Gzz", include_analysis=True)
        
        print(f"✅ Successfully downloaded game: {game_data.game_id}")
        print(f"   White: {game_data.white_player} ({game_data.white_rating})")
        print(f"   Black: {game_data.black_player} ({game_data.black_rating})")
        print(f"   Result: {game_data.result}")
        print(f"   Opening: {game_data.opening}")
        print(f"   Has Analysis: {game_data.has_analysis}")
        
        return game_data
        
    except Exception as e:
        print(f"❌ Failed to download game: {e}")
        return None

def test_game_search():
    """Test game search functionality."""
    print("\n🔍 Testing Game Search...")
    
    client = LichessClient()
    
    # Create filters for high-quality games
    filters = GameFilters(
        min_rating=2000,
        max_rating=2800,
        time_control='rapid',
        min_moves=30,
        max_moves=80,
        rated=True,
        analyzed=True
    )
    
    try:
        print("🔎 Searching for games...")
        game_ids = client.get_top_games(filters, max_games=5)
        
        print(f"✅ Found {len(game_ids)} games:")
        for i, game_id in enumerate(game_ids[:3], 1):
            print(f"   {i}. https://lichess.org/{game_id}")
        
        return game_ids
        
    except Exception as e:
        print(f"❌ Failed to search games: {e}")
        return []

def test_tactical_detection(game_data):
    """Test tactical moment detection."""
    print("\n🎯 Testing Tactical Detection...")
    
    if not game_data:
        print("❌ No game data available for tactical detection")
        return
    
    detector = TacticalDetector()
    
    try:
        print(f"🔍 Analyzing game {game_data.game_id} for tactical moments...")
        tactical_moments = detector.analyze_game(game_data)
        
        print(f"✅ Found {len(tactical_moments)} tactical moments:")
        
        for i, moment in enumerate(tactical_moments[:3], 1):
            print(f"\n   {i}. Move {moment.move_number} ({moment.player_to_move} to move)")
            print(f"      Move played: {moment.move_played}")
            print(f"      Best move: {moment.best_move}")
            print(f"      Evaluation drop: {moment.evaluation_drop:.0f}cp")
            print(f"      Quality score: {moment.quality_score:.2f}")
            print(f"      FEN: {moment.fen_before}")
        
        # Get statistics
        stats = detector.get_tactical_statistics(tactical_moments)
        if stats:
            print(f"\n📊 Tactical Statistics:")
            print(f"   Average evaluation drop: {stats['avg_evaluation_drop']:.0f}cp")
            print(f"   High quality moments: {stats['high_quality_moments']}")
            print(f"   Distribution: {stats['move_number_distribution']}")
        
        return tactical_moments
        
    except Exception as e:
        print(f"❌ Failed to detect tactical moments: {e}")
        return []

def test_batch_processing():
    """Test batch processing of multiple games."""
    print("\n⚡ Testing Batch Processing...")
    
    client = LichessClient()
    detector = TacticalDetector()
    
    # Use some known game IDs for testing
    test_game_ids = ["5IrD6Gzz", "QPJcy1Jb", "3r4EhJkF"]
    
    try:
        print(f"📦 Processing {len(test_game_ids)} games...")
        
        total_moments = 0
        for i, game_data in enumerate(client.batch_download_games(test_game_ids), 1):
            print(f"   Processing game {i}/{len(test_game_ids)}: {game_data.game_id}")
            
            moments = detector.analyze_game(game_data)
            total_moments += len(moments)
            
            print(f"   Found {len(moments)} tactical moments")
        
        print(f"✅ Batch processing complete!")
        print(f"   Total tactical moments found: {total_moments}")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")

def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n⏱️  Testing Rate Limiting...")
    
    client = LichessClient()
    
    try:
        print("🔄 Making multiple requests to test rate limiting...")
        
        # Make several requests in succession
        for i in range(3):
            print(f"   Request {i+1}/3...")
            game_data = client.get_game("5IrD6Gzz", include_analysis=False)
            print(f"   ✅ Request {i+1} successful")
        
        # Check rate limiter stats
        stats = client.get_client_stats()
        print(f"📊 Rate Limiter Stats:")
        print(f"   Current delay: {stats['current_delay']:.1f}s")
        print(f"   Consecutive errors: {stats['consecutive_errors']}")
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Lichess Integration Tests\n")
    
    # Test 1: Basic API functionality
    game_data = test_lichess_client()
    
    # Test 2: Game search
    game_ids = test_game_search()
    
    # Test 3: Tactical detection
    if game_data:
        tactical_moments = test_tactical_detection(game_data)
    
    # Test 4: Batch processing
    test_batch_processing()
    
    # Test 5: Rate limiting
    test_rate_limiting()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Next steps:")
    print("   1. Verify tactical moments are being detected correctly")
    print("   2. Test with different types of games (tactical vs positional)")
    print("   3. Implement pattern recognition for specific tactical themes")
    print("   4. Create training data for machine learning models")

if __name__ == "__main__":
    main()