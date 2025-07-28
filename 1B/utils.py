import os
import sys
import json
import re
import fitz
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

try:
    from sentence_transformers import SentenceTransformer
    from transformers import pipeline
    import torch
except ImportError:
    print("❌ Required ML libraries not installed.")
    print("Please run: pip install sentence-transformers transformers torch")
    sys.exit(1)

@dataclass
class TextElement:
    """Represents a text element with positioning and formatting info."""
    text: str
    font_size: float
    is_bold: bool
    is_italic: bool
    left_margin: float
    top_position: float
    page_num: int
    line_height: float
    font_name: str = ""

class PDFParser:
    """Handles PDF parsing and text extraction with detailed formatting info."""
    
    def parse_pdf(self, filepath: str) -> List[TextElement]:
        """Parse PDF and extract all text elements with positioning and formatting."""
        try:
            doc = fitz.open(filepath)
            print(f"📖 Processing {len(doc)} pages...")
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            return []
        
        all_elements = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            elements = self._extract_text_elements(page, page_num + 1)
            all_elements.extend(elements)
        
        doc.close()
        return all_elements
    
    def _extract_text_elements(self, page, page_num: int) -> List[TextElement]:
        """Extract detailed text elements with positioning and formatting info."""
        elements = []
        blocks = page.get_text("dict", flags=11).get("blocks", [])
        
        for block in blocks:
            if block.get('type') != 0:  # Skip non-text blocks
                continue
                
            for line in block.get("lines", []):
                line_text = ""
                font_sizes = []
                flags_list = []
                font_names = []
                bbox_info = []
                
                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if span_text:
                        line_text += span_text + " "
                        font_sizes.append(span.get("size", 12))
                        flags_list.append(span.get("flags", 0))
                        font_names.append(span.get("font", ""))
                        bbox_info.append(span.get("bbox", [0, 0, 0, 0]))
                
                line_text = line_text.strip()
                if line_text and len(line_text) > 2:
                    # Calculate dominant font characteristics
                    max_font_size = max(font_sizes) if font_sizes else 12
                    is_bold = any(bool(flags & 16) for flags in flags_list)
                    is_italic = any(bool(flags & 2) for flags in flags_list)
                    
                    # Calculate positioning
                    if bbox_info:
                        left_margin = min(bbox[0] for bbox in bbox_info)
                        top_position = min(bbox[1] for bbox in bbox_info)
                        line_height = max(bbox[3] - bbox[1] for bbox in bbox_info)
                    else:
                        left_margin = 0
                        top_position = 0
                        line_height = max_font_size
                    
                    dominant_font = max(set(font_names), key=font_names.count) if font_names else ""
                    
                    elements.append(TextElement(
                        text=line_text,
                        font_size=max_font_size,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        left_margin=left_margin,
                        top_position=top_position,
                        page_num=page_num,
                        line_height=line_height,
                        font_name=dominant_font
                    ))
        
        return elements

def extract_section_headings(text_elements: List[TextElement]) -> List[Dict]:
    """Extract section-level headings using heuristics and fallback logic."""
    if not text_elements:
        return []
    
    # Analyze document structure
    font_sizes = [elem.font_size for elem in text_elements]
    avg_font_size = sum(font_sizes) / len(font_sizes)
    
    headings = []
    seen_texts = set()
    
    # Very strict heading patterns for accuracy
    heading_patterns = [
        r'^(Introduction|Conclusion|Summary|Guide|Tips)$',
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){1,3}$',  # Title case (2-4 words only)
        r'^(Activities|Things|Places|Hotels|Restaurants|History|Culture)$',
    ]
    
    # Comprehensive exclusion patterns for accuracy
    exclusion_patterns = [
        r'^(and|or|but|the|a|an|in|on|at|by|for|with|from|to|of)\s+',
        r'^(this|that|these|those|it|they|we|you|are|is|was|were)\s+',
        r'[.!?]$',  # Ends with punctuation
        r'(visit|explore|discover|enjoy|experience|located|situated|offers|provides|features|includes)',
        r'^(one|some|many|several|various|day|night|morning|afternoon|evening)\s+',
        r'(market|museum|restaurant|hotel|city|region)\s+(explores|showcases|features)',
        r'(perfect|ideal|best|great|wonderful|beautiful|stunning)',
    ]
    
    for i, element in enumerate(text_elements):
        text = element.text.strip()
        
        # Very strict length requirements for precision
        if (text.lower() in seen_texts or 
            len(text) < 5 or 
            len(text) > 50 or  # Much shorter limit
            len(text.split()) > 5):  # Max 5 words
            continue
        
        # Strict exclusion filtering
        is_excluded = any(re.search(pattern, text.lower()) for pattern in exclusion_patterns)
        if is_excluded:
            continue
        
        is_heading = False
        heading_level = "H3"
        
        # Only very clear headings
        # Font size must be significantly larger
        if element.font_size > avg_font_size * 1.4:
            is_heading = True
            heading_level = "H1" if element.font_size > avg_font_size * 1.7 else "H2"
        
        # Bold + left-aligned + larger font
        elif element.is_bold and element.left_margin <= 30 and element.font_size > avg_font_size * 1.2:
            is_heading = True
            heading_level = "H2"
        
        # Semantic patterns (very specific)
        elif any(re.match(pattern, text, re.IGNORECASE) for pattern in heading_patterns):
            is_heading = True
            if re.match(r'^(Introduction|Conclusion|Guide)', text, re.IGNORECASE):
                heading_level = "H1"
            else:
                heading_level = "H2"
        
        # Final quality check
        if is_heading:
            # Must be proper title format
            if not (text.istitle() or text.isupper()):
                continue
            
            # No sentence-like words
            if any(word in text.lower() for word in ['visit', 'explore', 'located', 'offers']):
                continue
            
            seen_texts.add(text.lower())
            headings.append({
                "level": heading_level,
                "text": text,
                "page": element.page_num,
                "position": element.top_position,
                "element_index": i
            })
    
    # Aggressive duplicate removal
    headings.sort(key=lambda x: (x["page"], x["position"]))
    filtered_headings = []
    
    for heading in headings:
        is_duplicate = False
        for existing in filtered_headings:
            # Remove if any word overlap
            common_words = set(heading['text'].lower().split()) & set(existing['text'].lower().split())
            if len(common_words) > 0:
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_headings.append(heading)
    
    # Limit to top 8 headings per document for conciseness
    return filtered_headings[:8]

