# src/app/controllers/scrapy_news_controller.py
from fastapi import APIRouter, Request, HTTPException
from app.scraping.spider_factory import ejecutar_spider_dinamico_desde_db
from loguru import logger

router = APIRouter(prefix="/newsSpider", tags=["News spider"])

@router.get("/scrape-news")
async def scrape_news_articles(request: Request):
    try:
        pool = request.app.state.pool
        await ejecutar_spider_dinamico_desde_db(pool)
        return {"status": "✅ Noticias procesadas correctamente"}
    except Exception as e:
        logger.error(f"Fallo el scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Fallo al hacer scraping: {str(e)}")
