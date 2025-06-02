# @ Author: Antonio Llorente. Aitea Tech Becarios
# <antoniollorentecuenca@gmail.com>
# @ Project: Cebolla
# @ Create Time: 2025-05-05 10:30:50
# @ Modified time: 2025-06-02 10:29:59
# @ Description:
# This FastAPI router provides endpoints for managing and executing a dynamic
# news scraping system. It includes functionality to:
#
# - Submit and validate RSS feed URLs (e.g., from Google Alerts),
# - Trigger asynchronous scraping tasks using dynamic spiders,
# - Schedule periodic scraping jobs to extract cybersecurity-related news,
# - Automatically collect and process links from RSS feeds into structured data,
# - Store or retrieve data using a PostgreSQL backend,
# - Initiate recurring background jobs that execute every 24 hours.
#
# The system is built for asynchronous execution and integrates file I/O,
# background scheduling with threads, structured error handling, and persistent
# feed metadata storage for reliable news data collection.

import os
import feedparser
import asyncio
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.models.pydantic import FeedUrlRequest, SaveLinkResponse
from app.scraping.feeds_gd import run_dorks_continuously
from app.scraping.spider_factory import run_dynamic_spider_from_db
from loguru import logger
import threading

from app.controllers.google_alerts_pages import fetch_and_save_alert_urls

router = APIRouter(
    prefix="/newsSpider",
    tags=["News spider"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal Server Error"},
    },
)

LINKS_FILE = Path("src/data/google_alert_rss.txt")

@router.post("/save-feed-google-alerts", response_model=SaveLinkResponse)
async def guardar_link(feed_req: FeedUrlRequest) -> SaveLinkResponse:
    '''
    @brief Endpoint to save a new RSS feed URL along with its title.

    This asynchronous POST endpoint receives a feed URL in the request body,
    validates the feed by parsing it with `feedparser`, and extracts the feed t
    itle.    If the feed is invalid or contains no entries, it raises an HTTP 4
    00 error.

    Upon successful validation, it appends the feed URL and title to a
    designated file.

    @param feed_req: Request body containing the feed URL (FeedUrlRequest model).
    @return: A response indicating success with the saved URL and feed title
    (SaveLinkResponse).
    @raises HTTPException: If the feed is invalid or cannot be parsed.
    '''
    url = str(feed_req.feed_url)

    try:
        # Parsear el feed con feedparser
        feed = feedparser.parse(url)

        if not feed.entries:
            raise ValueError("No se encontraron entradas en el feed")

        title = feed.feed.get("title", "Sin título")

    except Exception as e:
        raise HTTPException(
                status_code=400,
                detail=f"Error validando el feed: {e}"
            )

    # Guardar si todo va bien
    LINKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LINKS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url} | {title}\n")

    return SaveLinkResponse(
            message="Link guardado correctamente",
            link=feed_req.feed_url, title=title
        )


@router.get("/scrape-news")
async def scrape_news_articles(request: Request) -> dict[str, str]:
    """
    Endpoint to start the news scraping process using the dynamic spider.

    This function:
    - Retrieves the PostgreSQL connection pool from the app state.
    - Launches the dynamic spider asynchronously in the background.
    - Returns an immediate success message while the process runs.

    Args:
        request (Request): The incoming HTTP request object, with access to
                           the app's state (DB connection pool).

    Returns:
        dict[str, str]: A dictionary with the operation status message.

    Raises:
        HTTPException: If an error occurs during scraping, a 500 status code
                       exception is raised.
    """
    try:
        pool = request.app.state.pool
        # Run the spider function asynchronously in the background
        asyncio.create_task(run_dynamic_spider_from_db(pool))
        return {"status": "✅ News processing started"}
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


