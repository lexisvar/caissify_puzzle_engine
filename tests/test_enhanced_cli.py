#!/usr/bin/env python3
"""Comprehensive test suite for the enhanced CLI tool."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_lesson_generator import main, setup_argument_parser, format_lesson_text


class TestEnhancedCLI(unittest.TestCase):
    """Test suite for enhanced CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = setup_argument_parser()
        self.sample_lesson = {
            'topic': 'forks',
            'skill_level': 'beginner',
            'intro': 'This is a fork lesson.',
            'pgn': '1. e4 e5 2. Nf3 Nc6 3. Bb5',
            'difficulty': 'easy',
            'stockfish_score_start': 0.2,
            'stockfish_score_final': 1.5,
            'generation_attempts': 2
        }
        
        self.sample_database_lesson = {
            **self.sample_lesson,
            'source': 'database',
            'game_info': {
                'white': 'Kasparov, G.',
                'black': 'Karpov, A.',
                'white_rating': 2800,
                'black_rating': 2750,
                'event': 'World Championship'
            }
        }
        
        self.sample_ml_lesson = {
            **self.sample_lesson,
            'ml_features': {
                'confidence': 0.95,
                'predicted_difficulty': 'intermediate'
            }
        }

    def test_argument_parser_setup(self):
        """Test that argument parser is set up correctly."""
        # Test basic arguments
        args = self.parser.parse_args(['forks', '3', 'beginner'])
        self.assertEqual(args.topic, 'forks')
        self.assertEqual(args.num_examples, 3)
        self.assertEqual(args.skill_level, 'beginner')
        
        # Test database mode
        args = self.parser.parse_args(['--database', 'pins', '2', 'advanced'])
        self.assertTrue(args.database)
        self.assertEqual(args.topic, 'pins')
        
        # Test ML enhanced mode
        args = self.parser.parse_args(['--ml-enhanced', 'skewers', '1', 'intermediate'])
        self.assertTrue(args.ml_enhanced)
        
        # Test information commands
        args = self.parser.parse_args(['--database-stats'])
        self.assertTrue(args.database_stats)
        
        args = self.parser.parse_args(['--pipeline-status'])
        self.assertTrue(args.pipeline_status)
        
        # Test position search
        args = self.parser.parse_args(['--search-positions', '--theme', 'fork', '--min-rating', '1500'])
        self.assertTrue(args.search_positions)
        self.assertEqual(args.theme, 'fork')
        self.assertEqual(args.min_rating, 1500)

    def test_format_lesson_text_basic(self):
        """Test basic lesson text formatting."""
        output = format_lesson_text(self.sample_lesson)
        
        self.assertIn('FORKS LESSON', output)
        self.assertIn('Skill Level: Beginner', output)
        self.assertIn('This is a fork lesson.', output)
        self.assertIn('1. e4 e5 2. Nf3 Nc6 3. Bb5', output)
        self.assertIn('Difficulty: Easy', output)
        self.assertIn('Evaluation: 0.2 → 1.5', output)
        self.assertIn('Generated in 2 attempts', output)

    def test_format_lesson_text_database(self):
        """Test database lesson text formatting."""
        output = format_lesson_text(self.sample_database_lesson)
        
        self.assertIn('Source: database', output)
        self.assertIn('Game: Kasparov, G. vs Karpov, A.', output)
        self.assertIn('Ratings: 2800 vs 2750', output)
        self.assertIn('Event: World Championship', output)

    def test_format_lesson_text_ml(self):
        """Test ML lesson text formatting."""
        output = format_lesson_text(self.sample_ml_lesson)
        
        self.assertIn('ML Confidence: 0.95', output)
        self.assertIn('Predicted Difficulty: intermediate', output)

    def test_format_lesson_text_error(self):
        """Test error lesson formatting."""
        error_lesson = {'error': 'Failed to generate lesson'}
        output = format_lesson_text(error_lesson)
        
        self.assertIn('ERROR: Failed to generate lesson', output)

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_list_topics_command(self, mock_engine_class):
        """Test --list-topics command."""
        mock_engine = MagicMock()
        mock_engine.get_lesson_topics.return_value = ['forks', 'pins', 'skewers']
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--list-topics']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_print.assert_any_call('Supported Topics:')
                mock_print.assert_any_call('  - forks')
                mock_print.assert_any_call('  - pins')
                mock_print.assert_any_call('  - skewers')

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_database_stats_command(self, mock_engine_class):
        """Test --database-stats command."""
        mock_engine = MagicMock()
        mock_stats = {
            'total_positions': 1500,
            'themes': {'fork': 300, 'pin': 250},
            'avg_rating': 1800
        }
        mock_engine.get_database_statistics.return_value = mock_stats
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--database-stats']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_print.assert_called()
                # Check that JSON output was printed
                printed_args = [call[0][0] for call in mock_print.call_args_list]
                json_output = next((arg for arg in printed_args if 'total_positions' in str(arg)), None)
                self.assertIsNotNone(json_output)

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_pipeline_status_command(self, mock_engine_class):
        """Test --pipeline-status command."""
        mock_engine = MagicMock()
        mock_status = {
            'status': 'running',
            'last_update': '2024-01-01T12:00:00Z',
            'positions_processed': 1000
        }
        mock_engine.get_pipeline_status.return_value = mock_status
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--pipeline-status']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_print.assert_called()

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_search_positions_command(self, mock_engine_class):
        """Test --search-positions command."""
        mock_engine = MagicMock()
        mock_positions = [
            {
                'theme': 'fork',
                'white_rating': 1600,
                'black_rating': 1550,
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'best_move': 'e4'
            },
            {
                'theme': 'fork',
                'white_rating': 1700,
                'black_rating': 1650,
                'fen': 'rnbqkb1r/pppp1ppp/5n2/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 2 3',
                'best_move': 'd4'
            }
        ]
        mock_engine.search_tactical_positions.return_value = mock_positions
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--search-positions', '--theme', 'fork']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_print.assert_any_call('Found 2 tactical positions:')

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_database_lesson_generation(self, mock_engine_class):
        """Test database lesson generation."""
        mock_engine = MagicMock()
        mock_engine.generate_database_lessons.return_value = [self.sample_database_lesson]
        mock_engine.get_cache_stats.return_value = {'hits': 5, 'misses': 2}
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--database', 'forks', '1', 'beginner']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_engine.generate_database_lessons.assert_called_once_with(
                    topic='forks',
                    num_examples=1,
                    skill_level='beginner'
                )

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_ml_enhanced_lesson_generation(self, mock_engine_class):
        """Test ML-enhanced lesson generation."""
        mock_engine = MagicMock()
        mock_engine.generate_lessons.return_value = [self.sample_ml_lesson]
        mock_engine.get_cache_stats.return_value = {'hits': 5, 'misses': 2}
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--ml-enhanced', 'pins', '1', 'advanced']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_engine.generate_lessons.assert_called_once_with(
                    topic='pins',
                    num_examples=1,
                    skill_level='advanced',
                    use_ml_features=True
                )

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_json_output_format(self, mock_engine_class):
        """Test JSON output format."""
        mock_engine = MagicMock()
        mock_engine.generate_lessons.return_value = [self.sample_lesson]
        mock_engine.get_cache_stats.return_value = {'hits': 5, 'misses': 2}
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', 'forks', '1', 'beginner', '--format', 'json']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                # Check that JSON was printed
                printed_output = mock_print.call_args_list[-1][0][0]
                parsed_json = json.loads(printed_output)
                
                self.assertEqual(parsed_json['topic'], 'forks')
                self.assertEqual(parsed_json['skill_level'], 'beginner')
                self.assertEqual(len(parsed_json['lessons']), 1)

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_output_file_writing(self, mock_engine_class):
        """Test writing output to file."""
        mock_engine = MagicMock()
        mock_engine.generate_lessons.return_value = [self.sample_lesson]
        mock_engine.get_cache_stats.return_value = {'hits': 5, 'misses': 2}
        mock_engine_class.return_value = mock_engine
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('sys.argv', ['enhanced_lesson_generator.py', 'forks', '1', 'beginner', '--output', temp_path]):
                with patch('builtins.print') as mock_print:
                    result = main()
                    
                    self.assertEqual(result, 0)
                    mock_print.assert_any_call(f'Results saved to {temp_path}')
                    
                    # Check file contents
                    with open(temp_path, 'r') as f:
                        content = f.read()
                        self.assertIn('FORKS LESSON', content)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_force_ingestion_command(self, mock_engine_class):
        """Test --force-ingestion command."""
        mock_engine = MagicMock()
        mock_engine.force_pipeline_ingestion.return_value = {'status': 'success', 'processed': 100}
        mock_engine_class.return_value = mock_engine
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', '--force-ingestion']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                self.assertEqual(result, 0)
                mock_print.assert_any_call('Forcing data pipeline ingestion...')
                mock_engine.force_pipeline_ingestion.assert_called_once()

    def test_error_handling_missing_topic(self):
        """Test error handling when topic is missing."""
        with patch('sys.argv', ['enhanced_lesson_generator.py']):
            with patch('builtins.print') as mock_print:
                with patch('sys.stderr'):
                    result = main()
                    
                    self.assertEqual(result, 1)

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_keyboard_interrupt_handling(self, mock_engine_class):
        """Test keyboard interrupt handling."""
        mock_engine_class.side_effect = KeyboardInterrupt()
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', 'forks', '1', 'beginner']):
            with patch('builtins.print') as mock_print:
                with patch('sys.stderr'):
                    result = main()
                    
                    self.assertEqual(result, 1)

    @patch('enhanced_lesson_generator.ChessLessonEngine')
    def test_exception_handling(self, mock_engine_class):
        """Test general exception handling."""
        mock_engine_class.side_effect = Exception("Test error")
        
        with patch('sys.argv', ['enhanced_lesson_generator.py', 'forks', '1', 'beginner']):
            with patch('builtins.print') as mock_print:
                with patch('sys.stderr'):
                    result = main()
                    
                    self.assertEqual(result, 1)


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""
    
    def test_cli_help_output(self):
        """Test that CLI help output includes new features."""
        result = subprocess.run([
            sys.executable, 'enhanced_lesson_generator.py', '--help'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('--database', result.stdout)
        self.assertIn('--ml-enhanced', result.stdout)
        self.assertIn('--database-stats', result.stdout)
        self.assertIn('--pipeline-status', result.stdout)
        self.assertIn('--search-positions', result.stdout)
        self.assertIn('--force-ingestion', result.stdout)

    def test_cli_version_compatibility(self):
        """Test CLI compatibility with different Python versions."""
        # Test that the script can be imported without errors
        try:
            import enhanced_lesson_generator
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import enhanced_lesson_generator: {e}")


def run_performance_benchmarks():
    """Run performance benchmarks for CLI operations."""
    import time
    
    print("\n=== CLI Performance Benchmarks ===")
    
    # Benchmark argument parsing
    start_time = time.time()
    parser = setup_argument_parser()
    for _ in range(1000):
        args = parser.parse_args(['forks', '1', 'beginner'])
    parse_time = time.time() - start_time
    print(f"Argument parsing (1000 iterations): {parse_time:.4f}s")
    
    # Benchmark lesson formatting
    sample_lesson = {
        'topic': 'forks',
        'skill_level': 'beginner',
        'intro': 'This is a test lesson.',
        'pgn': '1. e4 e5 2. Nf3 Nc6',
        'difficulty': 'easy'
    }
    
    start_time = time.time()
    for _ in range(1000):
        output = format_lesson_text(sample_lesson)
    format_time = time.time() - start_time
    print(f"Lesson formatting (1000 iterations): {format_time:.4f}s")
    
    print("=== Benchmarks Complete ===\n")


if __name__ == '__main__':
    # Run performance benchmarks
    run_performance_benchmarks()
    
    # Run unit tests
    unittest.main(verbosity=2)