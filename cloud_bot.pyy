#!/usr/bin/env python3
"""
StoryMinta Auth Cloud Bot v9.1 - GitHub Actions
Account: akinolaogunlana5@gmail.com | 73466892Ak
3:30/story + SCROLL + Login
"""
import requests,re,time,json,os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

def login(driver):
    """Login with your credentials"""
    try:
        print("🔐 Logging in...")
        driver.get("https://storyminta.com/login")
        
        # Wait for email field
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field.send_keys("akinolaogunlana5@gmail.com")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("73466892Ak")
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)
        print("✅ Logged in as akinolaogunlana5@gmail.com")
    except:
        print("⚠️ Login skipped (public mode)")

def main():
    s=requests.Session()
    stories=list(set(sum([re.findall(r'<loc>(https://storyminta[^<]+story[^<]+)</loc>',s.get(u).text,re.I)for u in["https://storyminta.com/sitemap.xml","https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap"]],[])))
    
    Path("stats").mkdir()
    print(f"🚀 Auth Bot: {len(stories)} stories | 3:30 each | akinolaogunlana5@gmail.com")
    
    opts=Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    driver=webdriver.Chrome(options=opts)
    
    # LOGIN FIRST
    login(driver)
    
    visited=0
    for i,url in enumerate(stories[:102]):  # MAX GitHub capacity
        print(f"\n🕐 [{i+1}/102] {url.split('/')[-1]}")
        driver.get(url)
        time.sleep(2)
        
        start=time.time()
        scroll_count=0
        
        # 3:30 SCROLL MARATHON
        while time.time()-start<210:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            # Scroll up
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            scroll_count+=1
            
            pct=int((time.time()-start)/210*100)
            print(f"⏳ {pct}% | {int((210-(time.time()-start))//60)}:{int((210-(time.time()-start))%60):02d} | Scrolls: {scroll_count}")
        
        visited+=1
    
    driver.quit()
    
    # Stats
    stats={"account":"akinolaogunlana5@gmail.com","visited":visited,"total":len(stories),"scrolls":scroll_count}
    with open("stats/progress.txt","w") as f:f.write(f"{visited}/{len(stories)}")
    with open("stats/stats.json","w") as f:json.dump(stats,f,indent=2)
    print(f"✅ CLOUD RUN COMPLETE: {visited} stories | Next in 30min")

if __name__=='__main__':main()
