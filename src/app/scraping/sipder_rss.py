import feedparser
import asyncio
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy.utils.log import configure_logging
from app.models.ttrss_postgre_db import insert_feed_to_db, FeedCreateRequest

# Función para leer las URLs desde un archivo
def leer_urls_desde_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, "r") as archivo:
            urls = [linea.strip() for linea in archivo.readlines()]
        return urls
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

# Crear el Spider para extraer los RSS
def crear_spider_rss(urls, resultados):
    class SpiderRSS(Spider):
        name = "rss_spider"
        start_urls = urls

        def parse(self, response):
            for link in response.css("link"):
                href = link.attrib.get("href", "")
                tipo = link.attrib.get("type", "")
                rel = link.attrib.get("rel", "")

                # Detectar feeds RSS o Atom
                if "rss" in tipo or "atom" in tipo or "application/xml" in tipo:
                    full_url = response.urljoin(href)
                    if full_url not in resultados:
                        resultados.append(full_url)
                        print(f"RSS encontrado: {full_url}")
    return SpiderRSS

# Función para extraer RSS y guardar en la base de datos
async def extraer_rss_y_guardar(pool, archivo_urls):
    urls = leer_urls_desde_archivo(archivo_urls)
    if not urls:
        print("No se encontraron URLs para procesar.")
        return

    resultados = []
    SpiderRSS = crear_spider_rss(urls, resultados)

    # Configuración de logging para Scrapy
    configure_logging({'LOG_LEVEL': 'ERROR'})
    process = CrawlerProcess()

    # Iniciar el crawl de Scrapy en asyncio
    process.crawl(SpiderRSS)

    # Ejecutar el proceso Scrapy de manera asíncrona usando asyncio
    await asyncio.to_thread(process.start)

    print(f"\nSe encontraron {len(resultados)} feeds RSS. Validando e insertando...")

    # Guardar los resultados en la base de datos
    async with pool.acquire() as conn:
        for feed_url in resultados:
            try:
                feed = feedparser.parse(feed_url)
                if not feed.entries:
                    print(f"⚠️  No se encontraron entradas en {feed_url}")
                    continue

                title = feed.feed.get("title", "Sin título")
                site_url = feed.feed.get("link", "Sin sitio")

                feed_data = FeedCreateRequest(
                    title=title,
                    feed_url=feed_url,
                    site_url=site_url,
                    owner_uid=1,
                    cat_id=0
                )

                await insert_feed_to_db(conn, feed_data)
                print(f"✅ Feed insertado en DB: {feed_url}")

            except Exception as e:
                print(f"❌ Error procesando {feed_url}: {e}")