def rank_sections_by_relevance(sections: List[Dict], job_description: str, 
                              embedding_model) -> List[Dict]:
    """
    Rank sections by semantic similarity to job description using embeddings.
    
    Args:
        sections: List of section dictionaries
        job_description: Target job description
        embedding_model: Sentence transformer model
        
    Returns:
        List of sections with importance ranks (1-5)
    """
    if not sections:
        return []
    
    # Generate embedding for job description
    job_embedding = embedding_model.encode([job_description])[0]
    
    # Calculate similarities
    section_scores = []
    for section in sections:
        # Create section context
        section_text = f"{section['text']}: {section.get('content', '')[:300]}"
        section_embedding = embedding_model.encode([section_text])[0]
        
        # Calculate cosine similarity
        similarity = np.dot(job_embedding, section_embedding) / (
            np.linalg.norm(job_embedding) * np.linalg.norm(section_embedding)
        )
        
        section_scores.append((section, similarity))
    
    # Sort by similarity (descending)
    section_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Assign importance ranks (1-5, where 5 is most important)
    ranked_sections = []
    total_sections = len(section_scores)
    
    for i, (section, score) in enumerate(section_scores):
        # Assign rank based on percentile
        percentile = (total_sections - i) / total_sections
        if percentile >= 0.8:
            rank = 5
        elif percentile >= 0.6:
            rank = 4
        elif percentile >= 0.4:
            rank = 3
        elif percentile >= 0.2:
            rank = 2
        else:
            rank = 1
        
        section['importance_rank'] = rank
        section['similarity_score'] = score
        ranked_sections.append(section)
    
    return ranked_sections

def extract_paragraph_chunks(text_elements: List[TextElement], 
                           heading_positions: List[Tuple[int, int]]) -> Dict[int, str]:
    """Extract paragraph chunks below each section heading."""
    content_map = {}
    
    for i, (start_idx, end_idx) in enumerate(heading_positions):
        content_parts = []
        
        # Extract text between current heading and next heading
        for j in range(start_idx + 1, min(end_idx, len(text_elements))):
            element = text_elements[j]
            text = element.text.strip()
            
            # More lenient content inclusion
            if len(text) < 5:  # Reduced from 15
                continue
            
            # Less aggressive heading filtering
            avg_font = 12  # Assume average
            if element.is_bold and element.font_size > avg_font * 1.3:
                continue
            
            # More lenient header/footer detection
            page_elements = [e for e in text_elements if e.page_num == element.page_num]
            if page_elements:
                page_height = max(e.top_position + e.line_height for e in page_elements)
                relative_pos = element.top_position / page_height if page_height > 0 else 0
                if relative_pos <= 0.05 or relative_pos >= 0.95:  # Only extreme positions
                    continue
            
            content_parts.append(text)
            
            # Increased content length limit
            if len(" ".join(content_parts)) > 2500:  # Increased from 1500
                break
        
        # Join content with proper spacing
        content = " ".join(content_parts)
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\s*\.\s*', '. ', content)
        content = re.sub(r'\s*,\s*', ', ', content)
        
        content_map[i] = content.strip()
    
    return content_map

