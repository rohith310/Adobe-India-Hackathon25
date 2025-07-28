import re
from typing import Dict, List

class HeadingPatterns:
    """Manages heading patterns and text classification rules."""
    
    def __init__(self):
        # Enhanced semantic patterns for different heading levels
        self.heading_patterns = {
            'H1': [
                r'^(Chapter|CHAPTER)\s+\d+',
                r'^(Abstract|Introduction|Conclusion|Summary|References|Bibliography)$',
                r'^[A-Z\s]{15,}$',  # Long uppercase text
                r'^(Executive\s+Summary|Table\s+of\s+Contents)$',
                r'^\d+\.\s+[A-Z][A-Za-z\s]{10,}$',  # "1. Major Section"
                r'^(Welcome\s+to|The\s+Journey|Your\s+Mission|Why\s+This\s+Matters)$',
                r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Challenge|Mission|Journey|Matters)$'
            ],
            'H2': [
                r'^\d+\.\d+\s+[A-Z]',  # "1.1 Subsection"
                r'^[A-Z][A-Z\s]{8,20}$',  # Medium uppercase
                r'^(Background|Methodology|Results|Discussion|Analysis|Implementation|Evaluation)$',
                r'^(Problem\s+Statement|Related\s+Work|Future\s+Work)$',
                r'^(What\s+You\s+Need|You\s+Will\s+Be|The\s+Journey\s+Ahead)$',
                r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){2,4}$'  # "Title Case Headings"
            ],
            'H3': [
                r'^\d+\.\d+\.\d+\s+[A-Z]',  # "1.1.1 Sub-subsection"
                r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:$',  # "Title Case:"
                r'^(Phase|Step|Stage|Round)\s+\d+',
                r'^[a-z]+\)\s+[A-Z]',  # "a) Item"
                r'^•\s+[A-Z][a-z]+.*:$'  # "• Round 1:"
            ]
        }

        # Enhanced exclusion patterns
        self.exclusion_patterns = [
            r'^\d+$',  # Just numbers
            r'^page\s+\d+',
            r'copyright|©|confidential',
            r'^(see|refer|figure|table|note)\s+',
            r'\.com|\.org|\.net|@',
            r'^\w{1,2}$',  # Very short words
            r'^(and|or|but|the|a|an|in|on|at|by|for|with|from|to|of|is|are|was|were)\s+',
            r'(experience|like|feels|seems|appears|building|creating|using|making)',
            r'(up\s+to\s+\d+|more\s+than|less\s+than)',
            r'(you\'re|we\'re|it\'s|that\'s|don\'t|won\'t)'
        ]

    def get_pattern_score(self, text: str) -> float:
        """Enhanced pattern scoring."""
        # Check explicit patterns first
        for level, patterns in self.heading_patterns.items():
            for pattern in patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    return 1.0
        
        # Additional pattern checks with scores
        if re.match(r'^\d+\.(\d+\.)*\s+[A-Z]', text):
            return 0.9
        if text.endswith(':') and text.istitle() and len(text.split()) >= 2:
            return 0.7
        if re.match(r'^[A-Z][A-Z\s]+$', text) and len(text) > 8:
            return 0.8
        if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){1,3}$', text):
            return 0.6
        if text.startswith('•') and ':' in text:
            return 0.5
        
        return 0.0

    def looks_like_prose(self, text: str) -> bool:
        """Check if text looks like prose rather than a heading."""
        prose_indicators = [
            r'(experience|like|feels|seems|appears)',
            r'(building|creating|using|making|developing)',
            r'(you|your|we|our|they|their)',
            r'(will|would|could|should|must|can)',
            r'(this|that|these|those|it)',
            r'\?',  # Questions
            r'(and|or|but)\s+\w+\s+(and|or|but)',  # Multiple conjunctions
        ]
        
        text_lower = text.lower()
        prose_count = sum(1 for pattern in prose_indicators if re.search(pattern, text_lower))
        
        # Also check for sentence-like structure
        has_articles = any(word in text_lower.split() for word in ['the', 'a', 'an'])
        has_conjunctions = any(word in text_lower.split() for word in ['and', 'or', 'but', 'so'])
        
        return prose_count > 0 or (has_articles and has_conjunctions and len(text.split()) > 6)

    def matches_exclusion_patterns(self, text: str) -> bool:
        """Check if text matches any exclusion patterns."""
        return any(re.search(pattern, text.lower()) for pattern in self.exclusion_patterns)
