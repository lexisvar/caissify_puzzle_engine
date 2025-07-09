"""Helpers for PGN generation and validation using python-chess."""

import chess
import chess.engine
import chess.pgn
import io
import re
import os
from .config import config
from .logger import get_logger
from .cache import position_cache

logger = get_logger(__name__)

def validate_pgn(pgn_str):
    """Validate a PGN string. Returns True if valid, else False."""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_str))
        return game is not None
    except Exception:
        return False

def pgn_to_dict(pgn_str):
    """Convert a PGN string to a dict with moves and comments."""
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    moves = []
    node = game
    while node.variations:
        next_node = node.variation(0)
        move_san = node.board().san(next_node.move)
        comment = next_node.comment
        moves.append({"move": move_san, "comment": comment})
        node = next_node
    return {"moves": moves, "headers": dict(game.headers)}

def check_stockfish_available():
    """Check if Stockfish binary exists and is executable."""
    stockfish_path = config.get('stockfish.path')
    if not os.path.isfile(stockfish_path):
        raise FileNotFoundError(f"Stockfish binary not found at {stockfish_path}")
    if not os.access(stockfish_path, os.X_OK):
        raise PermissionError(f"Stockfish binary at {stockfish_path} is not executable")
    logger.debug(f"Stockfish available at {stockfish_path}")

def evaluate_position(fen, time_limit=None, min_depth=None, multipv=None):
    """Evaluate a position using Stockfish with caching. Returns (score, mate, info)."""
    # Use config defaults if not specified
    time_limit = time_limit or config.get('stockfish.time_limit', 3.0)
    min_depth = min_depth or config.get('stockfish.min_depth', 25)
    multipv = multipv or config.get('stockfish.multipv', 3)
    
    # Check cache first
    cached_result = position_cache.get(fen, time_limit, min_depth, multipv)
    if cached_result is not None:
        return cached_result
    
    # Validate inputs
    check_stockfish_available()
    board = chess.Board(fen)
    if not board.is_valid():
        logger.error(f"Invalid FEN provided: {fen}")
        raise ValueError(f"Illegal FEN: {fen}")
    
    stockfish_path = config.get('stockfish.path')
    logger.debug(f"Evaluating position: {fen[:30]}... (time={time_limit}s, depth={min_depth}, multipv={multipv})")
    
    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            info = engine.analyse(
                board,
                chess.engine.Limit(time=time_limit, depth=min_depth),
                multipv=multipv
            )
            
            # Process results
            if isinstance(info, list):
                # Prefer the shortest mate found
                mate_scores = [(i["score"].white().mate(), i) for i in info if i["score"].is_mate()]
                if mate_scores:
                    mate, best_info = min(mate_scores, key=lambda x: abs(x[0]))
                    score = best_info["score"].white().score(mate_score=10000)
                    result = (score, mate, best_info)
                    logger.debug(f"Found mate in {mate} moves")
                else:
                    # Use the first line
                    info = info[0]
                    score = info["score"].white().score(mate_score=10000)
                    mate = info["score"].white().mate()
                    result = (score, mate, info)
            else:
                score = info["score"].white().score(mate_score=10000)
                mate = info["score"].white().mate()
                result = (score, mate, info)
            
            # Cache the result
            position_cache.set(fen, time_limit, min_depth, multipv, result[0], result[1], result[2])
            logger.debug(f"Position evaluation: score={result[0]}, mate={result[1]}")
            
            return result
            
    except Exception as e:
        logger.error(f"Stockfish evaluation failed for FEN {fen}: {e}")
        raise

