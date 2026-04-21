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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging

# === CONFIG ===
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

SITEMAP_URLS = [
    "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]

PROFILE_URL = "https://storyminta.com/sell/profile/akinolaogunlana"
TIME_PER_STORY = 210
MAX_STORIES = 120

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class StoryBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.stories = []

    def get_stories(self):
        urls = set()
        for sitemap in SITEMAP_URLS:
            try:
                logging.info(f"Fetching {sitemap}")
                r = requests.get(sitemap, timeout=15)
                soup = BeautifulSoup(r.content, 'xml')

                for loc in soup.find_all('loc'):
                    url = loc.text.strip()
                    if '/story/' in url:
                        urls.add(url)

            except Exception as e:
                logging.error(e)

        self.stories = list(urls)[:MAX_STORIES]
        logging.info(f"{len(self.stories)} stories loaded")

    def create_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 20)

    def is_logged_in(self):
        try:
            self.driver.get(PROFILE_URL)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if "login" in self.driver.current_url.lower():
                return False

            return True
        except:
            return False

    def login(self):
        logging.info("Logging in...")
        self.create_driver()

        self.driver.get("https://storyminta.com/login")

        try:
            email = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type=email]")
            ))
            password = self.driver.find_element(By.CSS_SELECTOR, "input[type=password]")

            email.clear()
            email.send_keys(EMAIL)

            password.clear()
            password.send_keys(PASSWORD)

            self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

            # wait for redirect
            time.sleep(5)

            if self.is_logged_in():
                logging.info("Login successful")
                return True

        except Exception as e:
            logging.error(f"Login error: {e}")

        return False

    def visit_story(self, url, num):
        try:
            if not self.is_logged_in():
                logging.warning("Session expired, re-login")
                self.driver.quit()
                if not self.login():
                    return False

            logging.info(f"[{num}] Visiting {url}")
            start = time.time()

            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Simulated reading
            while time.time() - start < TIME_PER_STORY:
                scroll = random.randint(200, 600)
                self.driver.execute_script(f"window.scrollBy(0, {scroll});")

                time.sleep(random.uniform(5, 12))

            logging.info(f"[{num}] Done")
            return True

        except Exception as e:
            logging.error(e)
            self.driver.save_screenshot(f"error_{num}.png")
            return False

    def run(self):
        self.get_stories()

        if not self.stories:
            return

        if not self.login():
            logging.error("Login failed")
            return

        success = 0

        for i, story in enumerate(self.stories, 1):
            if self.visit_story(story, i):
                success += 1

            time.sleep(random.uniform(8, 15))  # human-like gap

        logging.info(f"Completed: {success}/{len(self.stories)}")


if __name__ == "__main__":
    StoryBot().run()
