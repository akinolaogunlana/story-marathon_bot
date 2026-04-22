#!/usr/bin/env python3
import time
import random
import requests
import os
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import base64

SUPABASE_URL = "https://zccvawdmicngfqlkxsoc.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjY3Zhd2RtaWNuZ2ZxbGt4c29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5NzkyMDAsImV4cCI6MjA0OTU1NTIwMH0.EfL8q6vW4zKzq8zKzq8zKzq8zKzq8zKzq8zKzq8z"
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

class CreditFarmer:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    def detect_countdown(self):
        """Find countdown timer via multiple methods"""
        countdown_selectors = [
            '[class*="countdown"]', '[class*="timer"]', '[id*="count"]', '[id*="timer"]',
            '.countdown', '.timer', 'div[class*="time"]', 'span[class*="second"]',
            '[data-testid*="countdown"]', '[role="timer"]'
        ]
        
        for selector in countdown_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    text = el.text.strip().lower()
                    if any(word in text for word in ['second', 'minute', 's ', 'm ']) or text.isdigit():
                        print(f"⏱️ Found countdown: {el.text} @ {selector}")
                        return el
            except:
                continue
        return None
    
    def detect_credit_button(self):
        """Find 0.010¢ claim button"""
        button_selectors = [
            '[class*="claim"]', '[class*="credit"]', '[class*="earn"]', '[class*="reward"]',
            'button:has-text("Claim")', 'button:has-text("Credit")', 'button:has-text("Complete")',
            '.btn-claim', '.claim-reward', 'button[class*="green"]'
        ]
        
        for selector in button_selectors:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"💰 Credit button found: {selector}")
                return btn
            except:
                continue
        return None
    
    def computer_vision_click(self, target_text):
        """OCR + click for dynamic buttons"""
        # Screenshot current page
        screenshot = self.driver.get_screenshot_as_png()
        img = cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)
        
        # Simple template matching for text (scale invariant)
        for scale in np.linspace(0.5, 1.5, 20):
            resized = cv2.resize(img, None, fx=scale, fy=scale)
            # Match common credit phrases
            phrases = [target_text.lower(), "claim", "credit", "earn", "0.010"]
            for phrase in phrases:
                # Basic text region detection (green buttons common)
                hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
                green_mask = cv2.inRange(hsv, (40,50,50), (80,255,255))
                contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    x,y,w,h = cv2.boundingRect(cnt)
                    if w*h > 1000:  # Reasonable button size
                        center_x, center_y = x + w//2, y + h//2
                        # Click screen center (scale back)
                        real_x = int(center_x / scale)
                        real_y = int(center_y / scale)
                        ActionChains(self.driver).move_by_offset(real_x, real_y).click().perform()
                        print(f"🎯 CV clicked potential {phrase} button")
                        return True
        return False

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
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def save_screenshot(driver, name):
    screenshot = driver.get_screenshot_as_base64()
    with open(f"/tmp/{name}.png", "wb") as f:
        f.write(base64.b64decode(screenshot))

def retry_with_backoff(func, max_retries=3, backoff=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            wait = (backoff ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
    return None

def is_session_valid(driver):
    try:
        driver.get("https://storyminta.com/sell/profile/akinolaogunlana")
        WebDriverWait(driver, 5).until(
            lambda d: "profile" in d.page_source.lower() or "akinola" in d.page_source.lower()
        )
        return True
    except:
        return False

def login(driver):
    # [Previous robust login code - unchanged for brevity]
    driver.get("https://storyminta.com/auth")
    wait = WebDriverWait(driver, 10)
    
    # Email
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"], input[name="email"]')))
    email_field.clear()
    email_field.send_keys(EMAIL)
    
    # Password + Submit
    password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_field.send_keys(PASSWORD)
    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
    submit_btn.click()
    
    return is_session_valid(driver)

def process_story_with_credit(farmer, story_slug):
    """Full story view + countdown + credit claim"""
    url = f"https://storyminta.com/story/{story_slug}"
    farmer.driver.get(url)
    
    # Wait for story load
    WebDriverWait(farmer.driver, 15).until(
        lambda d: story_slug in d.current_url
    )
    
    credits_earned = 0
    
    # Watch for 210s + check countdown every 30s
    for _ in range(7):  # 210s / 30s = 7 checks
        # Realistic scroll
        farmer.driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
        time.sleep(30)
        
        # Check for countdown
        countdown_el = farmer.detect_countdown()
        if countdown_el:
            print(f"⏱️ COUNTDOWN DETECTED: {countdown_el.text}")
            time.sleep(3)  # Let it complete naturally first
            
            # Try claim button
            claim_btn = farmer.detect_credit_button()
            if claim_btn:
                claim_btn.click()
                credits_earned += 1
                print("💰 CREDIT CLAIMED: +0.010¢")
                time.sleep(2)
            else:
                # CV fallback
                farmer.computer_vision_click("claim")
    
    # Final credit sweep
    if farmer.computer_vision_click("claim") or farmer.computer_vision_click("credit"):
        credits_earned += 1
        print("💰 CV CREDIT CLAIMED")
    
    return credits_earned

def main():
    print("💰 StoryMinta CREDIT FARMER v13.4 - 0.010¢/story")
    
    stories = []
    offset = 0
    while offset < 2000:
        batch = get_stories_api(offset)
        if not batch: break
        stories.extend([s['slug'] for s in batch if s.get('slug')])
        offset += 120
    
    target_stories = stories[:120]
    print(f"📊 Targeting {len(target_stories)} stories for credits")
    
    driver = setup_chrome()
    farmer = CreditFarmer(driver)
    
    try:
        if not is_session_valid(driver):
            login(driver)
        
        total_credits = 0
        for i, slug in enumerate(target_stories):
            credits = process_story_with_credit(farmer, slug)
            total_credits += credits
            print(f"📖 {i+1}/120: {slug} → +{credits} credits")
            time.sleep(random.uniform(3, 6))
        
        earnings = total_credits * 0.010
        print(f"✅ SESSION COMPLETE: {total_credits} credits = ${earnings:.3f}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()