def summarize_sections(sections: List[Dict], summarizer_pipeline) -> List[Dict]:
    """Summarize selected sections with very concise output."""
    summarized = []
    
    for section in sections:
        content = section.get('content', '')
        
        # Skip if content too short
        if len(content.split()) < 15:
            refined_text = content[:100] + "..." if len(content) > 100 else content
        else:
            try:
                # Much shorter content for conciseness
                max_chars = 500  # Reduced from 1000
                truncated_content = content[:max_chars]
                
                # Very short summaries
                input_words = len(truncated_content.split())
                adaptive_max_length = max(15, min(40, int(input_words * 0.4)))  # Much shorter
                adaptive_min_length = max(8, min(adaptive_max_length - 5, int(input_words * 0.2)))
                
                summary_result = summarizer_pipeline(
                    truncated_content,
                    max_length=adaptive_max_length,
                    min_length=adaptive_min_length,
                    do_sample=False
                )
                
                refined_text = summary_result[0]['summary_text']
                
            except Exception as e:
                print(f"⚠️  Summarization failed: {e}")
                refined_text = content[:80] + "..." if len(content) > 80 else content
        
        summarized.append({
            'document_name': section['document_name'],
            'page_number': section['page_number'],
            'refined_text': refined_text
        })
    
    return summarized

class OutlineBuilder:
    """Builds hierarchical outline structure with content linking."""
    
    def build_hierarchical_outline(self, text_elements: List[TextElement]) -> List[Dict]:
        """Build complete hierarchical outline with content."""
        if not text_elements:
            return []
        
        # Extract headings
        headings = extract_section_headings(text_elements)
        if not headings:
            return []
        
        # Create heading position map
        heading_positions = []
        for i, heading in enumerate(headings):
            start_idx = heading['element_index']
            end_idx = (headings[i + 1]['element_index'] 
                      if i + 1 < len(headings) 
                      else len(text_elements))
            heading_positions.append((start_idx, end_idx))
        
        # Extract content for each heading
        content_map = extract_paragraph_chunks(text_elements, heading_positions)
        
        # Combine headings with content
        outline = []
        for i, heading in enumerate(headings):
            heading['content'] = content_map.get(i, '')
            outline.append(heading)
        
        return outline

class SemanticAnalyzer:
    """Handles semantic similarity and summarization using lightweight models."""
    
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.embedding_model = None
        self.summarizer = None
        
    def initialize_models(self):
        """Initialize lightweight models for CPU execution."""
        try:
            # Force CPU usage
            torch.set_num_threads(1)
            
            # Load sentence transformer (~90MB)
            print("📥 Loading sentence transformer (all-MiniLM-L6-v2)...")
            self.embedding_model = SentenceTransformer(
                'sentence-transformers/all-MiniLM-L6-v2',
                cache_folder=self.models_dir,
                device='cpu'
            )
            
            # Load T5-small for summarization (~240MB) with adaptive parameters
            print("📥 Loading summarization model (t5-small)...")
            self.summarizer = pipeline(
                "summarization",
                model="t5-small",
                tokenizer="t5-small",
                device=-1  # CPU only
                # Removed fixed max_length and min_length - will be set per call
            )
            
            print("✅ Models loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def analyze_document_relevance(self, outline: List[Dict], doc_name: str, 
                                 persona: str, job_description: str) -> List[Dict]:
        """Analyze document sections for relevance to persona and job."""
        if not outline:
            return []
        
        # Rank sections by relevance
        ranked_sections = rank_sections_by_relevance(
            outline, job_description, self.embedding_model
        )
        
        # Add document metadata
        for section in ranked_sections:
            section['document_name'] = doc_name
            section['page_number'] = section['page']
            section['section_title'] = section['text']
        
        return ranked_sections
    
    def rank_sections_globally(self, all_sections: List[Dict]) -> List[Dict]:
        """Rank all sections across documents by importance rank."""
        # Sort by importance rank (descending) then by similarity score
        ranked = sorted(all_sections, 
                       key=lambda x: (x['importance_rank'], x.get('similarity_score', 0)), 
                       reverse=True)
        
        # Limit total output to top 25 sections for conciseness
        return ranked[:25]
    
    def generate_summaries(self, sections: List[Dict]) -> List[Dict]:
        """Generate summaries for selected sections."""
        # Only top 10 sections with rank 5 for maximum relevance
        top_sections = [s for s in sections if s['importance_rank'] == 5][:10]
        return summarize_sections(top_sections, self.summarizer)

class JSONExporter:
    """Enhanced JSON exporter for structured output."""
    
    def create_structured_output(self, processed_docs: List[str], persona: str, 
                                job_description: str, ranked_sections: List[Dict],
                                summarized_sections: List[Dict], processing_time: float) -> Dict:
        """Create structured output matching challenge1b format."""
        
        return {
            "metadata": {
                "input_documents": processed_docs,
                "persona": persona,
                "job_to_be_done": job_description,
                "timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "total_sections_analyzed": len(ranked_sections)
            },
            "extracted_sections": [
                {
                    "document_name": section['document_name'],
                    "page_number": section['page_number'],
                    "section_title": section['section_title'],
                    "importance_rank": round(section['importance_rank'], 4)
                }
                for section in ranked_sections
            ],
            "sub_section_analysis": summarized_sections
        }
    
    def export_to_json(self, data: Dict, filepath: str):
        """Export data to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
