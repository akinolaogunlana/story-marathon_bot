#!/usr/bin/env python3
import asyncio
import logging
from config import Config
from sitemap_parser import fetch_sitemap_stories
from browser_automation import MobileViewer
from utils import setup_logging, random_delay

async def main():
    setup_logging()
    
    # Validate config
    Config.validate()
    
    # Initialize viewer
    viewer = MobileViewer(Config)
    
    # Launch browser
    browser, page = await viewer.launch_stealth_browser()
    
    try:
        # 1. Login
        if not await viewer.login(page):
            print("❌ Login failed")
            return
        
        # 2. Fetch stories
        stories = await fetch_sitemap_stories(
            Config.SITEMAP_URL, 
            Config.TARGET_DOMAIN
        )
        
        if not stories:
            print("❌ No stories found")
            return
        
        print(f"🚀 Starting to view {len(stories)} stories...")
        
        # 3. View all stories
        for i, story in enumerate(stories, 1):
            print(f"\n[{i}/{len(stories)}] {story}")
            success = await viewer.view_story(page, story)
            
            if success:
                print("✅ Success")
            else:
                print("❌ Failed")
            
            # Delay between stories
            await random_delay(*Config.DELAY_BETWEEN_STORIES)
        
        print("\n🎉 All stories completed!")
        
    finally:
        await browser.close()
        await viewer.playwright.stop()

if __name__ == "__main__":
    asyncio.run(main())