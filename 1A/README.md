# Adobe PDF Heading Extractor

This script extracts a clean outline of headings (H1, H2, H3) from PDF files using PyMuPDF. It combines multiple detection strategies including font formatting, positioning, semantic patterns, and visual layout analysis to accurately identify document structure even when font sizes are similar.

## Features

- **Multi-factor heading detection**: Combines font size, formatting (bold/italic), positioning, and semantic patterns
- **Modular architecture**: Separated into focused, reusable components
- **Robust fallback modes**: Works even with uniform font sizes by analyzing text patterns and formatting
- **Smart filtering**: Removes prose fragments, boilerplate text, and non-heading content
- **Isolation detection**: Uses whitespace analysis to identify visually separated headings
- **Pattern recognition**: Recognizes common heading formats (numbered sections, title case, etc.)
- **Hierarchy validation**: Ensures proper H1 > H2 > H3 nesting

## Quick Start

### Local Usage

1. **Install requirements:**
   ```bash
   pip install PyMuPDF
   ```

2. **Add PDFs and run:**
   ```bash
   mkdir input
   # Copy your PDF files to the input folder
   python main.py
   ```

## Architecture

### Modular Design

The system is organized into focused modules for better maintainability:

- **main.py**: Main orchestration and file processing
- **pdf_heading_extractor.py**: Core extraction logic and coordination
- **text_element.py**: Text extraction and element representation
- **heading_patterns.py**: Pattern matching rules and text classification
- **heading_scorer.py**: Scoring algorithms for heading detection
- **document_analyzer.py**: Document structure analysis and context
- **utils.py**: Common utilities and helper functions

### Multi-Factor Detection Algorithm

The extractor uses a scoring system that weighs multiple factors:

1. **Font & Formatting (35%)**
   - Bold text gets higher scores
   - Larger font sizes relative to document average
   - Font family consistency

2. **Text Characteristics (30%)**
   - Optimal heading length (2-12 words)
   - Title case, uppercase formatting
   - Absence of prose indicators

3. **Positioning & Layout (20%)**
   - Left-aligned text
   - Visual isolation (whitespace above/below)
   - Page boundary positioning

4. **Pattern Matching (15%)**
   - Numbered sections (1., 1.1, 1.1.1)
   - Common heading patterns ("Chapter", "Introduction", etc.)
   - Title case with colons ("Section Title:")

### Heading Level Classification

- **H1**: Major sections, chapters, long uppercase titles, mission statements
- **H2**: Numbered sections, medium importance headings, methodologies
- **H3**: Sub-sections, bullet points with colons, numbered subsections

### Advanced Filtering

- **Prose Detection**: Filters out sentences with articles, conjunctions, and action words
- **Fragment Removal**: Eliminates incomplete phrases and sentence fragments
- **Boilerplate Filtering**: Removes headers, footers, and repetitive content
- **Duplicate Prevention**: Avoids similar headings and case-insensitive duplicates

## Output Files

For each PDF `document.pdf`, generates `document.json`:

```json
{
  "title": "document",
  "outline": [
    {"level": "H1", "text": "Your Mission", "page": 1},
    {"level": "H2", "text": "What You Need to Build", "page": 2},
    {"level": "H3", "text": "• Round 1:", "page": 1}
  ]
}
```

## Configuration

The system automatically adapts to document characteristics, but key thresholds include:

- **Minimum heading score**: 0.35 (adjustable in `heading_scorer.py`)
- **Isolation threshold**: 1.2x line height for whitespace detection
- **Text length**: 3-character minimum, 12-word maximum for headings

## Troubleshooting

### Common Issues

- **"No headings detected"**: Check if PDF has extractable text and proper formatting
- **Missing headings**: Lower the score threshold in `heading_scorer.py`
- **Too many false positives**: Increase threshold or enhance patterns in `heading_patterns.py`
- **Import errors**: Ensure all module files are present in the same directory

### Debug Information

The script outputs detailed information during processing:
```
🔍 Document analysis: avg_font=12.0, range=10.0-16.0
✓ H1: 'Your Mission' (page 2, score: 0.75)
✓ H2: 'What You Need to Build' (page 2, score: 0.62)
```

### Performance Notes

- Processes up to 50 pages efficiently
- Samples first 8-15 pages for font analysis
- Memory usage scales with document complexity

## File Structure
```
1A/
├── main.py                    # Main orchestration script
├── pdf_heading_extractor.py   # Core extraction logic
├── text_element.py           # Text extraction utilities
├── heading_patterns.py       # Pattern matching rules
├── heading_scorer.py         # Scoring algorithms
├── document_analyzer.py      # Document analysis
├── utils.py                  # Common utilities
├── input/                    # Place PDF files here
├── output/                   # Generated JSON files (auto-created)
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container setup
└── README.md               # This file
```

## Usage Examples

### Local run:
```bash
python main.py
```

### Docker run:
```bash
docker build -t pdf-heading-extractor .
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" pdf-heading-extractor
```

## Advanced Customization

To modify detection behavior, edit these modules:

- **heading_patterns.py**: Add new semantic patterns for your document types
- **heading_scorer.py**: Adjust scoring weights and thresholds
- **document_analyzer.py**: Modify isolation detection and context analysis
- **text_element.py**: Enhance text extraction for specific PDF formats

## Dependencies

- **PyMuPDF (fitz)**: PDF text extraction and formatting analysis
- **Python 3.7+**: Standard libraries (os, json, re, collections, typing, dataclasses)

## Benefits of Modular Architecture

- **Maintainability**: Each module has a single, focused responsibility
- **Reusability**: Components can be imported and used in other projects
- **Testability**: Each module can be tested independently
- **Extensibility**: New features can be added without modifying existing code
- **Debugging**: Issues can be isolated to specific modules
