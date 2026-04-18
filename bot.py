#!/usr/bin/env python3
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import logging

# Config
SITEMAPS = [
    "https://zccvawdmicngqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
STORY_DELAY = 210  # 3m30s per story
MAX_STORIES = 120  # Per run (capacity: 120×58=6960/day)
LOG_FILE = "marathon.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                   format='%(asctime)s - %(message)s')

def scrape_story_urls():
    """Extract all <loc> story URLs from sitemaps"""
    urls = set()
    ua = UserAgent()
    
    for sitemap_url in SITEMAPS:
        try:
            headers = {'User-Agent': ua.random}
            resp = requests.get(sitemap_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.content, 'xml')
            
            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                if '/story/' in url and 'storyminta.com' in url:
                    urls.add(url)
                    
            logging.info(f"Scraped {len(urls)} stories from {sitemap_url}")
        except Exception as e:
            logging.error(f"Sitemap {sitemap_url} failed: {e}")
    
    story_list = list(urls)[:MAX_STORIES]
    logging.info(f"Selected {len(story_list)} stories for marathon")
    return story_list

def setup_driver():
    """Headless Chrome with stealth & login persistence"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=' + UserAgent().random)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def login(driver):
    """Multi-method login fallback"""
    methods = [
        # Method 1: Direct email/password
        lambda: driver.get("https://storyminta.com/login") or [
            driver.find_element(By.NAME, "email").send_keys(EMAIL),
            driver.find_element(By.NAME, "password").send_keys(PASSWORD),
            driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        ],
        # Method 2: Google SSO
        lambda: driver.get("https://storyminta.com/auth/google") or [
            time.sleep(2),
            driver.find_element(By.CSS_SELECTOR, "input[type=email]").send_keys(EMAIL),
            driver.find_element(By.ID, ":ra:1").click(),  # Next
            driver.find_element(By.NAME, "password").send_keys(PASSWORD),
            driver.find_element(By.ID, ":ra:1").click()
        ]
    ]
    
    for i, method in enumerate(methods):
        try:
            logging.info(f"Login attempt {i+1}")
            method()
            WebDriverWait(driver, 10).until(
                lambda d: "story" in d.current_url or "dashboard" in d.current_url
            )
            logging.info("✅ Login successful")
            return True
        except:
            driver.delete_all_cookies()
            continue
    
    logging.error("❌ All login methods failed")
    return False

def story_stroll(driver, url):
    """210s realistic browsing pattern"""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda d: "storyminta.com/story" in d.current_url
        )
        
        # Initial scroll & read pattern
        scroll_patterns = [
            ("100vh", 2), ("30vh", 3), ("-20vh", 1), ("50vh", 4),
            ("80vh", 2), ("0vh", 1), ("40vh", 3)
        ]
        
        for scroll, pauses in scroll_patterns:
            driver.execute_script(f"window.scrollBy(0, {scroll});")
            for _ in range(pauses):
                time.sleep(random.uniform(20, 35))  # Natural reading pace
                
                # Micro-interactions (20% chance)
                if random.random() < 0.2:
                    actions = [
                        "window.scrollBy(0, window.innerHeight*0.1);",
                        "window.scrollBy(0, -window.innerHeight*0.05);"
                    ]
                    driver.execute_script(random.choice(actions))
        
        # Final dwell to hit exactly 210s
        elapsed = time.time() - driver.execute_script("return performance.now() / 1000")
        remaining = STORY_DELAY - elapsed
        if remaining > 0:
            time.sleep(remaining)
            
        logging.info(f"✅ Completed {url} ({STORY_DELAY}s)")
        return True
        
    except Exception as e:
        logging.error(f"❌ Story failed {url}: {e}")
        return False

def main():
    stories = scrape_story_urls()
    if not stories:
        logging.error("No stories found!")
        return
    
    driver = setup_driver()
    
    try:
        if login(driver):
            completed = 0
            for i, url in enumerate(stories, 1):
                logging.info(f"[{i}/{len(stories)}] Visiting {url}")
                if story_stroll(driver, url):
                    completed += 1
                
                # Rotate UA every 10 stories
                if i % 10 == 0:
                    driver.quit()
                    time.sleep(random.uniform(30, 60))
                    driver = setup_driver()
                    login(driver)  # Re-auth
            
            logging.info(f"🏁 Marathon complete: {completed}/{len(stories)} stories")
        else:
            logging.error("Login failed - aborting")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
