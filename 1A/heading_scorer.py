import re
from typing import Dict, Optional
from text_element import TextElement
from heading_patterns import HeadingPatterns

class HeadingScorer:
    """Handles scoring and classification of potential headings."""
    
    def __init__(self):
        self.patterns = HeadingPatterns()

    def calculate_heading_score(self, element: TextElement, context: Dict) -> float:
        """Enhanced heading score calculation."""
        text = element.text.strip()
        words = text.split()
        score = 0.0
        
        # 1. Font and formatting score (35%)
        if element.is_bold:
            score += 0.2
        if element.is_italic and not element.is_bold:
            score += 0.05  # Italic alone is less likely for headings
        
        # Font size relative scoring
        if element.font_size > context.get('avg_font_size', 12):
            size_ratio = element.font_size / context.get('avg_font_size', 12)
            score += min(0.15, (size_ratio - 1) * 0.1)
        
        # 2. Text characteristics score (30%)
        if 2 <= len(words) <= 12:  # Reasonable heading length
            if len(words) <= 6:
                score += 0.15  # Shorter is better for headings
            else:
                score += 0.1
        
        # Case and formatting
        if text.isupper() and len(text) > 8:
            score += 0.1
        elif text.istitle() and len(words) >= 2:
            score += 0.08
        elif text[0].isupper() and len(words) >= 2:
            score += 0.05
        
        # 3. Positioning and isolation score (20%)
        if element.left_margin <= context.get('min_left_margin', 0) + 10:
            score += 0.1  # Left-aligned
        
        if context.get('is_isolated', False):
            score += 0.1  # Has whitespace around it
        
        # 4. Pattern matching score (15%)
        pattern_score = self.patterns.get_pattern_score(text)
        score += pattern_score * 0.15
        
        # Additional bonuses for strong indicators
        if text.endswith(':') and text.istitle():
            score += 0.1
        if re.match(r'^\d+\.(\d+\.)*\s+[A-Z]', text):
            score += 0.15
        if any(word in text for word in ['Mission', 'Journey', 'Challenge', 'Matters', 'Welcome']):
            score += 0.1
        
        # Penalties
        if len(words) > 15:
            score -= 0.3
        if self.patterns.matches_exclusion_patterns(text):
            score -= 0.4
        if self.patterns.looks_like_prose(text):
            score -= 0.3
        if len(text) < 5:
            score -= 0.2
        
        return max(0.0, min(1.0, score))

    def classify_heading_level(self, text: str, score: float, element: TextElement) -> Optional[str]:
        """Enhanced heading level classification."""
        # Check specific patterns first
        for level, patterns in self.patterns.heading_patterns.items():
            for pattern in patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    return level
        
        # Fallback classification based on characteristics
        if score < 0.35:  # Lowered threshold
            return None
        
        words = text.split()
        
        # Strong H1 indicators
        if (text.isupper() and len(text) > 15) or \
           re.match(r'^(Chapter|CHAPTER)\s+\d+', text) or \
           any(word in text for word in ['Mission', 'Journey', 'Challenge', 'Welcome']) or \
           (score >= 0.7 and len(words) <= 6):
            return "H1"
        
        # Strong H2 indicators
        if re.match(r'^\d+\.\s+[A-Z]', text) or \
           (text.isupper() and 8 <= len(text) <= 15) or \
           (text.istitle() and len(words) >= 3 and score >= 0.6):
            return "H2"
        
        # Strong H3 indicators
        if (text.endswith(':') and text.istitle()) or \
           re.match(r'^\d+\.\d+', text) or \
           text.startswith('•') or \
           re.match(r'^(Phase|Round|Step)\s+\d+', text):
            return "H3"
        
        # Default based on score and formatting
        if element.is_bold and score >= 0.6:
            if len(words) <= 4:
                return "H1"
            elif len(words) <= 8:
                return "H2"
            else:
                return "H3"
        elif score >= 0.5:
            return "H2"
        else:
            return "H3"
