# @ Author: Antonio Llorente. Aitea Tech Becarios

# <antoniollorentecuenca@gmail.com>

# @ Project: Cebolla

# @ Create Time: 2025-05-05 10:30:50

# @ Modified time: 2025-09-06 16:17:59

# @ Description: This FastAPI router provides endpoints for managing RSS feed
# data using a PostgreSQL backend.
# The router includes the following functionalities:
# 1. `POST /feeds`: Accepts an RSS feed URL, parses its content using the
# feedparser library, and inserts its metadata (e.g., title, feed URL, and
# site URL) into the PostgreSQL database.
# 2. `GET /search-and-insert-rss`: Reads a list of URLs from a file and
# processes them to extract and save RSS feed metadata into the database.
# 3. `GET /feeds`: Retrieves a list of RSS feeds stored in the PostgreSQL
# database, with an optional limit on the number of results.
# This module is designed to handle the creation, search, and insertion of
# RSS feeds and their metadata in a structured way, using asynchronous
# database interactions.

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


@router.get("/search-and-insert-rss")
async def search_and_insert_rss(request: Request) -> dict[str, str]:
    """
    Reads URLs from a file, processes them to extract RSS feeds, and stores
    the feed metadata into the PostgreSQL database.

    This endpoint triggers the process to read URLs from a predefined file,
    attempts to extract RSS feed links, and saves the feed metadata into the
    PostgreSQL database.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        dict: A success message indicating that the feeds were processed.
    """
    pool = request.app.state.pool
    file_path = "src/data/urls_ciberseguridad_ot_it.txt"
    await extract_rss_and_save(pool, file_path)
    return {"status": "✅ Feeds successfully processed"}




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