def estimate_difficulty(score, info, fen=None):
    """Estimate difficulty based on Stockfish evaluation, mate, and position. Handles both mate and 'winning' studies."""
    import chess
    # If the final position is checkmate, use additional heuristics
    if fen:
        board = chess.Board(fen)
        if board.is_checkmate():
            return "beginner"
    
    # Handle different info formats - could be dict with 'score' key or direct score object
    score_obj = None
    if isinstance(info, dict) and "score" in info:
        score_obj = info["score"]
    elif hasattr(info, 'is_mate'):
        score_obj = info
    else:
        # Fallback: use score value directly for difficulty estimation
        logger.warning(f"Unexpected info format in estimate_difficulty: {type(info)}")
        if abs(score) > 1000:
            return "beginner"
        elif 500 < abs(score) <= 1000:
            return "intermediate"
        elif 200 < abs(score) <= 500:
            return "intermediate"
        else:
            return "advanced"
    
    if score_obj and score_obj.is_mate():
        mate_in = score_obj.white().mate()
        if mate_in is not None:
            if abs(mate_in) == 1:
                if abs(score) > 500:
                    return "beginner"
                else:
                    return "intermediate"
            elif abs(mate_in) == 2:
                return "intermediate"
            else:
                return "advanced"
        return "advanced"
    # Heuristics for 'winning' studies (no mate, but decisive advantage)
    if abs(score) > 1000:
        # If only one move gives a decisive advantage, it's harder
        # (Try to detect if the solution is unique)
        try:
            board = chess.Board(fen) if fen else None
            if board:
                legal_moves = list(board.legal_moves)
                winning_moves = 0
                for move in legal_moves:
                    board.push(move)
                    mv_score, mv_mate, _ = evaluate_position(board.fen(), time_limit=1.0, min_depth=10, multipv=1)
                    board.pop()
                    if mv_score is not None and mv_score > 1000:
                        winning_moves += 1
                if winning_moves == 1:
                    return "advanced"
                elif winning_moves <= 3:
                    return "intermediate"
                else:
                    return "beginner"
        except Exception:
            pass
        return "beginner"
    if 500 < abs(score) <= 1000:
        return "intermediate"
    if 200 < abs(score) <= 500:
        return "intermediate"
    return "advanced"

def strip_pgn_variations_and_nags(pgn_str):
    """Remove variations (in parentheses) and NAGs (like $10) from PGN."""
    # Remove NAGs
    pgn_str = re.sub(r'\$\d+', '', pgn_str)
    # Remove nested parentheses (variations)
    while re.search(r'\([^()]*\)', pgn_str):
        pgn_str = re.sub(r'\([^()]*\)', '', pgn_str)
    return pgn_str

def strip_pgn_to_main_line(pgn_str):
    """Remove all comments, NAGs, and variations, keeping only the main line of moves and headers."""
    import re
    # Remove comments {...}
    pgn_str = re.sub(r'\{[^}]*\}', '', pgn_str)
    # Remove NAGs ($...)
    pgn_str = re.sub(r'\$\d+', '', pgn_str)
    # Remove variations ( ... )
    depth = 0
    result = []
    for c in pgn_str:
        if c == '(':
            depth += 1
        elif c == ')':
            depth = max(0, depth - 1)
        elif depth == 0:
            result.append(c)
    pgn_str = ''.join(result)
    # Remove extra whitespace
    pgn_str = re.sub(r'\s+', ' ', pgn_str)
    # Restore newlines for headers
    pgn_str = re.sub(r'(\[\w]+ ")', r'\n\1', pgn_str)
    return pgn_str.strip()

def extract_main_line_moves(pgn_str):
    """Remove all comments, NAGs, and variations, keeping only the main line of moves and headers."""
    import re
    # 1. Remove comments {...}, NAGs ($...), and variations ( ... )
    pgn_str = re.sub(r'\{[^}]*\}', '', pgn_str)
    pgn_str = re.sub(r'\$\d+', '', pgn_str)
    # Remove all nested parentheses (variations)
    while re.search(r'\([^()]*\)', pgn_str):
        pgn_str = re.sub(r'\([^()]*\)', '', pgn_str)

    # 2. Split headers and moves
    lines = pgn_str.strip().splitlines()
    header_lines = [line for line in lines if line.strip().startswith('[')]
    # Moves are everything after the last header line
    moves_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('['):
            moves_start = i + 1
    move_lines = lines[moves_start:]
    move_str = ' '.join(move_lines).strip()

    # 3. Clean move text: only strip trailing +, #, !, ? from move tokens
    def clean_token(token):
        # If token looks like a move (contains a letter or number, not a header or result)
        if re.match(r'^[a-hRNBQKO0-9=/]+[+#?!]*$', token):
            return re.sub(r'[+#?!]+$', '', token)
        return token
    tokens = move_str.split()
    tokens = [clean_token(tok) for tok in tokens]
    cleaned_moves = ' '.join(tokens)

    # 4. Reconstruct PGN: headers on separate lines, blank line, then moves
    pgn_str = '\n'.join(header_lines) + '\n\n' + cleaned_moves
    return pgn_str.strip()

