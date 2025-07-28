import os
import json
import sys
import time
from datetime import datetime
from collections import Counter

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed.")
    print("Please run: pip install PyMuPDF")
    sys.exit(1)

from utils import PDFParser, OutlineBuilder, SemanticAnalyzer, JSONExporter

def setup_directories():
    """Setup input and output directories."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if running in Docker
    if os.path.exists('/app'):
        input_dir = '/app/input'
        output_dir = '/app/output'
        models_dir = '/app/models'
    else:
        input_dir = os.environ.get('INPUT_DIR', os.path.join(script_dir, 'input'))
        output_dir = os.environ.get('OUTPUT_DIR', os.path.join(script_dir, 'output'))
        models_dir = os.path.join(script_dir, 'models')
    
    for directory in [output_dir, models_dir]:
        os.makedirs(directory, exist_ok=True)
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        print("💡 Create an 'input' directory and add PDF files")
        return None, None, None
    
    return input_dir, output_dir, models_dir

def get_user_inputs():
    """Get persona and job description from user input or environment."""
    # Try environment variables first (for Docker/automated runs)
    persona = os.environ.get('PERSONA')
    job_description = os.environ.get('JOB_TO_BE_DONE')
    
    # If not in environment, prompt user
    if not persona:
        print("\n" + "="*60)
        print("📝 Please provide the following inputs:")
        print("="*60)
        persona = input("👤 Enter persona (e.g., 'PhD Researcher in Computational Biology'): ").strip()
        if not persona:
            persona = "PhD Researcher in Computational Biology"
    
    if not job_description:
        if 'PERSONA' not in os.environ:  # Only prompt if not using env vars
            job_description = input("🎯 Enter job to be done (e.g., 'Prepare a comprehensive literature review...'): ").strip()
        if not job_description:
            job_description = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
    
    print(f"\n👤 Persona: {persona}")
    print(f"🎯 Job: {job_description}")
    
    return persona, job_description

def process_documents_pipeline(input_dir, output_dir, models_dir, persona, job_description):
    """Complete pipeline for processing PDF documents with semantic analysis."""
    start_time = time.time()
    
    # Find PDF files (increased limit to 7 for performance)
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')][:7]
    
    if not pdf_files:
        print("❌ No PDF files found!")
        return None
    
    print(f"\n🎯 Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   📄 {pdf}")
    
    # Initialize components
    print("\n🔧 Initializing components...")
    parser = PDFParser()
    builder = OutlineBuilder()
    analyzer = SemanticAnalyzer(models_dir)
    exporter = JSONExporter()
    
    # Initialize semantic analyzer
    print("🤖 Loading semantic models...")
    analyzer.initialize_models()
    
    all_sections = []
    processed_docs = []
    
    # Process each PDF
    for filename in pdf_files:
        filepath = os.path.join(input_dir, filename)
        
        print(f"\n🔄 Processing: {filename}")
        print("-" * 40)
        
        try:
            # Extract section headings
            print("📋 Extracting section headings...")
            text_elements = parser.parse_pdf(filepath)
            if not text_elements:
                print(f"⚠️  No text elements found in {filename}")
                continue
            
            # Build outline with content
            print("🔗 Building outline structure...")
            outline = builder.build_hierarchical_outline(text_elements)
            if not outline:
                print(f"⚠️  No outline created for {filename}")
                continue
            
            # Rank sections by relevance
            print("🎯 Ranking sections by relevance...")
            doc_sections = analyzer.analyze_document_relevance(
                outline, filename, persona, job_description
            )
            
            all_sections.extend(doc_sections)
            processed_docs.append(filename)
            
            print(f"✅ Extracted {len(doc_sections)} sections")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not all_sections:
        print("❌ No sections extracted from any document!")
        return None
    
    # Rank all sections globally and assign importance ranks
    print(f"\n🔍 Ranking {len(all_sections)} sections globally...")
    ranked_sections = analyzer.rank_sections_globally(all_sections)
    
    # Generate summaries for only the most relevant sections
    print(f"📝 Generating summaries for top-ranked sections...")
    top_sections = [s for s in ranked_sections if s['importance_rank'] == 5][:8]  # Only rank 5, max 8
    summarized_sections = analyzer.generate_summaries(top_sections)
    
    # Create final output
    processing_time = time.time() - start_time
    output_data = exporter.create_structured_output(
        processed_docs, persona, job_description, 
        ranked_sections, summarized_sections, processing_time
    )
    
    # Save to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"challenge1b_output_{timestamp}.json"
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Display results
    print(f"\n✅ Processing complete in {processing_time:.1f} seconds")
    print(f"💾 Saved: {output_filename}")
    print(f"📊 Total sections analyzed: {len(ranked_sections)}")
    print(f"📝 Top sections summarized: {len(summarized_sections)}")
    
    # Show top sections preview
    print(f"\n📋 Top 5 relevant sections:")
    for i, section in enumerate(ranked_sections[:5]):
        print(f"   {i+1}. [{section['importance_rank']}] {section['section_title']}")
        print(f"      📄 {section['document_name']} - Page {section['page_number']}")
    
    return output_path

def main():
    """Main function to process PDF documents with semantic analysis."""
    print("🚀 PDF Semantic Document Analyzer")
    print("=" * 50)
    
    # Setup directories
    input_dir, output_dir, models_dir = setup_directories()
    if not input_dir:
        return
    
    print(f"📂 Input:  {input_dir}")
    print(f"📂 Output: {output_dir}")
    print(f"📂 Models: {models_dir}")
    
    # Get user inputs
    try:
        persona, job_description = get_user_inputs()
        
        # Process documents
        result_path = process_documents_pipeline(input_dir, output_dir, models_dir, persona, job_description)
        
        if result_path:
            print(f"\n🎉 Analysis complete! Results saved to: {result_path}")
        else:
            print(f"\n❌ Analysis failed!")
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
