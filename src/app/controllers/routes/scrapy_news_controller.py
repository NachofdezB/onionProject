# @ Author: Antonio Llorente. Aitea Tech Becarios
# <antoniollorentecuenca@gmail.com>
# @ Project: Cebolla
# @ Create Time: 2025-05-05 10:30:50
# @ Modified time: 2025-09-20 10:29:59
# @ Description:This FastAPI router defines endpoints for interacting with a
# dynamic web scraping
#
# system focused on news content. It allows users to:
# - Add and validate new RSS feed URLs (typically from Google Alerts),
# - Trigger a scraping process that extracts real news URLs and content using spiders,
# - Initiate scraping from URLs stored in a PostgreSQL database,
# - Access the final results of scraping via the `result.json` file.
#
# The system integrates asynchronous processing, error handling, and structur

import os
import feedparser
import asyncio
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
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


def recurring_google_alert_scraper() -> None:
    """
    Extrae URLs desde feeds de Google Alerts, ejecuta el spider dinámico,
    y reprograma la tarea para que se ejecute cada 24 horas.
    """
    try:
        logger.info("[Google Alerts] Iniciando extracción de feeds desde google_alert_rss.txt")
        fetch_and_save_alert_urls()

        logger.info("[Spider] Iniciando scraping de contenido desde las URLs extraídas")
        run_dynamic_spider_from_db("news_content_spider")

        logger.success("[Feeds] Proceso de scraping desde Google Alerts finalizado correctamente")

    except Exception as e:
        logger.error(f"[Feeds] Error en el proceso de scraping desde Google Alerts: {e}")

    # Reprogramar después de 24 horas (86400 segundos)
    timer = threading.Timer(86400, recurring_google_alert_scraper)
    timer.daemon = True
    timer.start()
    logger.info("Scheduler] Próxima ejecución del scraping de Google Alerts programada en 24 horas")

@router.get("/start-google-alerts-scheduler")
async def start_google_alert_scheduler() -> JSONResponse:
    """
    Inicia un hilo en segundo plano que ejecuta el scraping de Google Alerts cada 24 horas.

    Returns:
        JSONResponse: mensaje de éxito
    """
    feeds_path = "src/data/google_alert_rss.txt"
    if not os.path.exists(feeds_path):
        logger.warning("[Startup] Archivo google_alert_rss.txt no encontrado. Abortando scheduler.")
        raise HTTPException(
            status_code=404,
            detail="Archivo google_alert_rss.txt no encontrado"
        )

    threading.Thread(
        target=recurring_google_alert_scraper,
        daemon=True
    ).start()

    logger.info("[Scheduler] Tarea recurrente de Google Alerts iniciada correctamente.")
    return JSONResponse(
        content={"message": "Proceso de scraping de Google Alerts iniciado. Se ejecutará cada 24 horas."},
        status_code=200
    )

def background_scraping_every() -> None:
    """
    Ejecuta el scraping una vez y programa el siguiente para dentro de 24 horas.
    """
    try:
        logger.info("🔍 [Scraper] Iniciando scraping con run_dorks_continuously()...")
        run_dorks_continuously()
        logger.success("[Scraper] Scraping completado.")
    except Exception as e:
        logger.error(f"[Scraper] Error durante el scraping: {e}")

    # Reprogramar ejecución dentro de 24 horas
    timer = threading.Timer(8400, background_scraping_every)
    timer.daemon = True
    timer.start()
    logger.info("[Scheduler] Próxima ejecución de scraping programada en 24 horas.")


@router.get("/scrapy/feeds/discover")
async def start_scraping_scheduler() -> dict[str, str]:
    """
    Inicia el scraping en segundo plano, y lo programa para ejecutarse cada 24 horas.
    """
    threading.Thread(
        target=background_scraping_every,
        daemon=True
    ).start()

    logger.info("Scheduler] Scraping programado para ejecutarse cada 24 horas.")
    return {"message": "Scraping iniciado. Se repetirá automáticamente cada 24 horas."}