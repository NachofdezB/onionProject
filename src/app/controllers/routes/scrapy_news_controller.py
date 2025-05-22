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
from app.scraping.spider_factory import run_dynamic_spider_from_db
from loguru import logger

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


@router.get("/feeds")
async def get_news_from_google_alerts(request: Request) -> JSONResponse:
    '''
    @brief Endpoint to trigger extraction and scraping of news URLs from
    Google Alerts.

    This asynchronous GET endpoint initiates the process of fetching and
    saving URLs from Google Alerts RSS feeds, then runs a dynamic spider to
    scrape content from those URLs.

    Logs the start and success of each major step, and handles exceptions by
    returning an HTTP 500 error with the exception details.

    @param request: The incoming HTTP request (Request object).
    @return: A JSON response confirming successful spider execution.
    @raises HTTPException: If any error occurs during fetching or scraping.
    '''
    try:
        logger.info("Iniciando extracción de URLs desde Google Alerts")
        fetch_and_save_alert_urls()

        logger.info("Iniciando scraping de contenido desde las URLs extraídas")
        run_dynamic_spider_from_db("news_content_spider")

        return JSONResponse(
                content={"message": "Spiders ejecutados correctamente"},
                status_code=200
            )

    except Exception as e:
        logger.error(f"Error al ejecutar spiders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result.json")
async def get_result_json():
    """
    Endpoint to retrieve the result.json file.

    This function attempts to return the `result.json` file from the server's
    file system. If the file is not found, it raises a 404 error.

    Returns:
        FileResponse: The `result.json` file if it exists.

    Raises:
        HTTPException: If the `result.json` file does not exist, a 404 status
                       code is raised.
    """
    file_path = "src/outputs/result.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='application/json')