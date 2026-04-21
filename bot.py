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

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

SITEMAP_URLS = [
    "https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap",
    "https://storyminta.com/sitemap.xml"
]

PROFILE_URL = "https://storyminta.com/sell/profile/akinolaogunlana"

# ⚡ SPEED BOOST: reduce runtime drastically
TIME_PER_STORY = 90   # was 210 → now 90 seconds (FAST MODE)
MAX_STORIES = 60      # reduce workload for CI speed

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class StoryBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.stories = []
        self.logged_in = False

    # ---------- DRIVER ----------
    def create_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")

        # ⚡ speed boost flags
        options.page_load_strategy = "eager"

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        self.wait = WebDriverWait(self.driver, 15)

    # ---------- STORIES ----------
    def get_stories(self):
        urls = set()

        for sitemap in SITEMAP_URLS:
            try:
                r = requests.get(sitemap, timeout=10)
                soup = BeautifulSoup(r.content, "xml")

                for loc in soup.find_all("loc"):
                    url = loc.text.strip()
                    if "/story/" in url:
                        urls.add(url)

            except Exception as e:
                logging.error(e)

        self.stories = list(urls)[:MAX_STORIES]
        logging.info(f"{len(self.stories)} stories loaded")

    # ---------- LOGIN ----------
    def login(self):
        try:
            logging.info("Logging in...")

            self.driver.get("https://storyminta.com/login")

            email = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
            )
            password = self.driver.find_element(By.CSS_SELECTOR, "input[type=password]")

            email.send_keys(EMAIL)
            password.send_keys(PASSWORD)

            self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

            time.sleep(3)

            self.logged_in = self.is_logged_in()

            if self.logged_in:
                logging.info("Login successful")
            else:
                logging.warning("Login failed")

            return self.logged_in

        except Exception as e:
            logging.error(f"Login error: {e}")
            return False

    # ---------- SESSION CHECK ----------
    def is_logged_in(self):
        try:
            self.driver.get(PROFILE_URL)
            time.sleep(2)

            return "login" not in self.driver.current_url.lower()

        except:
            return False

    # ---------- AUTO RECOVERY ----------
    def ensure_login(self):
        if not self.logged_in or not self.is_logged_in():
            logging.warning("Re-login triggered...")
            self.driver.quit()
            self.create_driver()
            return self.login()
        return True

    # ---------- STORY VIEW ----------
    def visit_story(self, url, i):
        try:
            if not self.ensure_login():
                return False

            logging.info(f"[{i}] Visiting story")

            self.driver.get(url)
            time.sleep(2)

            start = time.time()

            # ⚡ faster, more efficient reading simulation
            while time.time() - start < TIME_PER_STORY:
                self.driver.execute_script(
                    "window.scrollBy(0, arguments[0]);",
                    random.randint(300, 700)
                )

                time.sleep(random.uniform(4, 8))  # faster cycle

            logging.info(f"[{i}] Done")
            return True

        except Exception as e:
            logging.error(e)
            return False

    # ---------- RUN ----------
    def run(self):
        self.get_stories()

        if not self.stories:
            return

        self.create_driver()

        if not self.login():
            return

        success = 0

        for i, story in enumerate(self.stories, 1):
            if self.visit_story(story, i):
                success += 1

            # ⚡ shorter break = faster runtime
            time.sleep(random.uniform(3, 6))

        logging.info(f"Completed {success}/{len(self.stories)}")


if __name__ == "__main__":
    StoryBot().run()
