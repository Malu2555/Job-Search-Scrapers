import os
import sys
from pathlib import Path

def test_import_setup():
    """Comprehensive import testing function"""
    
    print("=== IMPORT DIAGNOSTICS ===")
    
    # Current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Script directory (where this file is located)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Python path
    print(f"Python path entries:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5 entries
        print(f"  {i}: {path}")
    
    # List files in current directory
    print(f"\nFiles in current directory:")
    try:
        files = os.listdir(script_dir)
        for file in sorted(files):
            print(f"  {file}")
    except Exception as e:
        print(f"  Error listing files: {e}")
    
    # Check for specific files
    target_files = ['linkedin_login_with_captcha.py', 'supernova_scraper.py']
    print(f"\nChecking for required files:")
    for target_file in target_files:
        file_path = os.path.join(script_dir, target_file)
        exists = os.path.exists(file_path)
        print(f"  {target_file}: {'FOUND' if exists else 'NOT FOUND'}")
        if exists:
            print(f"    Full path: {file_path}")
    
    return script_dir

def test_absolute_import():
    """Test absolute import method"""
    print("\n=== TESTING ABSOLUTE IMPORT ===")
    try:
        import linkedin_login_with_captcha
        print("✓ Absolute import successful!")
        print(f"  Module file: {linkedin_login_with_captcha.__file__}")
        
        # Test if classes exist
        if hasattr(linkedin_login_with_captcha, 'LinkedInLoginHandler'):
            print("✓ LinkedInLoginHandler found")
        else:
            print("✗ LinkedInLoginHandler NOT found")
            
        if hasattr(linkedin_login_with_captcha, 'LinkedInSessionManager'):
            print("✓ LinkedInSessionManager found")
        else:
            print("✗ LinkedInSessionManager NOT FOUND")
            
        return True
    except ImportError as e:
        print(f"✗ Absolute import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_direct_import_classes():
    """Test importing specific classes"""
    print("\n=== TESTING DIRECT CLASS IMPORT ===")
    try:
        from linkedin_login_with_captcha import LinkedInLoginHandler, LinkedInSessionManager
        print("✓ Direct class import successful!")
        print(f"  LinkedInLoginHandler: {LinkedInLoginHandler}")
        print(f"  LinkedInSessionManager: {LinkedInSessionManager}")
        return True
    except ImportError as e:
        print(f"✗ Direct class import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_relative_import():
    """Test relative import method"""
    print("\n=== TESTING RELATIVE IMPORT ===")
    try:
        from .linkedin_login_with_captcha import LinkedInLoginHandler
        print("✓ Relative import successful!")
        return True
    except ImportError as e:
        print(f"✗ Relative import failed: {e}")
        print("  Note: Relative imports require running as module or proper package structure")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_sys_path_method():
    """Test sys.path modification method"""
    print("\n=== TESTING SYS.PATH MODIFICATION ===")
    
    # Add current directory to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        print(f"Added to sys.path: {script_dir}")
    
    try:
        import linkedin_login_with_captcha
        print("✓ sys.path method successful!")
        return True
    except ImportError as e:
        print(f"✗ sys.path method failed: {e}")
        return False

def test_import_all_methods():
    """Test all import methods systematically"""
    print("Starting import diagnostics...\n")
    
    # Setup
    script_dir = test_import_setup()
    
    # Test methods
    results = {}
    results['absolute'] = test_absolute_import()
    results['direct_class'] = test_direct_import_classes()
    results['sys_path'] = test_sys_path_method()
    
    # Only test relative import if we're running as a module
    if __name__ != '__main__':
        results['relative'] = test_relative_import()
    
    # Summary
    print(f"\n=== IMPORT TEST SUMMARY ===")
    for method, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {method}: {status}")
    
    successful_methods = sum(1 for success in results.values() if success)
    print(f"\nSuccessful import methods: {successful_methods}/{len(results)}")
    
    if successful_methods > 0:
        print("✅ At least one import method works!")
    else:
        print("❌ All import methods failed. Check file paths and names.")
    
    return results

if __name__ == "__main__":
    test_import_all_methods()