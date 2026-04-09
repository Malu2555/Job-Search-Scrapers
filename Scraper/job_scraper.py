
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import logging
from dotenv import load_dotenv
#Add the scraper directory to python path for imports
scraper_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(scraper_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if scraper_dir not in sys.path:
    sys.path.insert(0, scraper_dir)

# Import the LinkedIn login handler
from .linkedin_auth import LinkedInLoginHandler, LinkedInSessionManager
# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#credentials should be stored in .env file and not hardcoded for security reasons
#since will actually need to login to linkedin
class LinkedInJobScraper:
    def __init__(self):
        self.driver = None
        self.jobs_data = []
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=False")  # open and see browser
        # (if you do not want to see the browser, headless should equal True)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(self.chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def login(self):
        """Login to LinkedIn using environment variables"""
        if not self.email or not self.password:
            logger.error("LinkedIn credentials not found in environment variables")
            return False
            
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter credentials
            email_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            
            email_input.send_keys(self.email)
            password_input.send_keys(self.password)
        
            
            # Click login button
            # Assuming the text inside the span is "Login" (replace with actual text)
            xpath_selector = "//a[contains(@class, 'nav__button-secondary')]//span[contains(text(), 'sign in')]"

            login_button = WebDriverWait(self.driver, 10).until(  EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            login_button.click()
            
        except Exception as e:
         logger.error(f"Login failed: {e}")
        return False
    
    def search_jobs(self, keyword, location):
        """Search for jobs using the LinkedIn search interface"""
        try:    

            self.driver.get("https://www.linkedin.com/jobs/")
            
            # Wait for page to load
            time.sleep(5)
            
            # Enter search keywords
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search by title, skill, or company']"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            
            # Enter location
            location_input = self.driver.find_element(By.XPATH, "//input[@aria-label='City, state, or zip code']")
            location_input.clear()
            location_input.send_keys(location)
            
            # Submit search
            search_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Search']")
            search_button.click()
            
            # Wait for results to load
            time.sleep(5)
            
            logger.info(f"Searching for {keyword} jobs in {location}")
            return True
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False
    
    def scrape_job_listings(self, max_pages=5):
        """Scrape job listings from search results"""
        jobs = []
        
        for page in range(1, max_pages + 1):
            try:
                logger.info(f"Scraping page {page}")
                
                # Wait for job listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list_subtitle"))
                )
                
                # Get job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
                
                for card in job_cards:
                    try:
                        # Extract job details with error handling
                        title_elem = card.find_element(By.CSS_SELECTOR, ".job-card-list__title")
                        company_elem = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
                        location_elem = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__caption")
                        
                        # Try to get salary info (may not always be present)
                        salary_elem = None
                        try:
                            metadata_ul= WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".artdeco-entity-lockup__metadata-wrapper"))
                            )
                            #scroll into view to ensure salary info is loaded
                            self.driver.execute_script("arguments[0].scrollIntoView();", metadata_ul)

                        except NoSuchElementException:
                            pass
                        # collect all scraped data into a dictionary
                        job_data = {
                            'title': title_elem.text if title_elem else 'N/A',
                            'company': company_elem.text if company_elem else 'N/A',
                            'location': location_elem.text if location_elem else 'N/A',
                            'salary': salary_elem.text if salary_elem else 'Not specified',
                            'link': title_elem.get_attribute('href') if title_elem else 'N/A',
                            'scraped_at': pd.Timestamp.now()
                        }
                        #append job data to list of jobs
                        jobs.append(job_data)
                        
                    except NoSuchElementException:
                        continue
                
                # Go to next page if available
                try:
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-search-pagination__button--next"))
                    )
                    next_button.click()
                    time.sleep(5)
                except:
                    logger.info("No more pages to scrape.")
                    break
            except TimeoutException:
                logger.warning(f"Timeout while loading page {page}. Stopping scraper.")
                break
        self.jobs_data = jobs
        logger.info(f"Total jobs scraped: {len(jobs)}")
        return jobs
    
    def clean_data(self):
        """Clean and process scraped data using pandas"""
        if not self.jobs_data:
            logger.warning("No data to clean")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(self.jobs_data)
        #print first few rows of the dataframe to check the data using head() method
        logger.info("Cleaned data preview:")
        logger.info(df.head())
        
        # Remove duplicates based on title and company
        df = df.drop_duplicates(subset=['title', 'company'], keep='first')
        
        # Clean text data
        df['title'] = df['title'].str.strip().str.replace('\n', ' ')
        df['company'] = df['company'].str.strip().str.replace('\n', ' ')
        df['location'] = df['location'].str.strip().str.replace('\n', ' ')
        df['salary'] = df['salary'].str.strip().str.replace('\n', ' ')
        
        # Sort by scraped time
        df = df.sort_values('scraped_at', ascending=False).reset_index(drop=True)
        
        logger.info(f"Cleaned data: {len(df)} unique jobs")
        return df
    
    def save_to_csv(self, filename='linkedin_jobs.csv'):
        """Save data to CSV file"""
        if not self.jobs_data:
            logger.warning("No data to save")
            return
            
        df = self.clean_data()
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        return df
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    """Main function to run the scraper"""
    scraper = LinkedInJobScraper()
    
    try:
        # Setup driver
        scraper.setup_driver()
        
        # Login to LinkedIn
        if scraper.login():
            logger.info("Proceeding with job search...")
        else:
            logger.warning("Proceeding without login (limited results)")
        
        # Search for jobs
        scraper.search_jobs("Data Scientist", "United States")
        
        # Scrape job listings with pagination (max 4 pages)
        max_page = 4
        jobs = scraper.scrape_job_listings(max_pages=max_page)
        logger.info(f"Scraped {len(jobs)} jobs from {max_page} pages")
        
        # Save to  CSV 
        scraper.save_to_csv('data_scientist_jobs.csv')
        
        # Print summary
        if jobs:
            df = pd.DataFrame(jobs)
            print("\n=== Scraping Summary ===")
            print(f"Total jobs scraped: {len(jobs)}")
            print(f"Unique companies: {df['company'].nunique()}")
            print(f"Locations covered: {df['location'].nunique()}")
            
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
    #If you wish  you can give this backend logic a frontend visualization, 
    # it would be great to see the trends in job postings over time, 
    # the distribution of job locations, and the most common skills required for data science roles.