import logging
import random
import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

OUTPUT_FILE = "src/data/urls_cybersecurity_ot_it.txt"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
]

DORKS = [
    'inurl:rss cybersecurity',
    'inurl:feed "ot security"',
    'filetype:xml "industrial control systems"',
    'inurl:rss "scada breach"',
    'inurl:feed "ics security"',
    'site:.gov "cisa alert" inurl:feed',
    'site:.org "ot cybersecurity" inurl:rss',
    'inurl:rss ciberseguridad',
    'inurl:feed "seguridad OT"',
    'filetype:xml "sistemas de control industrial"',
    'inurl:rss "incidente SCADA"',
    'inurl:feed "seguridad ICS"',
    'site:.gob "alerta CISA" inurl:feed',
    'site:.org "ciberseguridad industrial" inurl:rss',
]

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def simulate_human_behavior(driver):
    actions = ActionChains(driver)
    for _ in range(random.randint(2, 5)):
        driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
        sleep(random.uniform(1, 3))
    sleep(random.uniform(2, 5))


def search_feeds_google_selenium(query, max_results=20, pages=2):
    user_agent = random.choice(USER_AGENTS)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)
    results = set()

    try:
        for page in range(pages):
            start = page * 10
            url = f"https://www.google.com/search?q={query}&hl=es&lr=lang_es&start={start}"
            driver.get(url)
            simulate_human_behavior(driver)

            links = driver.find_elements(By.CSS_SELECTOR, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and re.search(r"(rss|feed|\.xml)", href, re.IGNORECASE):
                    results.add(href)
                if len(results) >= max_results:
                    break

            sleep(random.uniform(2, 5))
    except Exception as e:
        logging.error(f"[Scraper] Error in query '{query}': {e}")
    finally:
        driver.quit()

    return results


def save_to_file(urls, path=OUTPUT_FILE):
    existing_urls = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing_urls.update([line.strip() for line in f.readlines()])
    except FileNotFoundError:
        pass

    new_urls = urls - existing_urls
    if new_urls:
        with open(path, "a", encoding="utf-8") as f:
            for url in new_urls:
                f.write(url + "\n")
        logging.info(f"[Scraper] Saved {len(new_urls)} new URLs in {path}")
    else:
        logging.info("[Scraper] No new URLs found to save.")


# ✅ Main function to be triggered once (repeated externally every 24h)
async def run_dorks_once():
    logging.info("[Scraper] Starting dorks scraping cycle...")
    total_urls = set()
    random.shuffle(DORKS)

    for dork in DORKS:
        logging.info(f"[Scraper] Running dork: {dork}")
        urls = search_feeds_google_selenium(dork)
        total_urls.update(urls)
        sleep(random.uniform(10, 20))  # Wait between dorks to avoid bans

    save_to_file(total_urls)
    logging.info("[Scraper] Dorks scraping cycle finished.")