@router.get("/start-google-alerts-scheduler")
async def start_google_alert_scheduler(request: Request) -> JSONResponse:
    """
    @brief Starts the recurring Google Alerts scraping scheduler.

    @details
    This endpoint initializes a background thread that runs a recurring scraping
    task every 24 hours. The task reads Google Alerts RSS feed URLs from a local
    file and processes them using a dynamic spider.

    The actual scraping is handled by the `recurring_google_alert_scraper` function,
    which is called in a background thread. The function re-schedules itself
    every 24 hours using a timer.

    If the RSS feeds file is missing, the request fails with a 404 error.

    @param request: The FastAPI request object, used to access the current event loop.

    @return JSONResponse: A message indicating that the scraping process was successfully scheduled.

    @throws HTTPException: If the RSS feeds file is not found on disk.
    """
    feeds_path = "src/data/google_alert_rss.txt"
    if not os.path.exists(feeds_path):
        logger.warning("[Startup] Archivo google_alert_rss.txt no encontrado. Abortando scheduler.")
        raise HTTPException(status_code=404, detail="Archivo google_alert_rss.txt no encontrado")

    loop = asyncio.get_running_loop()

    threading.Thread(
        target=recurring_google_alert_scraper,
        args=(loop,),
        daemon=True
    ).start()

    logger.info("[Scheduler] Tarea recurrente de Google Alerts iniciada correctamente.")
    return JSONResponse(
        content={"message": "Proceso de scraping de Google Alerts iniciado. Se ejecutará cada 24 horas."},
        status_code=200
    )


def recurring_google_alert_scraper(loop: asyncio.AbstractEventLoop) -> None:
    """
    @brief Periodically updates Google Alerts feeds from a local file.

    @details
    This function performs the following tasks:
    - Synchronously extracts Google Alerts RSS feed URLs from a local file by calling
      `fetch_and_save_alert_urls()`.
    - Logs success or failure of the feed update.
    - Reschedules itself to run again in 24 hours using a daemon thread timer.

    Note:
    This function only updates the feed URLs source. The actual scraping and processing
    of news articles should be handled separately (e.g., by the `scrape_news_articles` endpoint).

    @param loop: The main FastAPI event loop (required for consistency, but not used here).

    @return None
    """
    try:
        logger.info("[Google Alerts] Extrayendo feeds desde archivo...")
        fetch_and_save_alert_urls()

        logger.success("[Feeds] Feeds de Google Alerts actualizados.")
    except Exception as e:
        logger.error(f"[Feeds] Error al extraer feeds: {e}")

    # Repetir en 24h
    timer = threading.Timer(86400, recurring_google_alert_scraper, args=(loop,))
    timer.daemon = True
    timer.start()
    logger.info("[Scheduler] Próxima actualización de feeds en 24h")


@router.get("/scrapy/feeds/discover")
async def start_scraping_scheduler(request: Request) -> dict[str, str]:
    """
    @brief Starts a recurring background task to scrape feeds using predefined dorks.

    @details
    This endpoint launches a background thread that:
    - Executes the `run_dorks_continuously()` scraping routine.
    - Reschedules itself to repeat the scraping every 24 hours (86400 seconds).
    - Runs asynchronously and does not block the main FastAPI event loop.

    @param request: FastAPI request object, required to access the event loop.

    @return dict[str, str]: Status message indicating the scheduler has started.
    """
    loop = asyncio.get_running_loop()

    threading.Thread(
        target=background_scraping_every,
        args=(loop,),
        daemon=True
    ).start()

    logger.info("[Scheduler] Scraping programado para ejecutarse cada 24 horas.")
    return {"message": "Scraping iniciado. Se repetirá automáticamente cada 24 horas."}


def background_scraping_every(loop: asyncio.AbstractEventLoop) -> None:
    """
    @brief Executes the dorks-based scraping task and reschedules itself every 24 hours.

    @details
    - This function is intended to run in a separate daemon thread.
    - It uses the provided event loop to run the async scraping function
      `run_dorks_continuously()` inside a thread-safe coroutine context.
    - After the scraping is completed (or an error occurs), it sets a timer to
      call itself again after 86400 seconds (24 hours).

    @param loop: The main asyncio event loop to safely run asynchronous scraping logic from a thread.

    @return None
    """
    try:
        logger.info("🔍 [Scraper] Iniciando scraping con run_dorks_continuously()...")
        # Si run_dorks_continuously es async, llama así:
        future = asyncio.run_coroutine_threadsafe(run_dorks_continuously(), loop)
        future.result()  # espera a que termine (opcional)

        logger.success("[Scraper] Scraping completado.")
    except Exception as e:
        logger.error(f"[Scraper] Error durante el scraping: {e}")

    # Reprogramar ejecución dentro de 24 horas (86400 segundos)
    timer = threading.Timer(86400, background_scraping_every, args=(loop,))
    timer.daemon = True
    timer.start()
    logger.info("[Scheduler] Próxima ejecución de scraping programada en 24 horas.")
