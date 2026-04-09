# test_structure.py
import os
import sys

print("Current working directory:", os.getcwd())
print("Script location:", os.path.abspath(__file__))
print("Parent directory:", os.path.dirname(os.path.abspath(__file__)))

# Try to import from scraper directory
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper'))
    import linkedin_auth # type: ignore
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")