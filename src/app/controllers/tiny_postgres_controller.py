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
from pydantic import HttpUrl
from loguru import logger
import feedparser
from app.models.ttrss_postgre_db import (
    FeedCreateRequest,
    FeedResponse,
    get_feeds_from_db,
    insert_feed_to_db
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

@router.post("/feeds", response_model=FeedResponse)
async def enter_feed(
    request: Request,
    feed_url: HttpUrl
) -> FeedResponse:
    """
    Parse an RSS feed URL and insert its metadata into the database.

    This endpoint accepts an RSS feed URL, parses the feed's content,
    and inserts its metadata (such as title and site URL) into a PostgreSQL database.

    If the feed is successfully parsed and the entries are found,
    the feed's metadata is saved to the database, and the response contains
    the newly created feed's data.

    Args:
        request (Request): Incoming HTTP request object.
        feed_url (HttpUrl): The RSS feed URL to be processed.

    Returns:
        FeedResponse: The metadata of the newly inserted feed.
    """
    logger.info("Attempting to create feed from URL: {}", feed_url)

    try:
        feed_url_str = str(feed_url)

        feed = feedparser.parse(feed_url_str)

        if not feed.entries:
            logger.warning("No entries found in feed: {}", feed_url_str)
            raise HTTPException(
                status_code=422,
                detail="Unable to retrieve RSS feed entries."
            )

        title = feed.feed.title if 'title' in feed.feed else "Sin título"
        site_url = feed.feed.link if 'link' in feed.feed else "Sin URL del sitio"

        logger.debug("Parsed feed title: '{}', site URL: '{}'", title, site_url)

        owner_uid = 1  # Default user ID
        cat_id = 0     # Default category ID (will be assigned in DB logic)

        feed_data = FeedCreateRequest(
            title=title,
            feed_url=feed_url_str,
            site_url=site_url,
            owner_uid=owner_uid,
            cat_id=cat_id
        )

        async with request.app.state.pool.acquire() as conn:
            logger.info("Inserting feed into database.")
            await insert_feed_to_db(conn, feed_data)

            new_feed = await conn.fetchrow(
                "SELECT * FROM ttrss_feeds WHERE feed_url = $1",
                feed_url_str
            )

        logger.success("Feed successfully inserted with ID {}", new_feed['id'])

        response_feed = FeedResponse(
            id=new_feed['id'],
            title=new_feed['title'],
            feed_url=new_feed['feed_url'],
            site_url=new_feed['site_url'],
            owner_uid=new_feed['owner_uid'],
            cat_id=new_feed['cat_id']
        )

        return response_feed

    except Exception as e:
        logger.exception("Failed to insert feed: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error inserting feed: {str(e)}"
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
    file_path = "src/app/static/docs/urls_ciberseguridad_ot_it.txt"
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




