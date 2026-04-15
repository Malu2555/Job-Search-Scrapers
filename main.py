import sys
import os
from pathlib import Path

# Add scraper directory to path
project_dir = Path(__file__).parent
scraper_dir = project_dir / "Scraper"
sys.path.insert(0, str(scraper_dir))

# Now import works
from .Scraper.job_scraper import LinkedInJobScraper

if __name__ == "__main__":
    scraper = LinkedInJobScraper()
    scraper.login()  # or whatever your main function is