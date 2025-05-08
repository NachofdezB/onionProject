import psycopg2
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from app.models.ttrss_postgre_db import get_entry_links
import asyncio


# Clase base para spiders dinámicos
def crear_spider_dinamico(urls):
    class SpiderDinamico(Spider):
        name = "spider_dinamico"
        start_urls = urls

        def parse(self, response):
            datos = {
                "url": response.url,
                "title": response.css("title::text").get(default="Sin título")
            }

            for tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p"]:
                elementos = response.css(f"{tag}::text").getall()
                elementos_limpios = [e.strip() for e in elementos if e.strip()]
                datos[tag] = elementos_limpios

            yield datos

    return SpiderDinamico


# Función que ejecuta el spider con URLs desde la base de datos
async def ejecutar_spider_dinamico_desde_db(pool):
    try:
        async with pool.acquire() as conn:
            urls = await get_entry_links(conn)

            if not urls:
                print("No se encontraron URLs para procesar.")
                return

            print(f"Ejecutando spider con {len(urls)} URLs...")

            SpiderDinamico = crear_spider_dinamico(urls)

            process = CrawlerProcess(settings={
                "LOG_LEVEL": "ERROR",
                "FEEDS": {
                    "resultado.json": {
                        "format": "json",
                        "overwrite": True,
                        "encoding": "utf8"
                    }
                }
            })
            process.crawl(SpiderDinamico)
            await asyncio.to_thread(process.start)

    except Exception as e:
        print(f"Error al ejecutar el spider: {e}")
