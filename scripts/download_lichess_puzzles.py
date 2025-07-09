#!/usr/bin/env python3
"""
Download and Import Lichess Puzzle Database

This script downloads the complete Lichess puzzle database and imports it
into the ChessTutorAI engine for lesson generation.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import chess_lesson_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

from chess_lesson_engine.puzzle_client import LichessPuzzleClient
from chess_lesson_engine.puzzle_database import PuzzleDatabase

def download_and_import_puzzles(limit=None, min_quality=0.5):
    """
    Download and import Lichess puzzles.
    
    Args:
        limit: Maximum number of puzzles to import (None for all)
        min_quality: Minimum quality score to import (0.0-1.0)
    """
    print("🚀 ChessTutorAI - Lichess Puzzle Database Setup")
    print("=" * 60)
    
    # Initialize components
    print("📚 Initializing puzzle client and database...")
    client = LichessPuzzleClient()
    db = PuzzleDatabase("data/lichess_puzzles.db")  # Separate DB for Lichess puzzles
    
    # Check if zstandard is installed
    try:
        import zstandard
        print("✅ zstandard library found")
    except ImportError:
        print("❌ zstandard library required for compressed files")
        print("📦 Install with: pip install zstandard")
        return False
    
    # Download the database
    print("\n📥 Downloading Lichess puzzle database...")
    print("⏳ This may take several minutes (file is ~500MB compressed)...")
    
    try:
        csv_path = client.download_puzzle_database("data/lichess_puzzles.csv.zst")
        print(f"✅ Downloaded to: {csv_path}")
        
        # Get file size
        file_size_mb = os.path.getsize(csv_path) / (1024 * 1024)
        print(f"📁 File size: {file_size_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False
    
    # Parse and import puzzles
    print(f"\n📊 Parsing and importing puzzles...")
    if limit:
        print(f"🎯 Limiting import to {limit:,} puzzles")
    if min_quality > 0:
        print(f"⭐ Minimum quality score: {min_quality}")
    
    print("⏳ This will take time - processing millions of puzzles...")
    
    start_time = time.time()
    
    try:
        # Parse puzzles with filtering
        puzzles = client.parse_puzzle_csv(csv_path, limit=limit)
        
        # Filter by quality if specified
        if min_quality > 0:
            filtered_puzzles = []
            for puzzle in puzzles:
                if puzzle.quality_score and puzzle.quality_score >= min_quality:
                    filtered_puzzles.append(puzzle)
            puzzles = filtered_puzzles
        
        # Import into database
        imported_count = db.import_puzzles(puzzles, batch_size=1000)
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ Successfully imported {imported_count:,} puzzles!")
        print(f"⏱️  Import time: {elapsed_time/60:.1f} minutes")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Show database statistics
    print("\n📈 Database Statistics:")
    print("-" * 40)
    
    try:
        stats = db.get_puzzle_statistics()
        print(f"📍 Total puzzles: {stats['total_puzzles']:,}")
        print(f"⭐ Average quality: {stats['rating_stats']['avg_quality']:.3f}")
        print(f"🎯 Average rating: {stats['rating_stats']['avg_rating']:.0f}")
        
        print("\n🎯 Top themes:")
        for theme, count in list(stats['top_themes'].items())[:10]:
            print(f"  {theme}: {count:,}")
        
        print("\n📊 Quality distribution:")
        quality_dist = stats['quality_distribution']
        total = sum(quality_dist.values())
        for quality, count in quality_dist.items():
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {quality}: {count:,} ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"⚠️  Could not get statistics: {e}")
    
    print(f"\n🎉 Lichess puzzle database setup complete!")
    print(f"📁 Database location: data/lichess_puzzles.db")
    print(f"🚀 Ready for lesson generation with {imported_count:,} puzzles!")
    
    return True

def main():
    """Main function with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and import Lichess puzzle database")
    parser.add_argument("--limit", type=int, help="Maximum number of puzzles to import")
    parser.add_argument("--min-quality", type=float, default=0.5, 
                       help="Minimum quality score (0.0-1.0, default: 0.5)")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick setup: import 50k high-quality puzzles")
    
    args = parser.parse_args()
    
    # Quick setup option
    if args.quick:
        print("🚀 Quick setup: importing 50,000 high-quality puzzles...")
        limit = 50000
        min_quality = 0.7
    else:
        limit = args.limit
        min_quality = args.min_quality
    
    # Confirm large imports
    if not limit or limit > 100000:
        print("⚠️  You are about to download and import a large puzzle database.")
        print("📊 This will download ~500MB and may take 30+ minutes to process.")
        response = input("🤔 Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled")
            return
    
    # Run the import
    success = download_and_import_puzzles(limit=limit, min_quality=min_quality)
    
    if success:
        print("\n💡 Next steps:")
        print("1. Update your engine to use the new database:")
        print("   engine = create_engine(puzzle_db_path='data/lichess_puzzles.db')")
        print("2. Generate lessons with thousands of puzzle options!")
    else:
        print("\n❌ Setup failed. Check the error messages above.")

if __name__ == "__main__":
    main()