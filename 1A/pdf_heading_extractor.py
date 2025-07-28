import fitz
import re
from typing import List, Dict
from text_element import TextElement, TextExtractor
from heading_scorer import HeadingScorer
from document_analyzer import DocumentAnalyzer
from utils import fix_hierarchy, clean_bullet_points

class PDFHeadingExtractor:
    """Main class for extracting headings from PDF files."""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.scorer = HeadingScorer()
        self.analyzer = DocumentAnalyzer()

    def extract_headings(self, filepath: str) -> List[Dict]:
        """Enhanced heading extraction."""
        try:
            doc = fitz.open(filepath)
            print(f"📖 Processing {len(doc)} pages...")
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            return []
        
        all_elements = []
        
        # Extract all text elements
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            elements = self.text_extractor.extract_text_elements(page, page_num + 1)
            all_elements.extend(elements)
        
        doc.close()
        
        if not all_elements:
            print("⚠️  No text elements found")
            return []
        
        # Analyze document structure
        context = self.analyzer.analyze_document_structure(all_elements)
        print(f"🔍 Document analysis: avg_font={context.get('avg_font_size', 0):.1f}, range={context.get('min_font_size', 0):.1f}-{context.get('max_font_size', 0):.1f}")
        
        headings = []
        seen_texts = set()
        
        # Score and classify each element
        for i, element in enumerate(all_elements):
            text = element.text.strip()
            
            # Skip if already seen or too short
            if text.lower() in seen_texts or len(text) < 3:
                continue
            
            # Clean bullet points for comparison but keep in output
            clean_text = clean_bullet_points(text)
            if clean_text.lower() in seen_texts:
                continue
            
            # Add isolation context
            element_context = context.copy()
            element_context['is_isolated'] = self.analyzer.detect_isolation(all_elements, i)
            
            # Calculate heading score
            score = self.scorer.calculate_heading_score(element, element_context)
            
            # Classify if score is high enough (lowered threshold)
            if score >= 0.35:
                level = self.scorer.classify_heading_level(text, score, element)
                
                if level:
                    seen_texts.add(text.lower())
                    seen_texts.add(clean_text.lower())
                    headings.append({
                        "level": level,
                        "text": text,
                        "page": element.page_num,
                        "score": round(score, 2)  # For debugging
                    })
                    print(f"   ✓ {level}: '{text}' (page {element.page_num}, score: {score:.2f})")
        
        # Sort by page and level
        level_order = {"H1": 1, "H2": 2, "H3": 3}
        headings.sort(key=lambda x: (x["page"], level_order.get(x["level"], 99)))
        
        # Post-process: Fix hierarchy and remove duplicates
        headings = fix_hierarchy(headings)
        
        # Remove score from final output
        for heading in headings:
            heading.pop('score', None)
        
        return headings
