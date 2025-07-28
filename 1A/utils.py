import os
import re
from typing import List, Dict

def setup_directories():
    """Setup input and output directories."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try environment variables first, then local directories
    input_dir = os.environ.get('INPUT_DIR', os.path.join(script_dir, 'input'))
    output_dir = os.environ.get('OUTPUT_DIR', os.path.join(script_dir, 'output'))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        print("💡 Create an 'input' directory and add PDF files")
        return None, None
    
    return input_dir, output_dir

def fix_hierarchy(headings: List[Dict]) -> List[Dict]:
    """Fix heading hierarchy to ensure proper nesting."""
    if not headings:
        return headings
    
    fixed_headings = []
    level_order = {"H1": 1, "H2": 2, "H3": 3}
    last_level = 0
    
    for heading in headings:
        current_level = level_order.get(heading["level"], 3)
        
        # Don't skip more than one level
        if current_level > last_level + 1:
            new_level_num = min(last_level + 1, 3)
            heading["level"] = f"H{new_level_num}"
            current_level = new_level_num
        
        fixed_headings.append(heading)
        last_level = current_level
    
    return fixed_headings

def clean_bullet_points(text: str) -> str:
    """Clean bullet points for comparison but keep in output."""
    return re.sub(r'^[•·▪▫◦‣⁃*-]\s*', '', text).strip()