def analyze_lesson_pgn(pgn_str, lesson_name=None, debug=False):
    """Analyze a PGN, estimate its level, and return lesson info. Evaluates both starting and final positions for studies/puzzles."""
    import chess.pgn
    import io
    import re
    
    logger.info(f"Analyzing PGN lesson: {lesson_name or 'unnamed'}")
    
    try:
        clean_pgn = extract_main_line_moves(pgn_str)
        logger.debug(f"Cleaned PGN for {lesson_name}: {clean_pgn[:100]}...")
        
        # Extract FEN header if present
        fen_match = re.search(r'\[FEN "([^"]+)"\]', clean_pgn)
        starting_fen = fen_match.group(1) if fen_match else chess.STARTING_FEN
        logger.debug(f"Starting FEN: {starting_fen}")
        
        # Evaluate the starting position
        score_start, mate_start, info_start = evaluate_position(starting_fen)
        
        # Play out the main line to get the final position
        game = chess.pgn.read_game(io.StringIO(clean_pgn))
        if game is None:
            logger.error(f"Could not parse PGN for lesson {lesson_name}")
            return {"error": "Could not parse PGN.", "lesson_name": lesson_name, "cleaned_pgn": clean_pgn}
        
        board = chess.Board(starting_fen)
        node = game
        move_num = 1
        
        # Play out all moves in the main line
        while node.variations:
            next_node = node.variation(0)
            move = next_node.move
            if move is not None:
                try:
                    board.push(move)
                    logger.debug(f"Applied move {move_num}: {board.san(move)}")
                except Exception as e:
                    logger.warning(f"Move application failed at move {move_num}: {move} ({e})")
                    break
            node = next_node
            move_num += 1
        
        final_fen = board.fen()
        logger.debug(f"Final FEN: {final_fen}")
        
        # Evaluate the final position
        score_final, mate_final, info_final = evaluate_position(final_fen)
        
        # Estimate difficulty based on starting position
        difficulty = estimate_difficulty(score_start, info_start, fen=starting_fen)
        
        logger.info(f"Analysis complete for {lesson_name}: difficulty={difficulty}, "
                   f"start_score={score_start}, final_score={score_final}")
        
        return {
            "lesson_name": lesson_name,
            "pgn": pgn_str,
            "cleaned_pgn": clean_pgn,
            "start_fen": starting_fen,
            "final_fen": final_fen,
            "stockfish_score_start": score_start,
            "mate_start": mate_start,
            "stockfish_score_final": score_final,
            "mate_final": mate_final,
            "difficulty": difficulty
        }
        
    except Exception as e:
        logger.error(f"Exception analyzing PGN for lesson {lesson_name}: {e}", exc_info=True)
        return {"error": str(e), "lesson_name": lesson_name}

def deep_position_analysis(fen, depth=20, multipv=5, time_limit=10.0):
    """
    Perform deep analysis of a position with multiple principal variations.
    Returns detailed analysis including all variations and their evaluations.
    """
    check_stockfish_available()
    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError(f"Invalid FEN: {fen}")
    
    stockfish_path = config.get('stockfish.path')
    logger.debug(f"Deep analysis of position: {fen[:30]}... (depth={depth}, multipv={multipv})")
    
    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            # Configure engine for deep analysis
            engine.configure({"Hash": 256, "Threads": 2})
            
            info = engine.analyse(
                board,
                chess.engine.Limit(depth=depth, time=time_limit),
                multipv=multipv
            )
            
            variations = []
            for i, line in enumerate(info):
                score = line["score"].white().score(mate_score=10000)
                mate = line["score"].white().mate()
                pv = line.get("pv", [])
                
                # Convert moves to SAN notation
                temp_board = board.copy()
                san_moves = []
                for move in pv[:10]:  # Limit to first 10 moves
                    try:
                        san_moves.append(temp_board.san(move))
                        temp_board.push(move)
                    except:
                        break
                
                variations.append({
                    "rank": i + 1,
                    "score": score,
                    "mate": mate,
                    "depth": line.get("depth", 0),
                    "nodes": line.get("nodes", 0),
                    "pv": pv,
                    "san_moves": san_moves,
                    "line": " ".join(san_moves)
                })
            
            logger.debug(f"Deep analysis complete: {len(variations)} variations found")
            return {
                "fen": fen,
                "depth": depth,
                "multipv": multipv,
                "variations": variations,
                "best_move": variations[0]["san_moves"][0] if variations and variations[0]["san_moves"] else None,
                "best_score": variations[0]["score"] if variations else None,
                "is_tactical": is_position_tactical_deep(variations)
            }
            
    except Exception as e:
        logger.error(f"Deep analysis failed for FEN {fen}: {e}")
        raise

