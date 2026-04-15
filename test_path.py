#!/usr/bin/env python3
"""
Path debugging tool for job scraper project
"""

import sys
import os
from pathlib import Path

def debug_paths():
    """Debug and display all relevant paths"""
    print("=== PATH DEBUGGING TOOL ===\n")
    
    # Current file information
    current_file = Path(__file__).resolve()
    print(f"Current test file: {current_file}")
    print(f"Current file directory: {current_file.parent}")
    
    # Project structure detection
    project_root = current_file.parent
    scraper_dir = project_root / "Scraper"
    
    print(f"\n=== DIRECTORY STRUCTURE ===")
    print(f"Project root: {project_root}")
    print(f"Scraper directory: {scraper_dir}")
    print(f"Scraper directory exists: {scraper_dir.exists()}")
    
    # List contents of scraper directory
    if scraper_dir.exists():
        print(f"\nContents of scraper directory:")
        for item in scraper_dir.iterdir():
            status = "📁" if item.is_dir() else "📄"
            print(f"  {status} {item.name}")
    else:
        print(f"\nLooking for scraper directory in parent directories...")
        # Look up the tree
        for parent in project_root.parents:
            potential_scraper = parent / "Scraper"
            if potential_scraper.exists():
                print(f"Found scraper at: {potential_scraper}")
                break
    
    return project_root, scraper_dir

def test_python_path():
    """Display and test Python path"""
    print(f"\n=== PYTHON PATH ANALYSIS ===")
    print("Current Python path:")
    for i, path in enumerate(sys.path[:10]):  # Show first 10 entries
        marker = "👉" if "scraper" in path.lower() else "  "
        print(f"  {marker} [{i}] {path}")
    
    if len(sys.path) > 10:
        print(f"  ... and {len(sys.path) - 10} more entries")

def test_file_detection(scraper_dir):
    """Check for required files"""
    print(f"\n=== REQUIRED FILES CHECK ===")
    
    required_files = [
        "linkedin_auth.py",
        "job_scraper.py",
        "__init__.py"
    ]
    
    all_found = True
    for filename in required_files:
        file_path = scraper_dir / filename
        exists = file_path.exists()
        status = "✅ FOUND" if exists else "❌ MISSING"
        print(f"  {status} {filename}")
        if exists:
            print(f"    Full path: {file_path}")
        else:
            all_found = False
    
    return all_found

def test_import_methods(scraper_dir):
    """Test different import methods"""
    print(f"\n=== IMPORT METHOD TESTING ===")
    
    # Method 1: Direct sys.path manipulation
    print("Method 1: sys.path manipulation")
    original_path = sys.path.copy()
    
    try:
        if str(scraper_dir) not in sys.path:
            sys.path.insert(0, str(scraper_dir))
        
        import linkedin_auth
        print("  ✅ Direct import successful!")
        
        from .linkedin_auth import LinkedInLoginHandler
        print("  ✅ Class import successful!")
        
        # Restore path
        sys.path[:] = original_path
        return True
        
    except ImportError as e:
        print(f"  ❌ Direct import failed: {e}")
        sys.path[:] = original_path
        return False

def test_relative_imports():
    """Test relative imports"""
    print(f"\n=== RELATIVE IMPORT TESTING ===")
    
    try:
        from Scraper.linkedin_auth import LinkedInLoginHandler
        print("  ✅ Relative import successful!")
        return True
    except ImportError as e:
        print(f"  ❌ Relative import failed: {e}")
        print("    Note: This requires proper package structure and running as module")
        return False

def test_absolute_imports():
    """Test absolute imports"""
    print(f"\n=== ABSOLUTE IMPORT TESTING ===")
    
    try:
        import Scraper.linkedin_auth
        print("  ✅ Absolute import successful!")
        return True
    except ImportError as e:
        print(f"  ❌ Absolute import failed: {e}")
        return False

def suggest_solutions(scraper_dir, files_found):
    """Suggest solutions based on test results"""
    print(f"\n=== SOLUTION SUGGESTIONS ===")
    
    if not scraper_dir.exists():
        print("🔧 Issue: Scraper directory not found")
        print("   Solution: Check your directory structure")
        return
    
    if not files_found:
        print("🔧 Issue: Required files missing")
        print("   Solution: Verify file names and locations")
        return
    
    print("🔧 Try adding this to the top of your job_scraper.py:")
    print("   " + "="*50)
    print('   import sys')
    print('   from pathlib import Path')
    print('   ')
    print(f'   # Add scraper directory to Python path')
    print(f'   scraper_dir = Path(__file__).resolve().parent')
    print(f'   sys.path.insert(0, str(scraper_dir))')
    print('   ')
    print('   # Now imports should work:')
    print('   from linkedin_auth import LinkedInLoginHandler')
    print("   " + "="*50)

def main():
    """Main test function"""
    print("Starting path debugging...\n")
    
    # Debug paths
    project_root, scraper_dir = debug_paths()
    
    # Test Python path
    test_python_path()
    
    # Check for files
    files_found = test_file_detection(scraper_dir)
    
    # Test import methods
    if scraper_dir.exists() and files_found:
        test_import_methods(scraper_dir)
        test_relative_imports()
        test_absolute_imports()
    
    # Provide solutions
    suggest_solutions(scraper_dir, files_found)
    
    print(f"\n=== DEBUG COMPLETE ===")
    print("Run this test with: python test_paths.py")

if __name__ == "__main__":
    main()