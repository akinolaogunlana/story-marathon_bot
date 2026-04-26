import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from supabase import create_client, Client
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credentials
EMAIL = "akinolaogunlana5@gmail.com"
PASSWORD = "73466892Ak"
SUPABASE_URL = "https://zccvawdmicngfqlkxsoc.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjY3Zhd2RtaWNuZ2ZxbGt4c29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5NzkyMDAsImV4cCI6MjA0OTU1NTIwMH0.EfL8q6vW4zKzq8zKzq8zKzq8zKzq8zKzq8zKzq8z"
SITEMAP_URL = "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap"
TARGET_SITE = "https://storyminta.com"

class StoryViewerBot:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, API_KEY)
        self.driver = None
        self.stories = []
        self.session = requests.Session()
        
    def setup_driver(self):
        """Setup undetected Chrome with mobile emulation"""
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36')
        
        # Mobile emulation
        mobile_emulation = {
            "deviceMetrics": { 
                "width": 360, 
                "height": 740, 
                "pixelRatio": 3.0 
            },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.maximize_window()
        
    def fetch_sitemap_stories(self):
        """Fetch all story URLs from Supabase sitemap"""
        try:
            logger.info("Fetching sitemap from Supabase...")
            response = self.session.get(SITEMAP_URL)
            if response.status_code == 200:
                # Parse XML sitemap
                root = ET.fromstring(response.content)
                ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                # Extract URLs from sitemap
                urls = []
                for url_elem in root.findall('.//sitemap:url/sitemap:loc', ns):
                    story_url = url_elem.text
                    if story_url and 'story' in story_url.lower():
                        urls.append(story_url)
                
                self.stories = list(set(urls))  # Remove duplicates
                logger.info(f"Found {len(self.stories)} unique stories")
                return True
        except Exception as e:
            logger.error(f"Sitemap fetch failed: {e}")
            return False
    
    def login(self):
        """Login to storyminta.com"""
        try:
            self.driver.get(TARGET_SITE)
            wait = WebDriverWait(self.driver, 10)
            
            # Wait for login button and click
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login') or contains(text(),'Sign in')]")))
            login_btn.click()
            
            # Enter email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email") or (By.XPATH, "//input[@type='email']")))
            email_field.clear()
            email_field.send_keys(EMAIL)
            
            # Enter password
            password_field = self.driver.find_element(By.NAME, "password") or self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            # Submit login
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            
            # Wait for login success (check for dashboard or stories page)
            time.sleep(3)
            if "dashboard" in self.driver.current_url or "stories" in self.driver.current_url.lower():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - check credentials")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def simulate_natural_behavior(self):
        """Simulate realistic mobile user interactions"""
        actions = [
            lambda: self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);"),
            lambda: self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);"),
            lambda: self.driver.execute_script("window.scrollTo(0, 0);"),
            lambda: self.random_click(),
            lambda: self.random_pause()
        ]
        
        for _ in range(random.randint(8, 15)):  # 8-15 interactions per story
            action = random.choice(actions)
            try:
                action()
            except:
                pass
            time.sleep(random.uniform(1.5, 4.5))
    
    def random_click(self):
        """Random safe click on page elements"""
        elements = self.driver.find_elements(By.TAG_NAME, "div") + self.driver.find_elements(By.TAG_NAME, "span")
        safe_elements = [el for el in elements if el.size['height'] > 20 and el.size['width'] > 20]
        if safe_elements:
            element = random.choice(safe_elements[:10])  # Limit to first 10 for safety
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.driver.execute_script("arguments[0].click();", element)
    
    def random_pause(self):
        """Random pause mimicking reading"""
        time.sleep(random.uniform(2, 6))
    
    def view_story(self, story_url):
        """View individual story with natural engagement"""
        try:
            logger.info(f"Viewing story: {story_url}")
            self.driver.get(story_url)
            
            # Wait for story to load
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Simulate 3 minutes of natural engagement
            start_time = time.time()
            while time.time() - start_time < 180:  # 3 minutes
                self.simulate_natural_behavior()
                remaining = 180 - (time.time() - start_time)
                if remaining > 0:
                    logger.info(f"Story progress: {remaining/60:.1f} minutes remaining")
            
            logger.info(f"Completed story: {story_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to view story {story_url}: {e}")
            return False
    
    def run(self):
        """Main execution loop"""
        try:
            self.setup_driver()
            
            # Login first
            if not self.login():
                logger.error("Cannot proceed without successful login")
                return
            
            # Fetch stories from sitemap
            if not self.fetch_sitemap_stories():
                logger.error("Cannot fetch stories from sitemap")
                return
            
            # View all stories
            successful = 0
            for i, story in enumerate(self.stories, 1):
                logger.info(f"Processing story {i}/{len(self.stories)}")
                if self.view_story(story):
                    successful += 1
                
                # Random delay between stories (2-5 minutes)
                delay = random.uniform(120, 300)
                logger.info(f"Waiting {delay/60:.1f} minutes before next story...")
                time.sleep(delay)
            
            logger.info(f"Completed! Successfully viewed {successful}/{len(self.stories)} stories")
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    # Install required packages first:
    # pip install undetected-chromedriver supabase selenium requests lxml
    
    bot = StoryViewerBot()
    bot.run()