def analyze_game_moves(pgn_str, depth=15, time_per_move=2.0):
    """
    Analyze all moves in a game, tracking evaluation changes.
    Returns move-by-move analysis with evaluation drops and tactical moments.
    """
    logger.info("Starting game move analysis")
    
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_str))
        if not game:
            raise ValueError("Could not parse PGN")
        
        # Get starting position
        fen_header = game.headers.get("FEN")
        board = chess.Board(fen_header) if fen_header else chess.Board()
        
        move_analyses = []
        node = game
        move_number = 1
        previous_eval = None
        
        while node.variations:
            next_node = node.variation(0)
            move = next_node.move
            
            if move:
                # Analyze position before move
                pre_move_fen = board.fen()
                pre_analysis = deep_position_analysis(
                    pre_move_fen,
                    depth=depth,
                    multipv=3,
                    time_limit=time_per_move
                )
                
                # Make the move
                san_move = board.san(move)
                board.push(move)
                
                # Analyze position after move
                post_move_fen = board.fen()
                post_analysis = deep_position_analysis(
                    post_move_fen,
                    depth=depth,
                    multipv=3,
                    time_limit=time_per_move
                )
                
                # Calculate evaluation change
                pre_score = pre_analysis["best_score"] or 0
                post_score = -(post_analysis["best_score"] or 0)  # Flip for opponent
                eval_change = post_score - pre_score
                
                # Detect blunders and tactical moments
                is_blunder = eval_change < -200  # Lost 2+ pawns
                is_tactical = pre_analysis["is_tactical"] or post_analysis["is_tactical"]
                
                move_analysis = {
                    "move_number": move_number,
                    "move": san_move,
                    "pre_fen": pre_move_fen,
                    "post_fen": post_move_fen,
                    "pre_score": pre_score,
                    "post_score": -post_score,  # From current player's perspective
                    "eval_change": eval_change,
                    "is_blunder": is_blunder,
                    "is_tactical": is_tactical,
                    "pre_analysis": pre_analysis,
                    "post_analysis": post_analysis
                }
                
                move_analyses.append(move_analysis)
                logger.debug(f"Move {move_number}: {san_move}, eval change: {eval_change:+.0f}cp")
                
                previous_eval = -post_score
                move_number += 1
            
            node = next_node
        
        logger.info(f"Game analysis complete: {len(move_analyses)} moves analyzed")
        return {
            "pgn": pgn_str,
            "moves": move_analyses,
            "total_moves": len(move_analyses),
            "blunders": [m for m in move_analyses if m["is_blunder"]],
            "tactical_moments": [m for m in move_analyses if m["is_tactical"]]
        }
        
    except Exception as e:
        logger.error(f"Game move analysis failed: {e}")
        raise

def is_position_tactical_deep(variations):
    """
    Determine if a position is tactical based on deep analysis variations.
    A position is tactical if there are significant evaluation differences
    between the best moves or if tactical themes are present.
    """
    if not variations or len(variations) < 2:
        return False
    
    best_score = variations[0]["score"] or 0
    second_score = variations[1]["score"] or 0
    
    # Large gap between best and second best move suggests tactics
    score_gap = abs(best_score - second_score)
    if score_gap > 150:  # 1.5 pawn advantage difference
        return True
    
    # Check for forcing moves (checks, captures, threats)
    for var in variations[:3]:
        if var["san_moves"]:
            first_move = var["san_moves"][0]
            # Check for tactical indicators
            if any(indicator in first_move for indicator in ['+', '#', 'x', '=']):
                return True
    
    # Check for mate threats
    for var in variations[:2]:
        if var["mate"] is not None and abs(var["mate"]) <= 3:
            return True
    
    return False

