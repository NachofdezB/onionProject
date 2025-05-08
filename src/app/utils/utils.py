# @ Author: Antonio Llorente. Aitea Tech Becarios
# <antoniollorentecuenca@gmail.com>

# @ Create Time: 2025-05-5 12:17:59

# @ Modified time: 2025-05-5 12:17:59

# @ Project: Cebolla

# @ Description:
'''
@router.post("/feeds/batch", response_model=List[FeedResponse])
async def enter_multiple_feeds(
    request: Request,
    url_list: FeedUrlList  # Usamos el modelo FeedUrlList para recibir la lista de URLs
) -> List[FeedResponse]:
    """
    Recibe una lista de URLs RSS y las inserta en la base de datos si son válidas.
    """
    resultados = []

    for feed_url in url_list.urls:
        try:
            feed_url_str = str(feed_url)
            feed = feedparser.parse(feed_url_str)

            if not feed.entries:
                logger.warning("No entries found in feed: {}", feed_url_str)
                continue

            title = feed.feed.title if 'title' in feed.feed else "Sin título"
            site_url = feed.feed.link if 'link' in feed.feed else "Sin URL del sitio"

            feed_data = FeedCreateRequest(
                title=title,
                feed_url=feed_url_str,
                site_url=site_url,
                owner_uid=1,  # Default
                cat_id=0
            )

            async with request.app.state.pool.acquire() as conn:
                await insert_feed_to_db(conn, feed_data)
                new_feed = await conn.fetchrow(
                    "SELECT * FROM ttrss_feeds WHERE feed_url = $1",
                    feed_url_str
                )

            response_feed = FeedResponse(
                id=new_feed['id'],
                title=new_feed['title'],
                feed_url=new_feed['feed_url'],
                site_url=new_feed['site_url'],
                owner_uid=new_feed['owner_uid'],
                cat_id=new_feed['cat_id']
            )

            resultados.append(response_feed)

        except Exception as e:
            logger.error("Error procesando feed {}: {}", feed_url, e)

    return resultados

@router.post("/feeds", response_model=FeedResponse)
async def enter_feed(
    request: Request,
    feed_url: HttpUrl
) -> FeedResponse:
    """
    Parse an RSS feed URL and insert its metadata into the database.

    Args:
        request (Request): Incoming HTTP request object.
        feed_url (HttpUrl): Validated URL of the RSS feed to be added.

    Returns:
        FeedResponse: The newly created feed's data from the database.
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


@router.get("/entry-links", response_model=List[str])
async def list_entry_links(request: Request):
    """
    Get all available RSS entry links stored in the database.
    """
    try:
        async with request.app.state.pool.acquire() as conn:
            links = await get_entry_links(conn)
            return links
    except Exception as e:
        logger.error(f"Failed to retrieve entry links: {e}")
        raise HTTPException(status_code=500, detail="Database error")

}
'''