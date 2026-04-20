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
    "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]
PROFILE_URL = "https://storyminta.com/sell/profile/akinolaogunlana"
EMAIL = os.getenv("EMAIL", "akinolaogunlana5@gmail.com")
PASSWORD = os.getenv("PASSWORD", "73466892Ak")
STORY_DELAY = 210  # 3m30s
MAX_STORIES = 120
LOG_FILE = "marathon.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                   format='%(asctime)s - %(message)s')

def scrape_story_urls():
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
            logging.info(f"Scraped {len(urls)} from {sitemap_url}")
        except Exception as e:
            logging.error(f"Sitemap fail {sitemap_url}: {e}")
    
    return list(urls)[:MAX_STORIES]

def setup_driver():
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

def verify_login_profile(driver):
    """Verify login by checking profile page"""
    try:
        driver.get(PROFILE_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check for profile content (username, stats, etc.)
        page_text = driver.page_source.lower()
        profile_indicators = [
            "akinolaogunlana", "sell", "profile", "stories", "earnings"
        ]
        
        verified = any(indicator in page_text for indicator in profile_indicators)
        logging.info(f"Profile verification: {'✅ PASS' if verified else '❌ FAIL'}")
        return verified
        
    except Exception as e:
        logging.error(f"Profile check failed: {e}")
        return False

def login(driver):
    """Robust login with profile verification"""
    login_methods = [
        # Method 1: Direct form
        lambda: [
            driver.get("https://storyminta.com/login"),
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))),
            driver.find_element(By.NAME, "email").send_keys(EMAIL),
            driver.find_element(By.NAME, "password").send_keys(PASSWORD),
            driver.find_element(By.CSS_SELECTOR, "button[type=submit], input[type=submit], .login-btn").click()
        ],
        # Method 2: Google SSO
        lambda: [
            driver.get("https://storyminta.com/auth/google"),
            time.sleep(2),
            driver.find_element(By.CSS_SELECTOR, "input[type=email], #identifierId").send_keys(EMAIL),
            driver.find_element(By.ID, ":ra:1, .VfPpkd-LgbsSe-OWXEXe-k8S8q").click(),
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))),
            driver.find_element(By.NAME, "password").send_keys(PASSWORD),
            driver.find_element(By.ID, ":ra:1, .VfPpkd-LgbsSe-OWXEXe-k8S8q").click()
        ],
        # Method 3: Profile direct (if session persists)
        lambda: [driver.get(PROFILE_URL)]
    ]
    
    for i, method in enumerate(login_methods):
        try:
            logging.info(f"Login method {i+1}")
            method()
            
            # Wait & verify
            time.sleep(3)
            if verify_login_profile(driver):
                logging.info("✅ Login + profile verified")
                return True
                
        except Exception as e:
            logging.warning(f"Method {i+1} failed: {e}")
            driver.delete_all_cookies()
    
    return False

def story_stroll(driver, url, story_num):
    try:
        logging.info(f"[{story_num}] {url}")
        start_time = time.time()
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            lambda d: "storyminta.com/story" in d.current_url
        )
        
        # Scroll patterns (210s total)
        scrolls = [
            ("window.innerHeight", 2),  # Full page down x2
            ("window.innerHeight * 0.3", 3),  # Smaller scrolls x3
            ("-window.innerHeight * 0.2", 1),  # Back up
            ("window.innerHeight * 0.5", 4),  # Medium scrolls x4
        ]
        
        for scroll_js, count in scrolls:
            for _ in range(count):
                driver.execute_script(f"window.scrollBy(0, {scroll_js});")
                pause = random.uniform(22, 38)
                time.sleep(pause)
                
                # Random micro-movements
                if random.random() < 0.25:
                    micro = random.choice([
                        "window.scrollBy(0, window.innerHeight*0.08)",
                        "window.scrollBy(0, -window.innerHeight*0.03)"
                    ])
                    driver.execute_script(micro)
        
        # Ensure exact 210s
        elapsed = time.time() - start_time
        if elapsed < STORY_DELAY:
            time.sleep(STORY_DELAY - elapsed)
            
        logging.info(f"✅ [{story_num}] Complete ({STORY_DELAY}s)")
        return True
        
    except Exception as e:
        logging.error(f"❌ [{story_num}] {url}: {e}")
        return False

def main():
    logging.info("🚀 Story Marathon v11.1 START")
    stories = scrape_story_urls()
    
    if not stories:
        logging.error("No stories!")
        return
    
    driver = None
    try:
        driver = setup_driver()
        
        if not login(driver):
            logging.error("💥 Login failed")
            return
        
        completed = 0
        for i, url in enumerate(stories, 1):
            success = story_stroll(driver, url, i)
            if success:
                completed += 1
            
            # Session refresh every 15 stories
            if i % 15 == 0:
                logging.info("🔄 Session refresh")
                driver.quit()
                time.sleep(random.uniform(45, 75))
                driver = setup_driver()
                if not login(driver):
                    logging.error("Re-login failed")
                    break
        
        logging.info(f"🏁 FINISH: {completed}/{len(stories)} stories")
        
    except Exception as e:
        logging.error(f"Critical error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
