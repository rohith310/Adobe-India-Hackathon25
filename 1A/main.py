import os
import json
import sys
from collections import Counter

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed.")
    print("Please run: pip install PyMuPDF")
    sys.exit(1)

from pdf_heading_extractor import PDFHeadingExtractor
from utils import setup_directories

def process_pdf_file(filepath, output_dir, extractor):
    """Process a single PDF file."""
    filename = os.path.basename(filepath)
    base_name = os.path.splitext(filename)[0]
    
    print(f"\n🔄 Processing: {filename}")
    print("-" * 50)
    
    try:
        headings = extractor.extract_headings(filepath)
        
        # Create output data
        output_data = {
            "title": base_name,
            "outline": headings
        }
        
        # Save to JSON
        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Display results
        print(f"\n✅ Extracted {len(headings)} headings")
        print(f"💾 Saved: {base_name}.json")
        
        if headings:
            level_counts = Counter(h["level"] for h in headings)
            print(f"📊 Distribution: {dict(level_counts)}")
            
            print(f"\n📋 Preview:")
            for i, heading in enumerate(headings[:5]):
                indent = "  " * (int(heading["level"][1]) - 1)
                print(f"   {indent}{heading['level']}: {heading['text']} (Page {heading['page']})")
            
            if len(headings) > 5:
                print(f"   ... and {len(headings) - 5} more")
        else:
            print("⚠️  No headings detected")
            
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to process PDF files."""
    print("🚀 PDF Heading Extractor")
    print("=" * 50)
    
    # Setup directories
    input_dir, output_dir = setup_directories()
    if not input_dir:
        return
    
    print(f"📂 Input:  {input_dir}")
    print(f"📂 Output: {output_dir}")
    
    # Find PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found!")
        return
    
    print(f"\n🎯 Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   📄 {pdf}")
    
    # Initialize extractor
    extractor = PDFHeadingExtractor()
    
    # Process each PDF
    for filename in pdf_files:
        filepath = os.path.join(input_dir, filename)
        process_pdf_file(filepath, output_dir, extractor)
    
    print(f"\n🎉 Processing complete!")

if __name__ == "__main__":
    main()
