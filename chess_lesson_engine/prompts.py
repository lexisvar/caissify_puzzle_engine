"""Enhanced prompt templates for OpenAI requests with few-shot examples and chain-of-thought reasoning."""

def lesson_intro_prompt(topic, skill_level=None):
    """Generate an educational explanation of a chess tactic."""
    skill_level = skill_level or 'beginner'
    
    # Few-shot examples for different tactics
    examples = {
        'forks': {
            'beginner': "A fork is when one piece attacks two or more enemy pieces simultaneously. The attacked pieces cannot both escape, so you win material. Look for opportunities when enemy pieces are on the same diagonal, rank, file, or knight's move pattern.",
            'intermediate': "Forks exploit geometric relationships between pieces. Knights create the most common forks due to their unique L-shaped movement. When executing a fork, ensure your attacking piece is protected and calculate if the opponent has any counter-tactics.",
            'advanced': "Advanced fork tactics involve preparatory moves to set up the geometric alignment, sacrificial forks for positional gain, and recognizing fork patterns in complex middlegame positions. Consider the dynamic balance between material gain and positional compensation."
        },
        'pins': {
            'beginner': "A pin occurs when a piece cannot or should not move because it would expose a more valuable piece behind it. The pinned piece becomes restricted and often vulnerable to attack.",
            'intermediate': "Pins create tactical pressure by limiting opponent mobility. Absolute pins (against the king) prevent movement entirely, while relative pins create difficult decisions. Use pins to build pressure before launching attacks.",
            'advanced': "Pin tactics involve creating pin-breaking moves, exploiting pinned pieces with multiple attackers, and using pins in combination with other tactical motifs. Consider the psychological pressure pins create in time-sensitive positions."
        },
        'skewers': {
            'beginner': "A skewer forces a valuable piece to move, exposing a less valuable piece behind it for capture. It's like a reverse pin - the more valuable piece must move first.",
            'intermediate': "Skewers often arise from checks or attacks on high-value pieces. Look for opportunities to create skewers with long-range pieces (bishops, rooks, queens) along open lines.",
            'advanced': "Advanced skewer tactics include deflection sacrifices to create skewer opportunities, using skewers in endgame technique, and recognizing skewer patterns in tactical combinations."
        }
    }
    
    # Get specific example or create generic one
    if topic.lower() in examples and skill_level in examples[topic.lower()]:
        example_text = examples[topic.lower()][skill_level]
    else:
        example_text = f"The {topic} tactic is an important chess concept that every {skill_level} player should understand."
    
    prompt = f"""You are an expert chess coach writing educational content. Create a clear, engaging explanation of the '{topic}' tactic for {skill_level} players.

Structure your explanation as follows:
1. Definition: What is {topic}?
2. Recognition: How to spot {topic} opportunities
3. Execution: How to properly execute {topic}
4. Common patterns: Typical positions where {topic} occurs

Example of good explanation style:
"{example_text}"

Write your explanation in a similar educational tone, being specific about the tactical mechanics while remaining accessible to {skill_level} players. Focus on practical application and pattern recognition."""

    return prompt

def annotated_pgn_prompt(topic, skill_level=None):
    """Generate a realistic chess position demonstrating a specific tactic."""
    skill_level = skill_level or 'beginner'
    
    # Specific examples for different tactics and skill levels
    pgn_examples = {
        'forks': {
            'beginner': '''[Event "Knight Fork Example"]
[FEN "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 1"]

1. Nxe5 { The knight captures the pawn and attacks both the queen and the knight on c6 } Nxe5 
2. d4 { White has won a pawn through the fork } *''',
            'intermediate': '''[Event "Advanced Knight Fork"]
[FEN "r2qkb1r/ppp2ppp/2n1bn2/3pp3/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 0 1"]

1. Nxd5 { Sacrificing the knight to open lines } Nxd5 2. exd5 Nb4 
3. Nxe5 { Now the knight forks the bishop on f6 and attacks the center } *'''
        },
        'pins': {
            'beginner': '''[Event "Simple Pin"]
[FEN "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"]

1. Bg5 { The bishop pins the knight to the queen - the knight cannot move without losing the queen } h6 
2. Bh4 { Maintaining the pin } g5 3. Bg3 { The knight remains pinned and under pressure } *'''
        },
        'skewers': {
            'beginner': '''[Event "Basic Skewer"]
[FEN "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1"]

1. Re8+ { Check forces the king to move } Kh7 2. Re7 { Now the rook attacks the pawns on the back rank } *'''
        }
    }
    
    # Get example or create generic prompt
    if topic.lower() in pgn_examples and skill_level in pgn_examples[topic.lower()]:
        example_pgn = pgn_examples[topic.lower()][skill_level]
        example_instruction = f"Here's an example of the format I want:\n\n{example_pgn}\n\n"
    else:
        example_instruction = ""
    
    prompt = f"""Create a realistic chess position that clearly demonstrates the '{topic}' tactic, appropriate for {skill_level} players.

Requirements:
1. Use proper PGN format with headers
2. Include a FEN if starting from a non-standard position
3. Add clear, educational comments explaining each key move
4. Keep the example concise (3-6 moves maximum)
5. Make it realistic - something that could occur in actual games
6. Ensure the tactic is the main point of the position

{example_instruction}Now create a similar example for '{topic}' at {skill_level} level. Focus on clarity and educational value. Output only the PGN with comments."""

    return prompt

def get_tactic_specific_validation_prompt(topic, pgn, skill_level=None):
    """Generate a prompt to validate if a PGN properly demonstrates the requested tactic."""
    return f"""Analyze this chess position and determine if it clearly demonstrates the '{topic}' tactic:

{pgn}

Answer with YES or NO, followed by a brief explanation:
- Does this position clearly show the {topic} tactic?
- Is the tactical motif the main point of the position?
- Is it appropriate for {skill_level or 'beginner'} level?
- Are there any issues with the chess notation or moves?

Format: YES/NO - [explanation]"""

def get_difficulty_assessment_prompt(pgn, topic):
    """Generate a prompt to assess the difficulty of a chess position."""
    return f"""Assess the difficulty level of this chess position showing the '{topic}' tactic:

{pgn}

Consider:
1. How obvious is the tactic?
2. How many candidate moves must be calculated?
3. Are there defensive resources for the opponent?
4. How complex is the resulting position?

Rate as: BEGINNER, INTERMEDIATE, or ADVANCED
Provide reasoning for your assessment."""
