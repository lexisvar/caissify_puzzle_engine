"""
Content Generator for ChessTutorAI lesson generation engine.
Uses AI providers to generate educational chess content.
"""

import os
from typing import List, Dict, Optional
from .models import (
    PuzzleExample, LessonGenerationConfig, DifficultyLevel, StepType,
    get_theme_info, ThemeInfo
)
from .logger import get_logger

# Simple AI client replacement
class SimpleAIClient:
    """Simple AI client for OpenAI integration."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    def get_available_providers(self):
        """Check if OpenAI is available."""
        return ["openai"] if self.api_key else []
    
    def get_completion(self, prompt: str, provider: str = "openai",
                      temperature: float = 0.7, max_tokens: int = 800) -> str:
        """Get completion from OpenAI."""
        if not self.api_key:
            return "OpenAI API key not configured."
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            return "OpenAI library not installed."
        except Exception as e:
            return f"AI generation error: {str(e)}"

# Global AI client instance
ai_client = SimpleAIClient()

logger = get_logger(__name__)


class ContentGenerator:
    """Generates educational content using AI providers."""
    
    def __init__(self, ai_provider: str = "openai"):
        """Initialize the content generator."""
        self.ai_provider = ai_provider
        self._initialize_templates()
        logger.info(f"Content generator initialized with provider: {ai_provider}")
    
    def _initialize_templates(self):
        """Initialize content templates for different lesson components."""
        self.templates = {
            'introduction': {
                'beginner': """
Create a beginner-friendly introduction to {theme_display_name}.

Theme: {theme_display_name}
Description: {theme_description}
Key Concepts: {key_concepts}
Difficulty: Beginner
Example Count: {example_count}
Average Rating: {avg_rating}

Write a clear, encouraging introduction that:
1. Explains what {theme_display_name} is in simple terms
2. Why it's important in chess
3. What students will learn in this lesson
4. Encourages practice and patience

Keep the language simple and motivating. Use around 150-200 words.
""",
                'intermediate': """
Create an intermediate-level introduction to {theme_display_name}.

Theme: {theme_display_name}
Description: {theme_description}
Key Concepts: {key_concepts}
Difficulty: Intermediate
Example Count: {example_count}
Average Rating: {avg_rating}

Write a comprehensive introduction that:
1. Explains the tactical concept and its variations
2. Discusses when and how to look for these opportunities
3. Mentions common patterns and setups
4. Sets expectations for the lesson content

Use chess terminology appropriately. Use around 200-250 words.
""",
                'advanced': """
Create an advanced introduction to {theme_display_name}.

Theme: {theme_display_name}
Description: {theme_description}
Key Concepts: {key_concepts}
Difficulty: Advanced
Example Count: {example_count}
Average Rating: {avg_rating}

Write a sophisticated introduction that:
1. Explores the deeper strategic implications
2. Discusses positional requirements and setups
3. Mentions psychological aspects and practical considerations
4. Connects to broader chess understanding

Assume strong chess knowledge. Use around 250-300 words.
""",
                'expert': """
Create an expert-level introduction to {theme_display_name}.

Theme: {theme_display_name}
Description: {theme_description}
Key Concepts: {key_concepts}
Difficulty: Expert
Example Count: {example_count}
Average Rating: {avg_rating}

Write a masterful introduction that:
1. Analyzes the concept from multiple perspectives
2. Discusses rare variations and exceptional cases
3. Explores connections to opening theory and endgames
4. Provides insights for competitive play

Use advanced chess terminology and concepts. Use around 300-350 words.
"""
            },
            
            'example_analysis': {
                'beginner': """
Analyze this chess puzzle for a beginner student.

Position: {fen}
Theme: {theme_display_name}
Solution: {solution_moves}
Rating: {rating}
Puzzle Themes: {themes}

Provide a clear analysis that:
1. Describes what to look for in the position
2. Explains the key tactical idea step by step
3. Shows why the solution works
4. Points out what makes this a good example of {theme_display_name}

