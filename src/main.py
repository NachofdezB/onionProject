# @ Author: Antonio Llorente. Aitea Tech Becarios
# <antoniollorentecuenca@gmail.com>

# @ Create Time: 2025-05-5 12:17:59

# @ Modified time: 2025-05-5 12:17:59

# @ Project: Cebolla

# @ Description: Main entry point for running the application in a development
# environment.
#
# This script contains the methods to save the information in OpenSearch and
# manages the application initialization and database connection pool.
from app.controllers.tiny_postgres_controller import router as postgre_feeds
from app.controllers.scrapy_news_controller import router as newsSpider
from loguru import logger
from fastapi import FastAPI
import asyncpg
import uvicorn


app = FastAPI()

# Include the feeds router (which handles Scrapy-related routes)
app.include_router(postgre_feeds)
app.include_router(newsSpider)

# Create a connection pool for the PostgreSQL database
async def create_pool():
    try:
        logger.info("Database connecting...")
        app.state.pool = await asyncpg.create_pool(
            user='postgres',
            password='password123',
            database='postgres',
            host='127.0.0.1', # ONLY DEVELOPER, PORT EXPOSED DB TINY POSTGRES
            port=5432,
            min_size=5,
            max_size=20
        )

        logger.info("Database connection pool created successfully.")
    except Exception as e:
        logger.error(f"Error creating database connection pool: {str(e)}")
        raise e

# Close the pool when the app is shut down
async def close_pool():
    if hasattr(app.state, "pool"):
        await app.state.pool.close()
        logger.info("Database connection pool closed.")

# Register event handlers OUTSIDE of __main__ block so they are used by uvicorn
app.add_event_handler("startup", create_pool)
app.add_event_handler("shutdown", close_pool)

# Main entry point
if __name__ == '__main__':
    logger.info("Initializing FastAPI application...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

