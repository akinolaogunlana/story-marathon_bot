import asyncio
import random
import time
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

class MobileViewer:
    def __init__(self, config):
        self.config = config
        self.ua = UserAgent()
    
    async def launch_stealth_browser(self):
        self.playwright = await async_playwright().start()
        browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': self.config.MOBILE_WIDTH, 'height': self.config.MOBILE_HEIGHT},
            user_agent=self.ua.random,
            locale='en-US'
        )
        
        page = await context.new_page()
        await self._apply_stealth(page)
        return browser, page
    
    async def _apply_stealth(self, page):
        """Apply anti-detection measures"""
        await page.add_init_script("""
            // Remove webdriver property
            delete navigator.__proto__.webdriver;
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Mock plugins and languages
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
    
    async def login(self, page):
        """Login to StoryMinta"""
        try:
            await page.goto("https://storyminta.com/login", wait_until="networkidle")
            await page.fill('input[type="email"]', self.config.EMAIL)
            await page.fill('input[type="password"]', self.config.PASSWORD)
            await page.click('button:has-text("Login"), button[type="submit"]')
            await page.wait_for_url("**/dashboard**", timeout=15000)
            logger.info("✅ Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def view_story(self, page, story_url: str):
        """View story with natural mobile behavior"""
        try:
            await page.goto(story_url, wait_until="networkidle")
            logger.info(f"📖 Viewing: {story_url}")
            
            start_time = time.time()
            while time.time() - start_time < self.config.VIEW_DURATION:
                # Natural scroll
                scroll_y = random.randint(100, 400)
                await page.evaluate(f"window.scrollBy(0, {scroll_y})")
                
                # Random mouse movements
                if random.random() < 0.4:
                    x, y = random.randint(50, 350), random.randint(200, 700)
                    await page.mouse.move(x, y)
                
                await asyncio.sleep(random.uniform(1, 3))
            
            logger.info("✅ Story viewing completed")
            return True
            
        except Exception as e:
            logger.error(f"Story view failed {story_url}: {e}")
            return False