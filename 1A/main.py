try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed or corrupted.")
    print("Please run: pip install PyMuPDF==1.23.22")
    print("Or if using the project: pip install -r requirements.txt")
    sys.exit(1)

import os
import json
import sys
from collections import Counter

def get_font_styles(doc):
    """Extract all font styles used in the document"""
    styles = Counter()
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:  # Text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        styles[(s["size"], s["flags"])] += 1
    return styles

def get_heading_levels(styles):
    """Determine heading levels based on font sizes"""
    if not styles:
        return {}
    
    # Get unique font sizes sorted by frequency (most common first)
    font_info = {}
    for (size, flags), count in styles.items():
        if size not in font_info:
            font_info[size] = {'count': 0, 'has_bold': False}
        font_info[size]['count'] += count
        if flags & 2**4:  # Bold flag
            font_info[size]['has_bold'] = True
    
    # Sort by size (largest first) - larger fonts are typically higher level headings
    font_sizes = sorted(font_info.keys(), reverse=True)
    
    # Assign heading levels (1 = highest, 2 = second, etc.)
    heading_levels = {}
    level = 1
    for size in font_sizes[:4]:  # Max 4 heading levels
        heading_levels[size] = level
        level += 1
    
    return heading_levels

def extract_outline(filepath):
    """Extract outline/headings from PDF"""
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        print(f"Error opening PDF {filepath}: {e}")
        return []
    
    styles = get_font_styles(doc)
    heading_levels = get_heading_levels(styles)
    
    outline = []
    
    # Add filename as title
    filename = os.path.basename(filepath)
    outline.append({
        "text": os.path.splitext(filename)[0],
        "level": 0,  # Title level
        "page": 1,
        "type": "title"
    })

    # Track seen text to avoid duplicates
    seen_text = set()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        for b in blocks:
            if b['type'] == 0:  # Text block
                for l in b["lines"]:
                    # Combine all spans in a line to get complete text
                    line_text = ""
                    line_font_size = None
                    line_flags = None
                    
                    for s in l["spans"]:
                        line_text += s["text"]
                        if line_font_size is None:
                            line_font_size = s["size"]
                            line_flags = s["flags"]
                    
                    line_text = line_text.strip()
                    
                    # Skip empty lines or very short text
                    if not line_text or len(line_text) < 3:
                        continue
                    
                    # Skip if we've already seen this text
                    if line_text.lower() in seen_text:
                        continue
                    
                    # Check if this line looks like a heading
                    font_size = line_font_size
                    is_bold = line_flags & 2**4 if line_flags else False
                    is_all_caps = line_text.isupper() and len(line_text) > 1
                    
                    level = heading_levels.get(font_size)
                    
                    # Additional heuristics for headings
                    if level is None:
                        # If text is bold or all caps and reasonably short, treat as heading
                        if (is_bold or is_all_caps) and len(line_text) < 100:
                            level = max(heading_levels.values()) + 1 if heading_levels else 1
                    
                    # Additional checks: skip very long text (likely paragraphs)
                    if level and len(line_text) < 200:  # Headings are typically shorter
                        seen_text.add(line_text.lower())
                        outline.append({
                            "text": line_text,
                            "level": level,
                            "page": page_num + 1,
                            "type": "heading",
                            "font_size": font_size,
                            "is_bold": is_bold,
                            "is_caps": is_all_caps
                        })

    doc.close()
    return outline

def main():
    # Make paths configurable for easier local testing
    input_dir = os.environ.get('INPUT_DIR', '/app/input')
    output_dir = os.environ.get('OUTPUT_DIR', '/app/output')
    
    # For local testing, use current directory structure
    if not os.path.exists(input_dir):
        local_input = os.path.join(os.path.dirname(__file__), 'input')
        if os.path.exists(local_input):
            input_dir = local_input
        else:
            print(f"Input directory not found: {input_dir}")
            print("Please create an 'input' directory and place your PDF files there.")
            return
    
    if not os.path.exists(output_dir):
        local_output = os.path.join(os.path.dirname(__file__), 'output')
        try:
            os.makedirs(local_output, exist_ok=True)
            output_dir = local_output
        except:
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                print(f"Could not create output directory: {e}")
                return
    
    print(f"Looking for PDFs in: {input_dir}")
    print(f"Output will be saved to: {output_dir}")
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory!")
        print("Please add some PDF files to process.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    for filename in pdf_files:
        filepath = os.path.join(input_dir, filename)
        
        print(f"\nProcessing: {filename}")
        
        try:
            outline = extract_outline(filepath)
            
            if not outline:
                print(f"  No outline extracted from {filename}")
                continue
            
            # Create both JSON and readable text output
            base_name = os.path.splitext(filename)[0]
            
            # JSON output
            json_output = os.path.join(output_dir, base_name + "_outline.json")
            with open(json_output, "w", encoding='utf-8') as f:
                json.dump({"outline": outline}, f, indent=2, ensure_ascii=False)
            
            # Text output for easy reading
            txt_output = os.path.join(output_dir, base_name + "_outline.txt")
            with open(txt_output, "w", encoding='utf-8') as f:
                f.write(f"OUTLINE FOR: {filename}\n")
                f.write("=" * 50 + "\n\n")
                
                for item in outline:
                    indent = "  " * (item["level"] if item["level"] > 0 else 0)
                    f.write(f"{indent}{item['text']} (Page {item['page']})\n")
            
            print(f"  ✓ Extracted {len(outline)} items")
            print(f"  ✓ Saved to: {base_name}_outline.json and {base_name}_outline.txt")
                
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
