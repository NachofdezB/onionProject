# @ Author: Ignacio Fernandez Belda. Aitea Tech Becarios
# <nachofernandezbelda@gmail.com>

# @ Create Time: 2025-05-5 12:17:59

# @ Modified time: 2025-05-9 20:39:59

# @ Project: Cebolla

# @ Description: This module defines the logic for dynamically scraping web
# pages using Scrapy.
# It includes a factory function that builds a custom Spider class on the fly,
# based on a list of input URLs. The spider extracts key structural content
# such as titles, headers (h1-h6), and paragraph text.
#
# The module also manages the execution of the spider:
# - Once via `run_dynamic_spider()` with a static list of URLs
# - Continuously via `run_dynamic_spider_from_db()`, which pulls fresh URLs
#   from a PostgreSQL database using an asyncpg connection pool.
#
# Extracted data is saved locally in JSON format for further processing or a
# nalysis.
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from app.models.ttrss_postgre_db import get_entry_links
from multiprocessing import Process
import time
import logging
from scrapy.utils.log import configure_logging
from typing import Type, Coroutine, Any

def create_dynamic_spider(urls)-> Type[Spider]:
    """
    Creates a dynamic Scrapy spider class for extracting content from a list
    of URLs.

    This function defines and returns a custom Scrapy Spider class that
    processes each URL by extracting:
      - The page title
      - All text content inside header tags (h1–h6) and paragraph tags (p)

    Args:
        urls (list[str]): A list of URLs to crawl.

    Returns:
        Type[Spider]: A dynamically created Scrapy Spider class.
    """
    class DynamicSpider(Spider):
        name = "dynamic_spider"
        start_urls = urls

        def parse(self, response):
            data = {
                "url": response.url,
                "title": response.css("title::text").get(default="Untitled")
            }

            for tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p"]:
                elements = response.css(f"{tag}::text").getall()
                clean_elements = [e.strip() for e in elements if e.strip()]
                data[tag] = clean_elements

            yield data

    return DynamicSpider

def run_dynamic_spider(urls)-> None:
    """
    Runs a dynamically generated Scrapy spider to scrape content from a list
    of URLs.

    This function sets up logging and Scrapy settings, creates a dynamic
    spider using the provided URLs, and launches a Scrapy crawler process with
    that spider.

    Features configured:
        - Disables default Scrapy logging to avoid console clutter.
        - Sets a realistic user-agent string for better scraping reliability.
        - Enables a download delay and auto-throttling to reduce server load.
        - Configures retries for transient HTTP errors (e.g., 429, 503).
        - Saves scraped data into a local JSON file ("result.json").

    Args:
        urls (list[str]): A list of web URLs to be scraped.
    """
    configure_logging(install_root_handler=False)
    logging.getLogger('scrapy').propagate = False
    logging.getLogger().setLevel(logging.CRITICAL)

    DynamicSpider = create_dynamic_spider(urls)

    process = CrawlerProcess(settings={
        "LOG_ENABLED": False,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        ),
        "DOWNLOAD_DELAY": 2.0,  # 2 seconds between requests
        "AUTOTHROTTLE_ENABLED": True,  # Adjusts delay based on load
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 5,  # Retry failed requests up to 5 times
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504],
        "FEEDS": {
            "result.json": {
                "format": "json",
                "overwrite": True,
                "encoding": "utf8"
            }
        }
    })

    process.crawl(DynamicSpider)
    process.start()


def run_dynamic_spider_from_db(pool)-> Coroutine[Any, Any, None]:
    """
    Creates and returns an asynchronous function that continuously runs the
    dynamic Scrapy spider.

    This function:
    - Periodically acquires URLs from a PostgreSQL connection pool.
    - Spawns a separate process to run a Scrapy spider using those URLs.
    - Waits 60 seconds before repeating the process.

    Args:
        pool (asyncpg.pool.Pool): The asyncpg connection pool for database
        access.

    Returns:
        Callable[[], None]: An asynchronous function that starts the continuous
        spider execution loop.
    """
    async def run()-> None:
        while True:
            async with pool.acquire() as conn:
                urls = await get_entry_links(conn)
                if not urls:
                    print("No URLs found to process.")
                    return

                p = Process(target=run_dynamic_spider, args=(urls,))
                p.start()
                p.join()

            print("Waiting for next run...")
            time.sleep(60)

    return run()