Use simple language and explain each move clearly. Around 100-150 words.
""",
                'intermediate': """
Analyze this chess puzzle for an intermediate student.

Position: {fen}
Theme: {theme_display_name}
Solution: {solution_moves}
Rating: {rating}
Puzzle Themes: {themes}

Provide a thorough analysis that:
1. Identifies the key features of the position
2. Explains the tactical motif and execution
3. Discusses alternative moves and why they fail
4. Highlights the learning points

Use appropriate chess notation and terminology. Around 150-200 words.
""",
                'advanced': """
Analyze this chess puzzle for an advanced student.

Position: {fen}
Theme: {theme_display_name}
Solution: {solution_moves}
Rating: {rating}
Puzzle Themes: {themes}

Provide a deep analysis that:
1. Examines the positional factors that enable the tactic
2. Analyzes the calculation required
3. Discusses defensive resources and refutations
4. Connects to similar patterns and themes

Assume strong analytical skills. Around 200-250 words.
""",
                'expert': """
Analyze this chess puzzle for an expert student.

Position: {fen}
Theme: {theme_display_name}
Solution: {solution_moves}
Rating: {rating}
Puzzle Themes: {themes}

Provide a masterful analysis that:
1. Explores all critical variations
2. Discusses the precise move order requirements
3. Analyzes psychological and practical aspects
4. Provides insights for similar positions

Use advanced analysis and precise evaluation. Around 250-300 words.
"""
            },
            
            'summary': {
                'beginner': """
Create a lesson summary for beginner students.

Theme: {theme_display_name}
Examples Covered: {example_count}
Key Concepts: {key_concepts}

Write a helpful summary that:
1. Reviews the main points learned
2. Provides simple tips for recognizing {theme_display_name}
3. Suggests how to practice these patterns
4. Encourages continued learning

Keep it encouraging and practical. Around 150-200 words.
""",
                'intermediate': """
Create a lesson summary for intermediate students.

Theme: {theme_display_name}
Examples Covered: {example_count}
Key Concepts: {key_concepts}

Write a comprehensive summary that:
1. Synthesizes the key learning points
2. Provides practical advice for game application
3. Suggests training methods and exercises
4. Connects to broader tactical understanding

Use clear, actionable advice. Around 200-250 words.
""",
                'advanced': """
Create a lesson summary for advanced students.

Theme: {theme_display_name}
Examples Covered: {example_count}
Key Concepts: {key_concepts}

Write a sophisticated summary that:
1. Distills the essential principles
2. Discusses practical application in competitive play
3. Suggests advanced training approaches
4. Provides insights for teaching others

Assume deep chess understanding. Around 250-300 words.
""",
                'expert': """
Create a lesson summary for expert students.

Theme: {theme_display_name}
Examples Covered: {example_count}
Key Concepts: {key_concepts}

Write a masterful summary that:
1. Provides deep insights and principles
2. Discusses cutting-edge understanding
3. Suggests research and analysis directions
4. Connects to the highest level of play

