#!/usr/bin/env python3
import time
import random
import requests
import os
import re
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

SUPABASE_URL = "https://zccvawdmicngfqlkxsoc.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjY3Zhd2RtaWNuZ2ZxbGt4c29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5NzkyMDAsImV4cCI6MjA0OTU1NTIwMH0.EfL8q6vW4zKzq8zKzq8zKzq8zKzq8zKzq8zKzq8z"

class ProofOfLifeBot:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.story_views = 0
        self.credits_earned = 0
        self.profile_balance_before = 0
        self.profile_balance_after = 0
    
    def check_balance(self):
        """Get exact account balance from profile"""
        try:
            self.driver.get("https://storyminta.com/sell/profile/akinolaogunlana")
            time.sleep(3)
            
            # Multiple balance selectors
            balance_selectors = [
                '[class*="balance"]', '[class*="earnings"]', '[class*="credits"]',
                '.balance', '.earnings', '$', '0.010', '¢'
            ]
            
            page_text = self.driver.page_source
            for selector in balance_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    text = el.text.strip()
                    if re.match(r'[\$¢]?0?\.\d{1,3}', text) or 'balance' in text.lower():
                        print(f"💳 Balance found: {text}")
                        return float(re.search(r'[\$¢]?([\d.]+)', text).group(1))
            return 0
        except:
            return 0
    
    def full_story_view(self, slug):
        """Complete 210s view + screenshots"""
        url = f"https://storyminta.com/story/{slug}"
        print(f"📖 Viewing: https://storyminta.com/story/{slug}")
        
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(
            lambda d: slug in d.current_url
        )
        
        # PROOF screenshots
        save_screenshot(self.driver, f"proof_view_{self.story_views}_{slug[:8]}")
        
        # 210s realistic reading
        for _ in range(7):  # 30s chunks
            self.driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
            time.sleep(30)
        
        self.story_views += 1
        print(f"✅ 210s complete. Total views: {self.story_views}")
    
    def hunt_countdown(self):
        """Aggressive countdown detection"""
        page_text = self.driver.page_source
        
        # Exact patterns
        if "reward unlocks in" in page_text.lower():
            time_match = re.search(r'in (\d+)s', page_text)
            seconds = int(time_match.group(1)) if time_match else 107
            print(f"🎯 COUNTDOWN: {seconds}s")
            save_screenshot(self.driver, f"countdown_active_{seconds}s")
            return seconds
        
        # Any $0.010 mention
        if "$0.010" in page_text or "0.010" in page_text:
            print("💰 $0.010 mention found!")
            save_screenshot(self.driver, "dollar010_detected")
        
        return None
    
    def verify_credits(self):
        """Before/after balance check"""
        self.profile_balance_before = self.check_balance()
        print(f"💳 Balance BEFORE: ${self.profile_balance_before}")
        
        # Run stories...
        
        self.profile_balance_after = self.check_balance()
        print(f"💳 Balance AFTER:  ${self.profile_balance_after}")
        
        if self.profile_balance_after > self.profile_balance_before:
            gained = self.profile_balance_after - self.profile_balance_before
            self.credits_earned += int(gained * 100)  # Convert to cents
            print(f"🎉 GAINED: ${gained} ({int(gained*100)} credits)")

def save_screenshot(driver, name):
    try:
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"/tmp/{name}_{timestamp}.png"
        screenshot = driver.get_screenshot_as_base64()
        with open(filename, "wb") as f:
            f.write(base64.b64decode(screenshot))
        print(f"📸 PROOF: {filename}")
    except Exception as e:
        print(f"Screenshot failed: {e}")

def get_stories_api(offset=0):
    url = f"{SUPABASE_URL}/rest/v1/stories"
    params = {"select": "slug,id,title", "status": "eq.approved", "limit": 30, "offset": offset}  # Reduced for testing
    headers = {"apikey": API_KEY}
    try:
        r = requests.get(url, params=params, headers=headers)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def setup_chrome():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Latest headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(45)
    return driver

def login(driver):
    print("🔐 Logging in...")
    driver.get("https://storyminta.com/auth")
    wait = WebDriverWait(driver, 20)
    
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]')))
    email_field.send_keys(os.getenv("EMAIL", "akinolaogunlana5@gmail.com"))
    
    password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_field.send_keys(os.getenv("PASSWORD", "73466892Ak"))
    
    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"], .login-btn')))
    submit_btn.click()
    
    # Verify login
    driver.get("https://storyminta.com/sell/profile/akinolaogunlana")
    time.sleep(5)
    save_screenshot(driver, "login_proof")
    print("✅ Login complete")
    return True

def main():
    print("🔍 PROOF OF LIFE v13.8 - Account Verification Mode")
    
    driver = setup_chrome()
    bot = ProofOfLifeBot(driver)
    
    try:
        login(driver)
        
        # Baseline balance
        bot.profile_balance_before = bot.check_balance()
        
        # Get test batch
        stories = []
        offset = 0
        while len(stories) < 10 and offset < 1000:  # Small test batch
            batch = get_stories_api(offset)
            stories.extend([s['slug'] for s in batch if s.get('slug')])
            offset += 30
        
        print(f"📋 Testing {len(stories)} stories...")
        
        for i, slug in enumerate(stories):
            print(f"\n--- Story {i+1}/{len(stories)} ---")
            
            bot.full_story_view(slug)
            countdown = bot.hunt_countdown()
            
            if countdown:
                print(f"⏱️ Waiting {countdown}s for credit...")
                time.sleep(countdown + 5)
            
            time.sleep(5)  # Story gap
        
        # Final balance check
        bot.profile_balance_after = bot.check_balance()
        bot.verify_credits()
        
        print(f"\n🎯 PROOF SUMMARY:")
        print(f"   Views: {bot.story_views}")
        print(f"   Credits: {bot.credits_earned}")
        print(f"   Balance change: ${bot.profile_balance_after - bot.profile_balance_before:.3f}")
        print(f"\n📸 Check GitHub artifacts for screenshots!")
        print(f"🔗 Manual check: https://storyminta.com/sell/profile/akinolaogunlana")
        
    finally:
        save_screenshot(driver, "final_proof")
        driver.quit()

if __name__ == "__main__":
    main()
