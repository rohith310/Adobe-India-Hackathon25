from dataclasses import dataclass
from typing import List
import fitz

@dataclass
class TextElement:
    text: str
    font_size: float
    is_bold: bool
    is_italic: bool
    left_margin: float
    top_position: float
    page_num: int
    line_height: float
    font_name: str = ""

class TextExtractor:
    """Handles extraction of text elements from PDF pages."""
    
    def extract_text_elements(self, page, page_num: int) -> List[TextElement]:
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