Use advanced concepts and terminology. Around 300-350 words.
"""
            }
        }
    
    def generate_introduction(self, theme: str, difficulty: DifficultyLevel, 
                            examples: List[PuzzleExample]) -> str:
        """Generate lesson introduction content."""
        try:
            theme_info = get_theme_info(theme)
            
            # Calculate example statistics
            avg_rating = sum(ex.rating for ex in examples) / len(examples) if examples else 1500
            
            # Get appropriate template
            difficulty_key = difficulty.value
            template = self.templates['introduction'].get(
                difficulty_key, 
                self.templates['introduction']['intermediate']
            )
            
            # Format template with lesson data
            prompt = template.format(
                theme_display_name=theme_info.display_name,
                theme_description=theme_info.description,
                key_concepts=', '.join(theme_info.key_concepts),
                example_count=len(examples),
                avg_rating=int(avg_rating)
            )
            
            # Generate content using AI
            content = self._generate_ai_content(prompt)
            
            logger.debug(f"Generated introduction for {theme} at {difficulty.value} level")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate introduction: {e}")
            return self._fallback_introduction(theme_info, difficulty, examples)
    
    def generate_step_content(self, example: PuzzleExample, step_type: StepType,
                            difficulty: DifficultyLevel, theme_info: ThemeInfo) -> str:
        """Generate content for a specific lesson step."""
        try:
            if step_type == StepType.EXAMPLE:
                return self._generate_example_content(example, difficulty, theme_info)
            elif step_type == StepType.SOLUTION:
                return self._generate_solution_content(example, difficulty, theme_info)
            elif step_type == StepType.ANALYSIS:
                return self._generate_analysis_content(example, difficulty, theme_info)
            else:
                logger.warning(f"Unknown step type: {step_type}")
                return f"Content for {step_type.value} step"
                
        except Exception as e:
            logger.error(f"Failed to generate step content: {e}")
            return self._fallback_step_content(example, step_type)
    
    def generate_summary(self, theme: str, difficulty: DifficultyLevel,
                        examples: List[PuzzleExample]) -> str:
        """Generate lesson summary and key takeaways."""
        try:
            theme_info = get_theme_info(theme)
            
            # Get appropriate template
            difficulty_key = difficulty.value
            template = self.templates['summary'].get(
                difficulty_key,
                self.templates['summary']['intermediate']
            )
            
            # Format template with lesson data
            prompt = template.format(
                theme_display_name=theme_info.display_name,
                example_count=len(examples),
                key_concepts=', '.join(theme_info.key_concepts)
            )
            
            # Generate content using AI
            content = self._generate_ai_content(prompt)
            
            logger.debug(f"Generated summary for {theme} at {difficulty.value} level")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return self._fallback_summary(theme_info, examples)
    
    def _generate_example_content(self, example: PuzzleExample, difficulty: DifficultyLevel,
                                theme_info: ThemeInfo) -> str:
        """Generate content for an example step."""
        try:
            # Create prompt for example presentation
            prompt = f"""
Present this chess puzzle to a {difficulty.value} level student.

Position: {example.fen}
Theme: {theme_info.display_name}
Rating: {example.rating}
Quality: {example.quality_score:.2f}

Create engaging content that:
1. Sets up the position and asks the student to find the best move
2. Provides hints about what to look for
3. Mentions the tactical theme without giving away the solution
4. Encourages careful analysis

Keep it concise and engaging. Around 80-120 words.
"""
            
            return self._generate_ai_content(prompt)
            
        except Exception as e:
            logger.error(f"Failed to generate example content: {e}")
            return f"Find the best move in this {theme_info.display_name.lower()} position."
    
    def _generate_solution_content(self, example: PuzzleExample, difficulty: DifficultyLevel,
                                 theme_info: ThemeInfo) -> str:
        """Generate content for a solution step."""
        try:
            solution_moves_str = ' '.join(example.solution_moves[:3])  # First 3 moves
            
            # Get appropriate template
            difficulty_key = difficulty.value
            template = self.templates['example_analysis'].get(
                difficulty_key,
                self.templates['example_analysis']['intermediate']
            )
            
            # Format template
            prompt = template.format(
                fen=example.fen,
                theme_display_name=theme_info.display_name,
                solution_moves=solution_moves_str,
                rating=example.rating,
                themes=', '.join(example.themes[:3])
            )
            
            return self._generate_ai_content(prompt)
            
        except Exception as e:
            logger.error(f"Failed to generate solution content: {e}")
            return f"The solution is {' '.join(example.solution_moves[:2])}."
    
    def _generate_analysis_content(self, example: PuzzleExample, difficulty: DifficultyLevel,
                                 theme_info: ThemeInfo) -> str:
        """Generate detailed analysis content."""
        try:
            prompt = f"""
Provide detailed analysis of this {theme_info.display_name.lower()} puzzle.

Position: {example.fen}
Solution: {' '.join(example.solution_moves)}
Rating: {example.rating}
Themes: {', '.join(example.themes)}