def find_critical_positions(game_analysis, eval_threshold=200):
    """
    Find critical positions in a game where evaluation changed significantly.
    These are candidates for tactical lessons.
    """
    critical_positions = []
    
    for move in game_analysis["moves"]:
        if abs(move["eval_change"]) >= eval_threshold:
            # This is a critical moment
            critical_positions.append({
                "move_number": move["move_number"],
                "move": move["move"],
                "fen": move["pre_fen"],  # Position before the critical move
                "eval_change": move["eval_change"],
                "is_blunder": move["is_blunder"],
                "is_tactical": move["is_tactical"],
                "best_continuation": move["pre_analysis"]["variations"][0]["line"],
                "analysis": move["pre_analysis"]
            })
    
    # Sort by evaluation change magnitude
    critical_positions.sort(key=lambda x: abs(x["eval_change"]), reverse=True)
    
    logger.info(f"Found {len(critical_positions)} critical positions")
    return critical_positions

def evaluate_tactical_complexity(position_analysis):
    """
    Evaluate the tactical complexity of a position based on deep analysis.
    Returns a complexity score and classification.
    """
    variations = position_analysis["variations"]
    if not variations:
        return {"score": 0, "level": "simple"}
    
    complexity_score = 0
    
    # Factor 1: Number of reasonable moves
    reasonable_moves = len([v for v in variations if abs(v["score"] - variations[0]["score"]) < 100])
    complexity_score += min(reasonable_moves * 10, 50)
    
    # Factor 2: Depth of best variation
    if variations[0]["san_moves"]:
        variation_depth = len(variations[0]["san_moves"])
        complexity_score += min(variation_depth * 5, 30)
    
    # Factor 3: Presence of forcing moves
    forcing_moves = sum(1 for v in variations[:3]
                       if v["san_moves"] and any(ind in v["san_moves"][0]
                                               for ind in ['+', '#', 'x']))
    complexity_score += forcing_moves * 15
    
    # Factor 4: Evaluation spread
    if len(variations) >= 2:
        eval_spread = abs(variations[0]["score"] - variations[-1]["score"])
        complexity_score += min(eval_spread / 10, 25)
    
    # Classify complexity level
    if complexity_score < 30:
        level = "simple"
    elif complexity_score < 60:
        level = "moderate"
    elif complexity_score < 90:
        level = "complex"
    else:
        level = "very_complex"
    
    return {
        "score": complexity_score,
        "level": level,
        "reasonable_moves": reasonable_moves,
        "forcing_moves": forcing_moves,
        "variation_depth": len(variations[0]["san_moves"]) if variations[0]["san_moves"] else 0
    }

def get_position_themes(position_analysis):
    """
    Identify tactical themes present in a position based on deep analysis.
    """
    themes = []
    variations = position_analysis["variations"]
    
    if not variations:
        return themes
    
    # Analyze the best variations for tactical patterns
    for var in variations[:3]:
        if not var["san_moves"]:
            continue
            
        moves = var["san_moves"]
        
        # Check for common tactical themes
        if any('+' in move for move in moves[:2]):
            themes.append("check")
        
        if any('#' in move for move in moves[:3]):
            themes.append("checkmate")
        
        if any('x' in move for move in moves[:2]):
            themes.append("capture")
        
        if any('=' in move for move in moves[:3]):
            themes.append("promotion")
        
        # Look for piece patterns
        if any(move.startswith('Q') for move in moves[:2]):
            themes.append("queen_move")
        
        if any(move.startswith('R') for move in moves[:2]):
            themes.append("rook_move")
        
        # Check for sacrificial patterns (material loss with compensation)
        if var["score"] > 200 and any('x' in move for move in moves[:1]):
            themes.append("sacrifice")
    
    # Check for mate threats
    if any(var["mate"] is not None and abs(var["mate"]) <= 3 for var in variations[:2]):
        themes.append("mate_threat")
    
    # Remove duplicates and return
    return list(set(themes))
