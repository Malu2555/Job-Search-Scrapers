from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LinkedInLoginHandler:
    def __init__(self, chromedriver_path: str = "/usr/local/bin/chromedriver"):
        self.driver = None
        self.chromedriver_path = chromedriver_path
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with human-like settings"""
        chrome_options = Options()
        # Remove headless mode for CAPTCHA handling
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(self.chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(10)
    
    def manual_captcha_handling(self) -> bool:
        """Handle CAPTCHA manually with user intervention"""
        try:
            # Check if CAPTCHA is present
            captcha_elements = self.driver.find_elements(By.CLASS_NAME, "captcha")
            recaptcha_elements = self.driver.find_elements(By.CLASS_NAME, "g-recaptcha")
            challenge_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'challenge')]")
            
            if captcha_elements or recaptcha_elements or challenge_elements:
                print("=" * 50)
                print("🚨 CAPTCHA DETECTED!")
                print("=" * 50)
                print("Please complete the CAPTCHA manually in the browser window.")
                print("Once completed, press ENTER to continue...")
                print("=" * 50)
                
                # Wait for user to complete CAPTCHA
                input("Press ENTER after completing CAPTCHA: ")
                
                # Verify login was successful
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "global-nav"))
                    )
                    logger.info("CAPTCHA handled successfully")
                    return True
                except TimeoutException:
                    logger.warning("CAPTCHA may not be resolved yet")
                    return self.manual_captcha_handling()  # Recursive call for retry
                    
            return True
            
        except Exception as e:
            logger.error(f"Error in CAPTCHA handling: {e}")
            return False
    
    def login_with_retry(self, email: str, password: str, max_attempts: int = 3) -> bool:
        """Login with automatic CAPTCHA detection and handling"""
        for attempt in range(max_attempts):
            try:
                logger.info(f"Login attempt {attempt + 1}/{max_attempts}")
                
                # Navigate to login page
                self.driver.get("https://www.linkedin.com/login")
                time.sleep(2)
                
                # Enter credentials
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email_input.clear()
                email_input.send_keys(email)
                
                password_input = self.driver.find_element(By.ID, "password")
                password_input.clear()
                password_input.send_keys(password)
                
                # Click login button
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                
                # Wait a moment for potential CAPTCHA
                time.sleep(3)
                
                # Check for CAPTCHA and handle it
                if self.check_for_captcha():
                    logger.info("CAPTCHA detected, handling...")
                    if not self.manual_captcha_handling():
                        continue  # Try again
                else:
                    # Wait for successful login
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "global-nav"))
                    )
                
                logger.info("Login successful!")
                return True
                
            except TimeoutException:
                logger.warning(f"Login attempt {attempt + 1} timed out")
                if attempt < max_attempts - 1:
                    print(f"Retrying... ({attempt + 2}/{max_attempts})")
                    time.sleep(5)
                continue
                
            except Exception as e:
                logger.error(f"Login attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    print(f"Retrying... ({attempt + 2}/{max_attempts})")
                    time.sleep(5)
                continue
        
        logger.error("All login attempts failed")
        return False
    
    def check_for_captcha(self) -> bool:
        """Check if CAPTCHA is present on the page"""
        try:
            # Common CAPTCHA indicators
            captcha_indicators = [
                "captcha",
                "recaptcha",
                "challenge",
                "security check",
                "verify you're human"
            ]
            
            page_source = self.driver.page_source.lower()
            
            for indicator in captcha_indicators:
                if indicator in page_source:
                    return True
            
            # Check for specific elements
            try:
                self.driver.find_element(By.CLASS_NAME, "g-recaptcha")
                return True
            except NoSuchElementException:
                pass
                
            try:
                self.driver.find_element(By.ID, "captcha")
                return True
            except NoSuchElementException:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for CAPTCHA: {e}")
            return False
    
    def safe_navigation(self, url: str) -> bool:
        """Navigate safely after login, handling any additional challenges"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # Check for additional security challenges
            if self.check_for_captcha():
                logger.info("Additional security challenge detected")
                return self.manual_captcha_handling()
            
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

# Alternative approach: Session-based login (more reliable)
class LinkedInSessionManager:
    """Manage LinkedIn sessions to reduce login frequency"""
    
    def __init__(self):
        self.session_cookies = None
        self.last_login_time = None
    
    def save_session(self, driver):
        """Save session cookies for reuse"""
        self.session_cookies = driver.get_cookies()
        self.last_login_time = time.time()
        logger.info("Session saved")
    
    def load_session(self, driver):
        """Load saved session cookies"""
        if not self.session_cookies:
            return False
            
        # Check if session is still valid (less than 24 hours old)
        if self.last_login_time and (time.time() - self.last_login_time) > 86400:
            logger.info("Session expired")
            return False
        
        try:
            driver.get("https://www.linkedin.com")
            for cookie in self.session_cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            
            # Verify session is still active
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "global-nav"))
                )
                logger.info("Session loaded successfully")
                return True
            except TimeoutException:
                logger.warning("Saved session invalid")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False

# Usage example:
def main():
    """Example usage with CAPTCHA handling"""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    # Initialize login handler
    login_handler = LinkedInLoginHandler()
    session_manager = LinkedInSessionManager()
    
    try:
        # Try to load previous session first
        if session_manager.load_session(login_handler.driver):
            print("Using saved session - no login required!")
        else:
            # Perform login with CAPTCHA handling
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if login_handler.login_with_retry(email, password):
                # Save session for future use
                session_manager.save_session(login_handler.driver)
                print("Login successful!")
            else:
                print("Login failed after all attempts")
                return
        
        # Now you can safely navigate and scrape
        if login_handler.safe_navigation("https://www.linkedin.com/jobs/"):
            print("Ready to scrape jobs!")
            # Continue with your scraping logic...
        
    except Exception as e:
        logger.error(f"Main process failed: {e}")
    
    finally:
        # Keep browser open for manual inspection if needed
        # login_handler.close()
        pass

if __name__ == "__main__":
    main()