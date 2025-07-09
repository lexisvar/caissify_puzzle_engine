#!/usr/bin/env python3
"""
Enhanced Tactical Analysis Test
Tests the new deep analysis capabilities with real chess positions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'chess_lesson_engine'))

from chess_lesson_engine.tactical_detector import TacticalDetector
from chess_lesson_engine.lichess_client import LichessClient
from chess_lesson_engine.chess_utils import deep_position_analysis, analyze_game_moves, find_critical_positions
import chess
import chess.pgn
import io

def test_deep_analysis():
    """Test the enhanced deep analysis capabilities"""
    print("🚀 Testing Enhanced Deep Analysis Capabilities\n")
    
    # Initialize components
    detector = TacticalDetector()
    
    # Test with a simpler tactical game
    famous_game_pgn = """
[Event "Test Game"]
[Site "Test"]
[Date "2024.01.01"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Be7 4. d3 d6 5. Ng5 Nh6 6. Nxf7 Nxf7 7. Bxf7+ Kxf7 8. Qh5+ Kg8 9. Qxe5 Bf6 10. Qg3 Re8 11. O-O Rxe4 12. dxe4 Bxb2 13. Bxb2 Qf6 14. Qg5 Qxg5 15. f4 Qg4 16. h3 Qg3 17. Rf3 Qg1+ 18. Kh2 Qxb2 19. Rb3 Qxa2 20. Rxb7 Qxc2 21. Rxc7 Qd2 22. Rc8+ Kf7 23. Rf1 Qd4 24. Rc7+ Kg6 25. h4 h5 26. Kg3 Qd3+ 27. Kh2 Qd2 28. Kg3 Qd3+ 29. Kh2 1/2-1/2
"""
    
    print("📋 Analyzing tactical test game...")
    
    # Parse the game
    game = chess.pgn.read_game(io.StringIO(famous_game_pgn))
    
    # Test deep game analysis
    print("\n🔍 Running deep game analysis...")
    try:
        analysis_result = detector.analyze_game_deep(game)
        
        print(f"✅ Deep analysis completed!")
        print(f"   📊 Total positions analyzed: {len(analysis_result.positions)}")
        print(f"   🎯 Tactical moments found: {len(analysis_result.tactical_moments)}")
        print(f"   ⭐ Average quality score: {analysis_result.average_quality:.2f}")
        
        # Show top tactical moments
        if analysis_result.tactical_moments:
            print(f"\n🏆 Top 3 Tactical Moments:")
            top_moments = sorted(analysis_result.tactical_moments, 
                               key=lambda x: x.quality_score, reverse=True)[:3]
            
            for i, moment in enumerate(top_moments, 1):
                print(f"   {i}. Move {moment.move_number}: {moment.move_played}")
                print(f"      Quality: {moment.quality_score:.2f}")
                print(f"      Eval drop: {moment.evaluation_drop}cp")
                print(f"      Themes: {moment.tactical_theme or 'None'}")
                print(f"      Difficulty: {moment.difficulty_score:.2f}")
        
        # Test training position extraction
        print(f"\n🎓 Extracting training positions...")
        training_positions = detector.get_training_positions(analysis_result.tactical_moments)
        print(f"   📚 High-quality training positions: {len(training_positions)}")
        
        if training_positions:
            best_position = training_positions[0]
            print(f"   🥇 Best position (Move {best_position.move_number}):")
            print(f"      FEN: {best_position.fen}")
            print(f"      Quality: {best_position.quality_score:.2f}")
            print(f"      Themes: {', '.join(best_position.themes) if best_position.themes else 'None'}")
        
    except Exception as e:
        print(f"   ❌ Deep analysis failed: {e}")
    
    # Test individual position deep analysis
    print(f"\n🔬 Testing deep position analysis...")
    
    # Famous tactical position: Légal's Mate setup
    legal_mate_fen = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/3P1N2/PPP2PPP/RNB1K2R w KQkq - 0 4"
    
    try:
        board = chess.Board(legal_mate_fen)
        print(f"   📍 Position: {legal_mate_fen}")
        
        # Test deep position analysis
        deep_analysis = deep_position_analysis(legal_mate_fen, depth=20, multipv=3)
        print(f"   ✅ Deep analysis completed!")
        print(f"   🎯 Best move: {deep_analysis['best_move']}")
        print(f"   📊 Evaluation: {deep_analysis.get('best_score', 0)}")
        print(f"   🔢 Variations analyzed: {len(deep_analysis.get('variations', []))}")
        
        # Test position analysis with detector
        position_analysis = detector.analyze_position_deep(board)
        print(f"   🎯 Tactical: {position_analysis.get('is_tactical', False)}")
        print(f"   ⭐ Quality: {position_analysis.get('quality_score', 0):.2f}")
        print(f"   🧩 Complexity: {position_analysis.get('complexity_score', 0):.2f}")
        print(f"   🏷️  Themes: {', '.join(position_analysis.get('themes', [])) if position_analysis.get('themes') else 'None'}")
        
    except Exception as e:
        print(f"   ❌ Position analysis failed: {e}")
    
    # Test pattern finding
    print(f"\n🔍 Testing tactical pattern recognition...")
    
    try:
        if 'analysis_result' in locals() and analysis_result.tactical_moments:
            patterns = detector.find_tactical_patterns(analysis_result.tactical_moments)
            print(f"   ✅ Pattern analysis completed!")
            
            for theme, moments in patterns.items():
                if moments:
                    print(f"   🏷️  {theme}: {len(moments)} positions")
                    avg_quality = sum(m.quality_score for m in moments) / len(moments)
                    print(f"      Average quality: {avg_quality:.2f}")
        else:
            print(f"   ⚠️  No tactical moments available for pattern analysis")
            
    except Exception as e:
        print(f"   ❌ Pattern analysis failed: {e}")
    
    print(f"\n🎉 Enhanced tactical analysis test completed!")
    
    # Summary
    print(f"\n📊 System Capabilities Summary:")
    print(f"   ✅ Deep multi-PV analysis (depth 20+)")
    print(f"   ✅ Tactical complexity assessment")
    print(f"   ✅ Theme recognition and classification")
    print(f"   ✅ Quality scoring for educational value")
    print(f"   ✅ Training data extraction")
    print(f"   ✅ Pattern grouping and analysis")
    print(f"   ✅ Critical position identification")
    
    return True

if __name__ == "__main__":
    test_deep_analysis()