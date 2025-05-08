# @ Author: Antonio Llorente. Aitea Tech Becarios

# <antoniollorentecuenca@gmail.com>

# @ Project: Cebolla

# @ Create Time: 2025-05-05 10:30:50

# @ Modified time: 2025-05-06 16:17:59

# @ Description: FastAPI router for managing RSS feeds using PostgreSQL
# backend.

from fastapi import APIRouter, Request, HTTPException, Query
from typing import List
from pydantic import HttpUrl
from loguru import logger
import feedparser

from app.models.ttrss_postgre_db import (
    FeedCreateRequest,
    FeedResponse,
    FeedUrlList,
    get_entry_links,
    get_feeds_from_db,
    insert_feed_to_db
)
from app.scraping.sipder_rss import extraer_rss_y_guardar

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

@router.get("/buscar-e-insertar-rss")
async def buscar_e_insertar_rss(request: Request):
    pool = request.app.state.pool
    ruta_archivo = "src/app/static/docs/urls_ciberseguridad_ot_it.txt"  # Ajusta la ruta si el archivo está en otro lugar
    await extraer_rss_y_guardar(pool, ruta_archivo)
    return {"status": "✅ Feeds procesados correctamente"}


@router.get("/feeds", response_model=List[FeedResponse])
async def list_feeds(
    request: Request,
    limit: int = Query(10, ge=1, le=100)
) -> List[FeedResponse]:
    """
    Retrieve a list of RSS feeds from the PostgreSQL database.

    Args:
        request (Request): Incoming HTTP request object.
        limit (int): Max number of feed records to return (default is 10).

    Returns:
        List[FeedResponse]: List of FeedResponse objects in JSON format.
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




