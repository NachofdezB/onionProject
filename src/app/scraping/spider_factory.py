from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from app.models.ttrss_postgre_db import get_entry_links
from multiprocessing import Process
import time
import logging
from scrapy.utils.log import configure_logging

# Clase base para spider dinámico
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

# Función que ejecuta el spider en un subproceso
def correr_spider_dinamico(urls):
    # Configura el logging para que no genere logs de Scrapy
    configure_logging(install_root_handler=False)
    logging.getLogger('scrapy').propagate = False
    logging.getLogger().setLevel(logging.CRITICAL)

    SpiderDinamico = crear_spider_dinamico(urls)

    process = CrawlerProcess(settings={
        "LOG_ENABLED": False,  # Desactiva los logs de Scrapy explícitamente
        "FEEDS": {
            "resultado.json": {
                "format": "json",
                "overwrite": True,
                "encoding": "utf8"
            }
        }
    })
    process.crawl(SpiderDinamico)
    process.start()

# Función que ejecuta el spider de forma continua
def ejecutar_spider_dinamico_desde_db(pool):
    async def run():
        while True:
            async with pool.acquire() as conn:
                urls = await get_entry_links(conn)
                if not urls:
                    print("No se encontraron URLs para procesar.")
                    return

                # Ejecuta el proceso en segundo plano con multiprocessing
                p = Process(target=correr_spider_dinamico, args=(urls,))
                p.start()
                p.join()  # Úsalo solo para esperar que el proceso termine, pero sigue el bucle

            # Espera un poco antes de volver a ejecutar el scraping
            print("Esperando para la próxima ejecución...")
            time.sleep(60)  # Espera 1 minuto antes de volver a ejecutar el scraping

    return run()
