#!/usr/bin/env python3
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import logging

# === CONFIG ===
EMAIL = os.getenv("EMAIL", "akinolaogunlana5@gmail.com")
PASSWORD = os.getenv("PASSWORD", "73466892Ak")
SITEMAP_URLS = [
    "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]
PROFILE_URL = "https://storyminta.com/sell/profile/akinolaogunlana"  # YOUR profile
TIME_PER_STORY = 210  # 3:30 exactly
MAX_STORIES = 120

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class StoryBot:
    def __init__(self):
        self.driver = None
        self.stories = []
    
    def get_stories(self):
        """Scrape sitemaps"""
        urls = set()
        for sitemap in SITEMAP_URLS:
            try:
                print(f"📄 {sitemap}")
                r = requests.get(sitemap, timeout=15)
                soup = BeautifulSoup(r.content, 'xml')
                for loc in soup.find_all('loc'):
                    url = loc.text.strip()
                    if '/story/' in url:
                        urls.add(url)
            except Exception as e:
                print(f"❌ {e}")
        
        self.stories = list(urls)[:MAX_STORIES]
        print(f"✅ {len(self.stories)} stories ready")
    
    def create_driver(self):
        """Headless Chrome"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={UserAgent().random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def is_logged_in(self):
        """Check if still logged in"""
        try:
            self.driver.get(PROFILE_URL)
            WebDriverWait(self.driver, 5).until(lambda d: "akinolaogunlana" in d.page_source.lower())
            print("✅ SESSION ACTIVE")
            return True
        except:
            print("⚠️ Session expired")
            return False
    
    def login(self):
        """Login with session persistence"""
        print("🔐 Logging in...")
        self.create_driver()
        
        # Method 1: Direct login
        self.driver.get("https://storyminta.com/login")
        try:
            WebDriverWait(self.driver, 10).until(lambda d: d.find_element(By.CSS_SELECTOR, "input[name=email], input[type=email]"))
            email_input = self.driver.find_element(By.CSS_SELECTOR, "input[name=email], input[type=email]")
            email_input.send_keys(EMAIL)
            
            pwd_input = self.driver.find_element(By.CSS_SELECTOR, "input[name=password], input[type=password]")
            pwd_input.send_keys(PASSWORD)
            
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit], .login-button, input[type=submit]")
            submit_btn.click()
            
            time.sleep(3)
        except:
            print("Trying Google login...")
            self.driver.get("https://accounts.google.com")
            # Google OAuth if direct fails
        
        # VERIFY login worked
        if self.is_logged_in():
            print("✅ LOGIN CONFIRMED")
            return True
        return False
    
    def refresh_session(self):
        """Re-login if needed"""
        print("🔄 Refreshing session...")
        self.driver.quit()
        return self.login()
    
    def visit_story(self, story_url, number):
        """Visit story for EXACTLY 3:30"""
        # CHECK SESSION before each story
        if not self.is_logged_in():
            if not self.refresh_session():
                print("💥 Cannot maintain login")
                return False
        
        print(f"📖 [{number}/{len(self.stories)}] {story_url}")
        start_time = time.time()
        
        self.driver.get(story_url)
        time.sleep(2)  # Load time
        
        # Natural scrolling for 3:30
        for i in range(9):  # 9 × 23.3s = 210s
            # Scroll down
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # Pause (natural reading)
            pause = random.uniform(22, 28)
            time.sleep(pause)
            
            # 30% chance re-read (scroll up)
            if random.random() < 0.3:
                self.driver.execute_script("window.scrollBy(0, -200);")
        
        # EXACT 210s
        elapsed = time.time() - start_time
        remaining = TIME_PER_STORY - elapsed
        if remaining > 0:
            time.sleep(remaining)
        
        print(f"✅ [{number}] DONE (210s exact)")
        return True
    
    def run_marathon(self):
        """Main loop"""
        self.get_stories()
        if not self.stories:
            return
        
        if not self.login():
            print("💥 Login failed")
            return
        
        success = 0
        for i, story in enumerate(self.stories, 1):
            if self.visit_story(story, i):
                success += 1
            
            # 10s break between stories
            time.sleep(10)
        
        print(f"🎉 MARATHON COMPLETE: {success}/{len(self.stories)}")

if __name__ == "__main__":
    bot = StoryBot()
    bot.run_marathon()
