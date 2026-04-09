#!/usr/bin/env python3
"""
Main entry point for LinkedIn Job Scraper
Automatically detects directory structure
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Automatically setup paths for imports"""
    # Get the directory where this script is located
    current_script_dir = Path(__file__).parent.absolute()
    print(f"Current script directory: {current_script_dir}")
    
    # Look for scraper directory
    scraper_dir = current_script_dir / "scraper"
    if scraper_dir.exists():
        print(f"Found scraper directory: {scraper_dir}")
        # Add scraper directory to Python path
        if str(scraper_dir) not in sys.path:
            sys.path.insert(0, str(scraper_dir))
            print(f"Added to Python path: {scraper_dir}")
    else:
        print("Scraper directory not found!")
        # List what directories we do have
        print("Available directories:")
        for item in current_script_dir.iterdir():
            if item.is_dir():
                print(f"  {item.name}/")
    
    # Also add current directory
    if str(current_script_dir) not in sys.path:
        sys.path.insert(0, str(current_script_dir))
    
    return scraper_dir

def test_file_exists(scraper_dir):
    """Check if required files exist"""
    required_files = [
        "linkedin_login_with_captcha.py",
        "supernova_scraper.py"
    ]
    
    print("\n=== CHECKING REQUIRED FILES ===")
    all_found = True
    for filename in required_files:
        file_path = scraper_dir / filename
        exists = file_path.exists()
        status = "FOUND" if exists else "MISSING"
        print(f"  {filename}: {status}")
        if exists:
            print(f"    Location: {file_path}")
        else:
            all_found = False
    
    return all_found

def main():
    """Main execution function"""
    print("=== LINKEDIN JOB SCRAPER SETUP ===")
    
    # Setup paths
    scraper_dir = setup_paths()
    
    # Check if files exist
    if not test_file_exists(scraper_dir):
        print("\n❌ Required files not found. Please check your directory structure!")
        return
    
    # Try imports
    print("\n=== TESTING IMPORTS ===")
    try:
        # Test importing the login handler
        import linkedin_auth # type: ignore
        print("✅ Successfully imported linkedin_login_with_captcha")
        
        from linkedin_auth import LinkedInLoginHandler, LinkedInSessionManager # type: ignore
        print("✅ Successfully imported LinkedInLoginHandler and LinkedInSessionManager")
        
        # Test importing the scraper
        import job_scraper # type: ignore
        print("✅ Successfully imported job_scraper")
        
        from job_scraper import LinkedInJobScraper # type: ignore
        print("✅ Successfully imported LinkedInJobScraper")
        
        print("\n🎉 All imports successful! Ready to run scraper.")
        
        # Uncomment these lines when you want to actually run the scraper:
        # print("\n🚀 Starting scraper...")
        # scraper = LinkedInJobScraper()
        # scraper.login()  # This will trigger the scraping process
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure file names match exactly (including case)")
        print("2. Ensure all .py files are in the scraper directory")
        print("3. Check that __init__.py files exist where needed")
        print("4. Verify your directory structure matches expected layout")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()