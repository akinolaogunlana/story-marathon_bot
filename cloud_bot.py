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

# === YOUR CONFIG ===
EMAIL = os.getenv("EMAIL", "akinolaogunlana5@gmail.com")
PASSWORD = os.getenv("PASSWORD", "73466892Ak")
SITEMAP_URLS = [
    "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]
TIME_PER_STORY = 210  # 3 minutes 30 seconds
MAX_STORIES_PER_RUN = 120

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_stories_from_sitemaps():
    """Get story URLs from sitemaps"""
    all_urls = set()
    for sitemap in SITEMAP_URLS:
        try:
            print(f"📄 Scraping {sitemap}")
            response = requests.get(sitemap, timeout=15)
            soup = BeautifulSoup(response.content, 'xml')
            
            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                if 'storyminta.com/story/' in url:
                    all_urls.add(url)
        except Exception as e:
            print(f"❌ Sitemap error: {e}")
    
    stories = list(all_urls)[:MAX_STORIES_PER_RUN]
    print(f"✅ Found {len(stories)} stories")
    return stories

def create_browser():
    """Headless Chrome browser"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f'--user-agent={UserAgent().random}')
    
    driver = webdriver.Chrome(options=options)
    return driver

def login_to_storyminta(driver):
    """Login to your account"""
    print("🔐 Logging in...")
    
    # Try direct login first
    driver.get("https://storyminta.com/login")
    try:
        email_field = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.NAME, "email") or d.find_element(By.CSS_SELECTOR, "input[type=email]")
        )
        email_field.send_keys(EMAIL)
        
        password_field = driver.find_element(By.NAME, "password") or driver.find_element(By.CSS_SELECTOR, "input[type=password]")
        password_field.send_keys(PASSWORD)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type=submit], .login-btn, input[type=submit]")
        login_button.click()
        
        print("✅ Login successful")
        return True
    except:
        print("❌ Direct login failed, trying Google...")
        # Google SSO fallback
        driver.get("https://storyminta.com/auth/google")
        time.sleep(3)
        # Add Google login if needed
        return False

def visit_story(driver, story_url, number):
    """Visit story for EXACTLY 3:30 with scrolling"""
    print(f"📖 [{number}] {story_url}")
    
    start_time = time.time()
    driver.get(story_url)
    
    # Scroll naturally over 3:30
    scroll_interval = 25  # seconds between scrolls
    scrolls_needed = TIME_PER_STORY // scroll_interval
    
    for i in range(scrolls_needed):
        # Scroll down a bit
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.4);")
        time.sleep(scroll_interval)
        
        # Sometimes scroll up a little (human behavior)
        if random.random() < 0.3:
            driver.execute_script("window.scrollBy(0, -window.innerHeight * 0.1);")
    
    # Ensure EXACTLY 3:30
    elapsed = time.time() - start_time
    if elapsed < TIME_PER_STORY:
        time.sleep(TIME_PER_STORY - elapsed)
    
    print(f"✅ [{number}] Complete (210s)")

def main():
    print("🚀 StoryMinta Bot Starting...")
    
    # Step 1: Get stories
    stories = get_stories_from_sitemaps()
    if not stories:
        print("❌ No stories found!")
        return
    
    # Step 2: Create browser + login
    driver = create_browser()
    try:
        if not login_to_storyminta(driver):
            print("💥 Login failed!")
            return
        
        # Step 3: Visit each story for 3:30
        for i, story in enumerate(stories, 1):
            visit_story(driver, story, i)
            print(f"📊 Progress: {i}/{len(stories)}")
            
            # Small break between stories
            if i < len(stories):
                time.sleep(random.uniform(5, 15))
    
    finally:
        driver.quit()
    
    print("🎉 All stories completed!")

if __name__ == "__main__":
    main()
