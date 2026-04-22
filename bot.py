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

SUPABASE_URL = "https://zccvawdmicngfqlkxsoc.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjY3Zhd2RtaWNuZ2ZxbGt4c29jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5NzkyMDAsImV4cCI6MjA0OTU1NTIwMH0.EfL8q6vW4zKzq8zKzq8zKzq8zKzq8zKzq8zKzq8z"

class DynamicCountdownHandler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
    
    def extract_countdown_time(self):
        """Extracts VARIABLE countdown from "Reward unlocks in 107s" → returns seconds"""
        page_text = self.driver.page_source
        
        # Multiple regex patterns for variable times
        time_patterns = [
            r"reward unlocks in (\d+)s",  # "Reward unlocks in 107s"
            r"unlock in (\d+)s",         # "Unlock in 120s" 
            r"wait (\d+)s",             # "Wait 90s"
            r"time remaining: (\d+)s",   # "Time remaining: 75s"
            r"(\d+)s remaining"         # "107s remaining"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                seconds = int(match.group(1))
                print(f"⏱️ EXTRACTED: {seconds}s countdown")
                save_screenshot(self.driver, f"countdown_{seconds}s")
                return seconds
        
        print("❌ No countdown time found")
        return None
    
    def detect_countdown_active(self):
        """Detects ANY countdown is present"""
        page_text = self.driver.page_source.lower()
        countdown_indicators = [
            "reward unlocks in",
            "earn $0.010",
            "unlock in",
            "s remaining",
            "countdown"
        ]
        
        for indicator in countdown_indicators:
            if indicator in page_text:
                print(f"🎯 COUNTDOWN ACTIVE: {indicator}")
                return True
        return False
    
    def wait_for_unlock(self, countdown_seconds):
        """Smart wait: exact time + random buffer"""
        print(f"⏳ Waiting {countdown_seconds}s + buffer...")
        
        # Exact wait + 3-8s buffer for network/processing
        total_wait = countdown_seconds + random.uniform(3, 8)
        time.sleep(total_wait)
        
        # Refresh to trigger auto-claim
        self.driver.refresh()
        time.sleep(2)
    
    def monitor_auto_claim(self):
        """Wait for "Auto-claiming reward..." """
        start_time = time.time()
        while time.time() - start_time < 20:
            if "auto-claiming" in self.driver.page_source.lower() or "claiming reward" in self.driver.page_source.lower():
                print("🔄 AUTO-CLAIM DETECTED")
                return True
            time.sleep(1.5)
        return False
    
    def confirm_credit_earned(self):
        """Verify "You earned $0.010!" """
        success_indicators = [
            "you earned $0.010",
            "earned $0.010",
            "thanks for reading",
            "$0.010 credit"
        ]
        
        page_text = self.driver.page_source
        for indicator in success_indicators:
            if indicator in page_text.lower():
                print("✅ $0.010 CREDIT CONFIRMED!")
                save_screenshot(self.driver, "credit_success")
                return True
        return False
    
    def process_variable_countdown(self, story_slug):
        """Complete dynamic countdown flow"""
        print(f"\n🔄 {story_slug} - Hunting variable countdown...")
        
        # Scroll a bit first to trigger countdown
        self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)
        
        # Detect + extract time
        if not self.detect_countdown_active():
            print("➡️ No countdown found")
            return False
        
        countdown_time = self.extract_countdown_time()
        if not countdown_time:
            print("❌ Could not parse time")
            return False
        
        # Wait exactly for unlock
        self.wait_for_unlock(countdown_time)
        
        # Monitor claiming
        self.monitor_auto_claim()
        
        # Confirm success
        success = self.confirm_credit_earned()
        
        if success:
            print(f"💰 CREDIT EARNED: {story_slug}")
            return True
        else:
            print(f"⚠️ Flow incomplete: {story_slug}")
            save_screenshot(self.driver, f"fail_{story_slug[:8]}")
            return False

# [Rest unchanged - setup_chrome, login, get_stories_api, etc.]

def main():
    print("💰 DYNAMIC COUNTDOWN FARMER v13.7")
    print("🎯 Handles: 'Reward unlocks in Xs' (107s, 120s, 90s, etc.)")
    
    stories = []
    offset = 0
    while offset < 5000:
        batch = get_stories_api(offset)
        if not batch: break
        stories.extend([s['slug'] for s in batch if s.get('slug')])
        offset += 120
    
    target_stories = stories[:120]
    print(f"📊 Targeting {len(target_stories)} stories")
    
    driver = setup_chrome()
    handler = DynamicCountdownHandler(driver)
    
    try:
        if not is_session_valid(driver):
            login(driver)
        
        credits = 0
        for i, slug in enumerate(target_stories):
            success = handler.process_variable_countdown(slug)
            if success:
                credits += 1
            
            earnings = credits * 0.010
            print(f"[{i+1:3d}/120] {slug[:25]:25} {'💰' if success else '➡️'}  ${earnings:.2f}")
            time.sleep(random.uniform(4, 8))
        
        daily_potential = credits * 0.010 * 58
        print(f"\n🎉 RESULTS:")
        print(f"   Credits: {credits}/120")
        print(f"   This run:  ${credits*0.010:.2f}")
        print(f"   Daily (58x): ${daily_potential:.0f}")
        
    finally:
        save_screenshot(driver, f"summary_{credits}_credits")
        driver.quit()

if __name__ == "__main__":
    main()