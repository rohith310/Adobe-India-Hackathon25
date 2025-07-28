# Adobe Outline Extractor

This script extracts titles and headings from PDF files using PyMuPDF. It analyzes font sizes, styles, and formatting to identify document structure.

## What it does

- Extracts document title (from filename)
- Identifies headings based on font size, bold formatting, and ALL CAPS text
- Outputs both JSON and human-readable text files
- Creates hierarchical outline with page numbers

## How to Run

### Option 1: Local Python (Recommended for testing)

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create directories and add PDFs:**
   ```bash
   mkdir input output
   # Copy your PDF files to the input folder
   ```

3. **Run the script:**
   ```bash
   python main.py
   ```

### Option 2: Docker

#### Prerequisites
- Docker

#### Build and Run

1. **Build the Docker image:**
   ```bash
   docker build -t adobe-outline-extractor .
   ```

2. **Create input directory and add PDFs:**
   ```bash
   mkdir input
   # Copy your PDF files to the input directory
   ```

3. **Run the container:**
   ```bash
   docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" adobe-outline-extractor
   ```

## Output

For each PDF file `document.pdf`, the script creates:
- `document_outline.json` - Structured JSON with detailed metadata
- `document_outline.txt` - Human-readable hierarchical outline

## Troubleshooting

- **"No PDF files found"**: Make sure PDF files are in the `input` directory
- **Empty outline**: The PDF might have uniform formatting - the script will still extract bold/caps text
- **Docker permission issues**: Ensure the input/output directories have proper permissions

## How it works

1. Analyzes all text in the PDF to identify font patterns
2. Assigns heading levels based on font size (larger = higher level)
3. Uses additional heuristics: bold text, ALL CAPS, and text length
4. Filters out duplicates and very long text (likely paragraphs)
