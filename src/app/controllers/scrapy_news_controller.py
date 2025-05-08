from fastapi import APIRouter, Request, HTTPException
from loguru import logger
from app.scraping.spider_factory import ejecutar_spider_dinamico_desde_db

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


@router.get("/scrape-news")
async def scrape_news_articles(request: Request):
    """
    Ejecuta un spider Scrapy para extraer contenido de noticias desde la base de datos.
    """
    try:
        pool = request.app.state.pool
        await ejecutar_spider_dinamico_desde_db(pool)

        logger.success("Scraping completado. Datos guardados en resultado.json.")
        return {
            "status": "Scraping completado",
            "message": "Datos guardados en resultado.json"
        }

    except Exception as e:
        logger.error(f"Fallo el scraping: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Fallo al hacer scraping: {str(e)}"
        )
