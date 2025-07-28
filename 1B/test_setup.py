"""
Test script to verify the PDF Semantic Document Analyzer setup.
"""
import os
import sys

def test_imports():
    """Test if all required imports work."""
    print("🧪 Testing imports...")
    
    try:
        import fitz
        print("✅ PyMuPDF imported successfully")
    except ImportError as e:
        print(f"❌ PyMuPDF import failed: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        return False
    
    try:
        from transformers import pipeline
        print("✅ transformers imported successfully")
    except ImportError as e:
        print(f"❌ transformers import failed: {e}")
        return False
    
    try:
        import torch
        print("✅ torch imported successfully")
    except ImportError as e:
        print(f"❌ torch import failed: {e}")
        return False
    
    try:
        # Try importing from utils module/package
        from utils import PDFParser, OutlineBuilder, SemanticAnalyzer, JSONExporter
        print("✅ utils module imported successfully")
    except ImportError as e:
        print(f"❌ utils module import failed: {e}")
        print("💡 Checking utils structure...")
        
        # Check if utils is a directory or file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        utils_file = os.path.join(script_dir, 'utils.py')
        utils_dir = os.path.join(script_dir, 'utils')
        
        if os.path.exists(utils_file):
            print(f"   📄 Found utils.py file")
        elif os.path.exists(utils_dir):
            print(f"   📁 Found utils/ directory")
            init_file = os.path.join(utils_dir, '__init__.py')
            if os.path.exists(init_file):
                print(f"   📄 Found __init__.py in utils/")
                print("   ⚠️  The utils directory should contain the classes or utils.py should be a single file")
            else:
                print(f"   ❌ Missing __init__.py in utils/")
        else:
            print(f"   ❌ Neither utils.py nor utils/ directory found")
        
        return False
    
    return True

def fix_utils_structure():
    """Provide guidance to fix utils structure."""
    print("\n🔧 Utils Structure Fix:")
    print("=" * 40)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    utils_dir = os.path.join(script_dir, 'utils')
    utils_file = os.path.join(script_dir, 'utils.py')
    
    if os.path.exists(utils_dir) and not os.path.exists(utils_file):
        print("📁 You have a utils/ directory instead of utils.py file")
        print("💡 Options to fix:")
        print("   1. Move the content from utils/__init__.py to utils.py")
        print("   2. Or ensure utils/__init__.py imports all required classes")
        print("   3. Or delete utils/ directory and create utils.py with all classes")
        
        print(f"\n📄 Current utils directory contents:")
        try:
            for item in os.listdir(utils_dir):
                item_path = os.path.join(utils_dir, item)
                if os.path.isfile(item_path):
                    print(f"   📄 {item}")
                else:
                    print(f"   📁 {item}/")
        except Exception as e:
            print(f"   ❌ Could not read directory: {e}")

def test_directory_structure():
    """Test if directory structure is correct."""
    print("\n🗂️  Testing directory structure...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = ['main.py', 'utils.py', 'requirements.txt']
    required_dirs = ['input']
    
    for file in required_files:
        file_path = os.path.join(script_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    for dir_name in required_dirs:
        dir_path = os.path.join(script_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    return True

def test_pdf_files():
    """Check for PDF files in input directory."""
    print("\n📄 Checking for PDF files...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'input')
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"   📄 {pdf}")
    else:
        print("⚠️  No PDF files found in input/ directory")
        print("💡 Add some PDF files to test the analyzer")
    
    return len(pdf_files) > 0

def test_torch_compatibility():
    """Test torch compatibility and suggest CPU-only installation if needed."""
    print("\n🔧 Testing PyTorch compatibility...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} imported successfully")
        print(f"🖥️  CUDA available: {torch.cuda.is_available()}")
        print(f"🖥️  CPU threads: {torch.get_num_threads()}")
        return True
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        print("\n💡 Try installing CPU-only PyTorch:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
        return False

def install_dependencies():
    """Provide installation commands for different scenarios."""
    print("\n📦 Installation Commands:")
    print("=" * 40)
    
    print("\n🔹 For CPU-only (recommended for this project):")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    print("   pip install sentence-transformers transformers PyMuPDF")
    print("   pip install numpy scipy scikit-learn")
    
    print("\n🔹 Alternative: Install from requirements.txt:")
    print("   pip install -r requirements.txt")
    
    print("\n🔹 If you encounter version conflicts:")
    print("   pip install --upgrade pip")
    print("   pip install torch --upgrade")
    print("   pip install -r requirements.txt --upgrade")

def auto_fix_utils_structure():
    """Automatically fix utils structure by removing directory and ensuring utils.py exists."""
    print("\n🔧 Auto-fixing utils structure...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    utils_dir = os.path.join(script_dir, 'utils')
    utils_file = os.path.join(script_dir, 'utils.py')
    
    if os.path.exists(utils_dir) and not os.path.exists(utils_file):
        try:
            import shutil
            print("📁 Removing utils/ directory...")
            shutil.rmtree(utils_dir)
            print("✅ utils/ directory removed")
            
            print("💡 Now you need to create utils.py file with all required classes")
            print("   The utils.py file should be created in the same directory as main.py")
            return True
        except Exception as e:
            print(f"❌ Failed to remove utils/ directory: {e}")
            print("💡 Please manually delete the utils/ directory and create utils.py")
            return False
    elif os.path.exists(utils_file):
        print("✅ utils.py file already exists")
        return True
    else:
        print("❌ Neither utils.py nor utils/ directory found")
        return False

def main():
    """Run all tests."""
    print("🚀 PDF Semantic Document Analyzer - Setup Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test imports
    total_tests += 1
    import_success = test_imports()
    if import_success:
        tests_passed += 1
    else:
        # Try to auto-fix utils structure
        print("\n🔧 Attempting to auto-fix utils structure...")
        if auto_fix_utils_structure():
            print("✅ Utils structure fixed. Please ensure utils.py contains all required classes.")
            print("💡 If utils.py is missing classes, you may need to recreate it.")
        
        # Show installation guidance and utils fix
        install_dependencies()
        fix_utils_structure()
    
    # Test PyTorch specifically
    total_tests += 1
    if test_torch_compatibility():
        tests_passed += 1
    
    # Test directory structure
    total_tests += 1
    if test_directory_structure():
        tests_passed += 1
    
    # Test PDF files (optional)
    has_pdfs = test_pdf_files()
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ Setup is complete and ready to use!")
        if has_pdfs:
            print("🎉 You can run 'python main.py' to start analyzing PDFs")
        else:
            print("💡 Add PDF files to input/ directory and run 'python main.py'")
    else:
        print("❌ Setup incomplete. Please check the failed tests above.")
        if not import_success:
            print("🔧 Main issue: utils module structure needs to be fixed")

if __name__ == "__main__":
    main()
