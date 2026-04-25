#!/usr/bin/env python3
import time
import random
import requests
import re
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import base64
from datetime import datetime
from io import StringIO

# YOUR EXACT CONFIG
EMAIL = os.getenv("EMAIL", "akinolaogunlana5@gmail.com")
PASSWORD = os.getenv("PASSWORD", "73466892Ak")
SITEMAP_URLS = [
    "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]
SUPABASE_URL = "https://zccvawdmicngfqlkxsoc.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjY3Zhd2RtaWNuZ2ZxbGt4c29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5NzkyMDAsImV4cCI6MjA0OTU1NTIwMH0.EfL8q6vW4zKzq8zKzq8zKzq8zKzq8zKzq8zKzq8z"

class UltimateCreditBot:
    def __init__(self, driver):
        self.driver = driver
        self.views = 0
        self.credits = 0
    
    def parse_sitemaps(self):
        """Parse YOUR sitemap URLs"""
        stories = set()
        
        for url in SITEMAP_URLS:
            print(f"🗺️ Parsing sitemap: {url}")
            try:
                r = requests.get(url, timeout=15)
                if "xml" in r.text.lower():
                    # XML parsing
                    root = ET.fromstring(r.content)
                    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        loc = url_elem.text
                        if "/story/" in loc:
                            slug = loc.split("/story/")[1].rstrip('/')
                            stories.add(slug)
                else:
                    # JSON sitemap
                    data = r.json()
                    stories.update([item.get('slug', item.get('loc', '')) for item in data])
            except Exception as e:
                print(f"Sitemap error {url}: {e}")
        
        print(f"📋 Found {len(stories)} stories from sitemaps")
        return list(stories)[:50]  # Limit for testing
    
    def get_supabase_stories(self):
        """Backup API stories"""
        url = f"{SUPABASE_URL}/rest/v1/stories"
        params = {"select": "slug", "status": "eq.approved", "limit": 50}
        headers = {"apikey": API_KEY}
        try:
            r = requests.get(url, params=params, headers=headers)
            return [s['slug'] for s in r.json()]
        except:
            return []
    
    def stealth_view(self, slug):
        """210s stealth story view"""
        url = f"https://storyminta.com/story/{slug}"
        print(f"📖 [{self.views+1}/50] {slug}")
        
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until(lambda d: slug in d.current_url)
        
        # PROOF
        save_screenshot(self.driver, f"view_{self.views}_{slug[:8]}")
        
        # 210s human reading
        for _ in range(7):
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)});")
            time.sleep(30)
        
        self.views += 1
        
        # Force profile refresh every 5 stories
        if self.views % 5 == 0:
            self.driver.get("https://storyminta.com/sell/profile/akinolaogunlana")
            time.sleep(5)
            save_screenshot(self.driver, f"profile_after_{self.views}_views")
    
    def run_marathon(self, stories):
        """Full marathon with sitemap stories"""
        print(f"🏃 Starting {len(stories)} story marathon...")
        
        for slug in stories:
            self.stealth_view(slug)
            time.sleep(random.uniform(5, 12))

def save_screenshot(driver, name):
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"/tmp/proof_{name}_{timestamp}.png"
    try:
        screenshot = driver.get_screenshot_as_base64()
        with open(filename, "wb") as f:
            f.write(base64.b64decode(screenshot))
        print(f"📸 {filename}")
    except:
        pass

def stealth_setup():
    """Ultimate stealth Chrome"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1366,768')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def login(driver):
    print("🔐 Login...")
    driver.get("https://storyminta.com/auth")
    wait = WebDriverWait(driver, 30)
    
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]')))
    email_field.send_keys(EMAIL)
    
    password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_field.send_keys(PASSWORD)
    
    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
    submit_btn.click()
    
    # Profile proof
    time.sleep(5)
    driver.get("https://storyminta.com/sell/profile/akinolaogunlana")
    save_screenshot(driver, "profile_start")
    print("✅ Logged in")

def main():
    print("🚀 v14.0 - YOUR CONFIG + SITEMAP + STEALTH")
    
    driver = stealth_setup()
    bot = UltimateCreditBot(driver)
    
    try:
        login(driver)
        
        # YOUR SITEMAPS FIRST
        sitemap_stories = bot.parse_sitemaps()
        
        # Supabase backup
        api_stories = bot.get_supabase_stories()
        
        all_stories = list(set(sitemap_stories + api_stories))[:50]
        
        bot.run_marathon(all_stories)
        
        print(f"\n🎉 MARATHON COMPLETE:")
        print(f"   Views: {bot.views}")
        print(f"   Sitemap stories: {len(sitemap_stories)}")
        print(f"   API stories: {len(api_stories)}")
        print(f"\n🔍 CHECK: https://storyminta.com/sell/profile/akinolaogunlana")
        
    finally:
        save_screenshot(driver, "final")
        driver.quit()

if __name__ == "__main__":
    main()
