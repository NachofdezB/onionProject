# @ Author: Antonio Llorente. Aitea Tech Becarios

# <antoniollorentecuenca@gmail.com>

# @ Project: Cebolla

# @ Create Time: 2025-05-05 10:30:50

# @ Modified time: 2025-05-06 16:17:59

# @ Description: Module for handling operations on RSS feed entries in Tiny
# Tiny RSS using PostgreSQL. Provides data models for input/output and database
#functions to retrieve and insert feeds.

from typing import List
from pydantic import BaseModel, HttpUrl
from asyncpg import Connection
from fastapi import HTTPException


class FeedCreateRequest(BaseModel):
    """
    Pydantic model for validating input when creating a new RSS feed.
    """
    feed_url: HttpUrl
    title: str
    site_url: str
    owner_uid: int
    cat_id: int


class FeedResponse(BaseModel):
    """
    Pydantic model for representing RSS feed data returned from the database.
    """
    id: int
    title: str
    feed_url: str
    site_url: str
    owner_uid: int
    cat_id: int

class FeedUrlList(BaseModel):
    urls: List[HttpUrl]

async def get_feeds_from_db(
    conn: Connection,
    limit: int
) -> List[FeedResponse]:
    """
    Retrieve a limited number of feed records from the ttrss_feeds table.

    Args:
        conn (Connection): Active database connection.
        limit (int): Maximum number of feeds to retrieve.

    Returns:
        List[FeedResponse]: List of feeds as FeedResponse objects.
    """
    rows = await conn.fetch("SELECT * FROM ttrss_feeds LIMIT $1", limit)
    feeds = []
    for row in rows:
        cat_id = row['cat_id'] if isinstance(row['cat_id'], int) else 0
        feed = FeedResponse(
            id=row['id'],
            title=row['title'],
            feed_url=row['feed_url'],
            site_url=row['site_url'],
            owner_uid=row['owner_uid'],
            cat_id=cat_id
        )
        feeds.append(feed)
    return feeds


async def insert_feed_to_db(
    conn: Connection,
    feed: FeedCreateRequest
) -> None:
    """
    Insert a new feed into the ttrss_feeds table. Ensures the feed category
    'Sin clasificar' exists before insertion.

    Args:
        conn (Connection): Active database connection.
        feed (FeedCreateRequest): Data of the feed to insert.

    Raises:
        HTTPException: If insertion fails or constraints are violated.
    """
    try:
        category = await conn.fetchrow("""
            SELECT id FROM ttrss_feed_categories
            WHERE title = 'Sin clasificar'
        """)

        if category:
            cat_id = category['id']
        else:
            await conn.execute("""
                INSERT INTO ttrss_feed_categories (title, owner_uid)
                VALUES ('Sin clasificar', $1)
            """, feed.owner_uid)

            cat_id = await conn.fetchval("""
                SELECT id FROM ttrss_feed_categories
                WHERE title = 'Sin clasificar'
            """)

        await conn.execute("""
            INSERT INTO ttrss_feeds (
                title, feed_url, site_url, owner_uid, cat_id
            ) VALUES ($1, $2, $3, $4, $5)
        """, feed.title, str(feed.feed_url),
             feed.site_url, feed.owner_uid, cat_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al insertar el feed en la base de datos: {str(e)}"
        )


async def get_entry_links(conn: Connection) -> List[str]:
    """
    Retrieve all non-null entry links from the ttrss_entries table.

    Args:
        conn (Connection): Active database connection.

    Returns:
        List[str]: A list of entry URLs from RSS feeds.
    """
    rows = await conn.fetch(
        "SELECT link FROM ttrss_entries WHERE link IS NOT NULL"
    )
    return [row["link"] for row in rows]
