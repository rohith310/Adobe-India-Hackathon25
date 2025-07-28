from typing import List, Dict
from collections import Counter
from text_element import TextElement

class DocumentAnalyzer:
    """Analyzes document structure and provides context for heading detection."""
    
    def analyze_document_structure(self, all_elements: List[TextElement]) -> Dict:
        """Analyze document structure to provide context for heading detection."""
        if not all_elements:
            return {}
        
        font_sizes = [elem.font_size for elem in all_elements]
        left_margins = [elem.left_margin for elem in all_elements]
        
        context = {
            'avg_font_size': sum(font_sizes) / len(font_sizes),
            'max_font_size': max(font_sizes),
            'min_font_size': min(font_sizes),
            'min_left_margin': min(left_margins),
            'max_left_margin': max(left_margins),
        }
        
        # Identify font size clusters
        font_size_counts = Counter(font_sizes)
        context['common_font_sizes'] = [size for size, count in font_size_counts.most_common(3)]
        
        return context

    def detect_isolation(self, elements: List[TextElement], index: int) -> bool:
        """Enhanced isolation detection."""
        if not elements or index < 0 or index >= len(elements):
            return False
        
        current = elements[index]
        threshold = current.line_height * 1.2  # Reduced threshold to catch more
        
        # Check spacing above
        has_space_above = True
        if index > 0:
            prev = elements[index - 1]
            if (current.page_num == prev.page_num and 
                current.top_position - (prev.top_position + prev.line_height) < threshold):
                has_space_above = False
        
        # Check spacing below
        has_space_below = True
        if index < len(elements) - 1:
            next_elem = elements[index + 1]
            if (current.page_num == next_elem.page_num and 
                next_elem.top_position - (current.top_position + current.line_height) < threshold):
                has_space_below = False
        
        # Also consider if it's the first/last element on a page
        is_page_boundary = (index == 0 or 
                           (index > 0 and elements[index-1].page_num != current.page_num) or
                           index == len(elements) - 1 or
                           (index < len(elements) - 1 and elements[index+1].page_num != current.page_num))
        
        return has_space_above or has_space_below or is_page_boundary