For a {difficulty.value} level student, explain:
1. Why this move works tactically
2. What the opponent's best defenses are
3. Key patterns to remember
4. How this applies to practical play

Use appropriate depth for the skill level. Around 150-200 words.
"""
            
            return self._generate_ai_content(prompt)
            
        except Exception as e:
            logger.error(f"Failed to generate analysis content: {e}")
            return "Detailed analysis of this tactical pattern."
    
    def _generate_ai_content(self, prompt: str) -> str:
        """Generate content using the configured AI provider."""
        try:
            # Check if AI client is available
            if not ai_client.get_available_providers():
                logger.warning("No AI providers available, using fallback content")
                return "AI-generated content not available."
            
            # Generate content
            response = ai_client.get_completion(
                prompt, 
                provider=self.ai_provider,
                temperature=0.7,
                max_tokens=800
            )
            
            if response and len(response.strip()) > 20:
                return response.strip()
            else:
                logger.warning("AI response too short or empty")
                return "Content generation failed."
                
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return "Content generation error."
    
    def _fallback_introduction(self, theme_info: ThemeInfo, difficulty: DifficultyLevel,
                             examples: List[PuzzleExample]) -> str:
        """Fallback introduction when AI generation fails."""
        avg_rating = sum(ex.rating for ex in examples) / len(examples) if examples else 1500
        
        return f"""Welcome to {theme_info.display_name}!

{theme_info.description}

In this {difficulty.value} level lesson, you'll work through {len(examples)} carefully selected puzzles with an average rating of {avg_rating:.0f}. Each example demonstrates key {theme_info.name} patterns that will improve your tactical vision.

Key concepts you'll learn:
{chr(10).join(f"• {concept.replace('_', ' ').title()}" for concept in theme_info.key_concepts)}

Take your time with each position and try to understand the underlying patterns. Let's begin!"""
    
    def _fallback_summary(self, theme_info: ThemeInfo, examples: List[PuzzleExample]) -> str:
        """Fallback summary when AI generation fails."""
        return f"""Lesson Summary: {theme_info.display_name}

You've completed {len(examples)} {theme_info.name} puzzles! Here are the key takeaways:

• Look for {theme_info.name} opportunities when pieces are aligned or overloaded
• Calculate forcing sequences carefully
• Practice recognizing the patterns in your games
• Review these positions periodically to reinforce the concepts

Keep practicing these tactical patterns, and you'll start seeing {theme_info.name} opportunities automatically in your games!"""
    
    def _fallback_step_content(self, example: PuzzleExample, step_type: StepType) -> str:
        """Fallback content for steps when AI generation fails."""
        if step_type == StepType.EXAMPLE:
            return f"Analyze this position and find the best move. Rating: {example.rating}"
        elif step_type == StepType.SOLUTION:
            return f"The solution is: {' '.join(example.solution_moves[:2])}"
        else:
            return f"Content for {step_type.value} step."
    
    def validate_content(self, content: str) -> bool:
        """Validate generated content quality."""
        if not content or len(content.strip()) < 20:
            return False
        
        # Check for common AI generation issues
        problematic_phrases = [
            "I cannot", "I'm sorry", "As an AI", "I don't have access",
            "Content generation failed", "Error", "Failed to generate"
        ]
        
        content_lower = content.lower()
        for phrase in problematic_phrases:
            if phrase.lower() in content_lower:
                return False
        
        return True
    
    def get_content_statistics(self, contents: List[str]) -> Dict:
        """Get statistics about generated content."""
        if not contents:
            return {}
        
        word_counts = [len(content.split()) for content in contents]
        char_counts = [len(content) for content in contents]
        
        return {
            'total_pieces': len(contents),
            'avg_word_count': sum(word_counts) / len(word_counts),
            'avg_char_count': sum(char_counts) / len(char_counts),
            'min_word_count': min(word_counts),
            'max_word_count': max(word_counts),
            'total_words': sum(word_counts),
            'total_characters': sum(char_counts)
        }