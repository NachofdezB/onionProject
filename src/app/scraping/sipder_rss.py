# src/app/scraping/spider_rss.py
import feedparser
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from app.models.ttrss_postgre_db import insert_feed_to_db, FeedCreateRequest
from multiprocessing import Process, Queue
from scrapy.utils.log import configure_logging

def leer_urls_desde_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, "r") as archivo:
            return [linea.strip() for linea in archivo if linea.strip()]
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

def crear_spider_rss(urls, resultados):
    class SpiderRSS(Spider):
        name = "rss_spider"
        start_urls = urls

        def parse(self, response):
            for link in response.css("link"):
                href = link.attrib.get("href", "")
                tipo = link.attrib.get("type", "")
                if "rss" in tipo or "atom" in tipo or "application/xml" in tipo:
                    full_url = response.urljoin(href)
                    if full_url not in resultados:
                        resultados.append(full_url)
                        print(f"RSS encontrado: {full_url}")
    return SpiderRSS

def correr_spider_rss(urls, queue):
    configure_logging({'LOG_LEVEL': 'ERROR'})
    resultados = []
    spider = crear_spider_rss(urls, resultados)
    process = CrawlerProcess()
    process.crawl(spider)
    process.start()
    queue.put(resultados)

# Función pública que se llama desde FastAPI
async def extraer_rss_y_guardar(pool, archivo_urls):
    urls = leer_urls_desde_archivo(archivo_urls)
    if not urls:
        print("No se encontraron URLs para procesar.")
        return

    queue = Queue()
    p = Process(target=correr_spider_rss, args=(urls, queue))
    p.start()
    p.join()

    resultados = queue.get()

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
                print(f"✅ Feed insertado: {feed_url}")

            except Exception as e:
                print(f"❌ Error procesando {feed_url}: {e}")
