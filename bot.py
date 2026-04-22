#!/usr/bin/env python3
import time
import random
import requests
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from urllib.parse import urlparse
import base64

# Supabase API (public anon key)
SUPABASE_URL = "https://zccvawdmicngfqlkxsoc.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjY3Zhd2RtaWNuZ2ZxbGt4c29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5NzkyMDAsImV4cCI6MjA0OTU1NTIwMH0.EfL8q6vW4zKzq8zKzq8zKzq8zKzq8zKzq8zKzq8z"
EMAIL = os.getenv("EMAIL", "akinolaogunlana5@gmail.com")
PASSWORD = os.getenv("PASSWORD", "73466892Ak")

def get_stories_api(offset=0):
    url = f"{SUPABASE_URL}/rest/v1/stories"
    params = {"select": "slug,id,title", "status": "eq.approved", "limit": 120, "offset": offset}
    headers = {"apikey": API_KEY}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def setup_chrome():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    return driver

def save_screenshot(driver, name):
    """Save base64 screenshot for GitHub artifacts"""
    screenshot = driver.get_screenshot_as_base64()
    with open(f"/tmp/{name}.png", "wb") as f:
        f.write(base64.b64decode(screenshot))
    print(f"📸 Screenshot saved: /tmp/{name}.png")

def retry_with_backoff(func, max_retries=3, backoff=2):
    """Exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            wait = (backoff ** attempt) + random.uniform(0, 1)
            print(f"⚠️ Retry {attempt+1}/{max_retries} after {wait:.1f}s: {e}")
            time.sleep(wait)
    return None

def is_session_valid(driver):
    """Check if logged in via profile page + content"""
    try:
        driver.get("https://storyminta.com/sell/profile/akinolaogunlana")
        wait = WebDriverWait(driver, 5)
        
        # Multiple success indicators
        success_indicators = [
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'akinola')]")),
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'profile')] | //*[contains(@class, 'profile')]")),
            lambda d: "profile" in d.page_source.lower() or "sell" in d.current_url
        ]
        
        for indicator in success_indicators:
            try:
                wait.until(indicator)
                print("✅ Session valid")
                return True
            except TimeoutException:
                continue
        
        return False
    except:
        return False

def login(driver):
    """Robust login with explicit waits + multiple selectors"""
    print("🔐 Attempting login...")
    
    def _login_attempt():
        driver.get("https://storyminta.com/auth")
        wait = WebDriverWait(driver, 10)
        
        # Email field - ordered selectors
        email_selectors = [
            'input[type="email"]',
            'input[placeholder*="email"]', 
            'input[name="email"], input[name*="email"]',
            '#email, #user_email',
            'input[autocomplete*="email"]'
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"✅ Found email field: {selector}")
                break
            except TimeoutException:
                continue
        
        if not email_field:
            save_screenshot(driver, "login_email_fail")
            raise Exception("Email field not found")
        
        email_field.clear()
        email_field.send_keys(EMAIL)
        
        # Password field
        password_selectors = [
            'input[type="password"]',
            'input[name="password"], input[name*="password"]',
            '#password, #user_password'
        ]
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                password_field.clear()
                password_field.send_keys(PASSWORD)
                print(f"✅ Found password field: {selector}")
                break
            except:
                continue
        
        # Submit button
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]', 
            '.login-button, .btn-login, button[class*="login"]',
            'button:has-text("Login"), button:has-text("Sign in"), button:has-text("Log in")'
        ]
        
        submit_btn = None
        for selector in submit_selectors:
            try:
                submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                submit_btn.click()
                print(f"✅ Submit clicked: {selector}")
                break
            except TimeoutException:
                continue
        
        if not submit_btn:
            save_screenshot(driver, "login_submit_fail")
            raise Exception("Submit button not found")
        
        return True
    
    return retry_with_backoff(_login_attempt) and is_session_valid(driver)

def realistic_scroll(driver, duration=210):
    """210s human-like scrolling with explicit waits"""
    start_time = time.time()
    scroll_pause = random.uniform(1.5, 3.5)
    
    while time.time() - start_time < duration:
        actions = [
            lambda: driver.execute_script("window.scrollBy(0, window.innerHeight/2);"),
            lambda: driver.execute_script("window.scrollBy(0, -window.innerHeight/3);"),
            lambda: driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        ]
        
        random.choice(actions)()
        
        # Wait for scroll to complete
        time.sleep(0.5)
        x, y = random.randint(100, 800), random.randint(100, 600)
        driver.execute_script(f"document.elementFromPoint({x}, {y}).dispatchEvent(new MouseEvent('mouseover', {{bubbles: true}}));")
        
        time.sleep(scroll_pause)
        scroll_pause = random.uniform(1.2, 4.0)

def main():
    print("🚀 StoryMinta Marathon Bot v13.3 - Enterprise")
    
    # Fast API story fetch
    all_stories = []
    offset = 0
    while offset < 5000:  # Cap for safety
        stories = get_stories_api(offset)
        if not stories:
            break
        all_stories.extend([s['slug'] for s in stories if s.get('slug')])
        offset += 120
        if len(stories) < 120:
            break
    
    target_stories = all_stories[:120]  # 120/run max
    print(f"📊 {len(all_stories)} total stories, targeting {len(target_stories)}")
    
    if not target_stories:
        print("❌ No stories - API down?")
        return
    
    driver = setup_chrome()
    
    try:
        # Session reuse first
        if not is_session_valid(driver):
            if not login(driver):
                print("❌ Login failed after retries")
                save_screenshot(driver, "final_fail")
                return
        
        stories_visited = 0
        for i, slug in enumerate(target_stories):
            try:
                url = f"https://storyminta.com/story/{slug}"
                print(f"📖 [{i+1}/120] {slug}")
                
                driver.get(url)
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                # Verify story loaded
                WebDriverWait(driver, 10).until(
                    lambda d: slug in d.current_url or "story" in d.current_url
                )
                
                realistic_scroll(driver, 210)
                stories_visited += 1
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"⚠️ Story {slug} failed: {e}")
                save_screenshot(driver, f"story_{stories_visited}_fail")
                continue
        
        print(f"✅ SUCCESS: {stories_visited}/120 stories @ 210s each")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()