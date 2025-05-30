# @ Author: Antonio Llorente. Aitea Tech Becarios
# <antoniollorentecuenca@gmail.com>
# @ Project: Cebolla
# @ Create Time: 2025-05-05 10:30:50
# @ Modified time: 2025-09-06 16:17:59
# @ Description:
# This FastAPI router provides endpoints for managing and retrieving RSS feed
# metadata using a PostgreSQL backend. The router supports the following
# operations:
#
# 1. `GET /search-and-insert-rss`: Reads a list of URLs from a local file,
# extracts valid RSS feeds using a scraping routine, and stores the
# resulting metadata (such as feed title and site URL) in the PostgreSQL
# database.
#
# 2. `GET /feeds`: Retrieves a list of RSS feeds stored in the database,
# allowing clients to specify a limit on the number of results returned
# (default: 10).
#
# The module is designed for efficient, asynchronous interaction with the
# database and serves as part of a larger system to collect and organize
# cybersecurity-related feed sources.


import asyncio
import os
import threading
from fastapi import APIRouter, Request, HTTPException
from app.scraping.sipder_rss import extract_rss_and_save
from fastapi import APIRouter, Request, HTTPException, Query
from typing import List
from loguru import logger

from app.models.ttrss_postgre_db import (
    FeedResponse,
    get_feeds_from_db,
)

# Router configuration
router = APIRouter(
    prefix="/postgre-ttrss",
    tags=["Postgre ttrss"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal Server Error"},
    },
)

def background_rss_process_every(pool, file_path: str, loop: asyncio.AbstractEventLoop):
    """
    Executes the RSS extraction and saving task, then schedules the next execution in 25 hours.

    Args:
        pool: PostgreSQL connection pool.
        file_path (str): Path to the file containing URLs to process.
        loop: Main asyncio event loop.
    """
    async def run_task():
        try:
            logger.info("🔍 [RSS] Starting RSS feed extraction and saving...")
            await extract_rss_and_save(pool, file_path)
            logger.success("[RSS] RSS feed extraction and saving completed.")
        except Exception as e:
            logger.error(f"[RSS] Error during RSS extraction and saving: {e}")

    # Ejecuta la corrutina en el loop principal de asyncio de forma segura desde otro hilo
    asyncio.run_coroutine_threadsafe(run_task(), loop)

    # Programa la siguiente ejecución en 25 horas (90000 segundos)
    timer = threading.Timer(300, background_rss_process_every, args=(pool, file_path, loop))
    timer.daemon = True
    timer.start()
    logger.info("[Scheduler] Next RSS extraction scheduled in 25 hours.")



@router.get("/search-and-insert-rss")
async def search_and_insert_rss(request: Request):
    """
    Starts the background process that runs RSS extraction every 25 hours.

    Args:
        request (Request): Incoming HTTP request object.

    Returns:
        dict: Message confirming that the background process has started.

    Raises:
        HTTPException: If the URL file is not found.
    """
    pool = request.app.state.pool
    file_path = "src/data/urls_cybersecurity_ot_it.txt"

    if not os.path.exists(file_path):
        logger.warning("[Startup] URL file not found. Aborting scheduler.")
        raise HTTPException(
            status_code=404,
            detail="URL file not found"
        )

    loop = asyncio.get_running_loop()

    threading.Thread(
        target=background_rss_process_every,
        args=(pool, file_path, loop),
        daemon=True
    ).start()

    logger.info("[Scheduler] Recurring RSS extraction task initialized.")
    return {"message": "Background process started. It will run every 25 hours."}


@router.get("/search-and-insert-rss")
async def search_and_insert_rss(request: Request):
    """
    Starts the background process that runs RSS extraction every 25 hours.

    Args:
        request (Request): Incoming HTTP request object.

    Returns:
        dict: Message confirming that the background process has started.

    Raises:
        HTTPException: If the URL file is not found.
    """
    pool = request.app.state.pool
    file_path = "src/data/urls_cybersecurity_ot_it.txt"

    if not os.path.exists(file_path):
        logger.warning("[Startup] URL file not found. Aborting scheduler.")
        raise HTTPException(
            status_code=404,
            detail="URL file not found"
        )

    threading.Thread(
        target=background_rss_process_every,
        args=(pool, file_path),
        daemon=True
    ).start()

    logger.info("[Scheduler] Recurring RSS extraction task initialized.")
    return {"message": "Background process started. It will run every 25 hours."}




@router.get("/feeds", response_model=List[FeedResponse])
async def list_feeds(
    request: Request,
    limit: int = Query(10, ge=1, le=100)
) -> List[FeedResponse]:
    """
    Retrieve a list of RSS feeds from the PostgreSQL database.

    This endpoint retrieves up to a specified number of RSS feeds from the
    PostgreSQL database. The maximum number of feeds returned can be controlled
    via the `limit` query parameter.

    Args:
        request (Request): Incoming HTTP request object.
        limit (int): The number of feed records to return (default is 10).

    Returns:
        List[FeedResponse]: A list of RSS feed metadata in JSON format.
    """
    logger.info("Fetching up to {} feeds from database.", limit)

    try:
        async with request.app.state.pool.acquire() as conn:
            feeds = await get_feeds_from_db(conn, limit)
            logger.success("Successfully fetched {} feeds.", len(feeds))
            return feeds
    except Exception as e:
        logger.error("Error fetching feeds: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving feeds: {str(e)}"
        )




