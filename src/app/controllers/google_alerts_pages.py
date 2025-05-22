import feedparser
import urllib.parse
from loguru import logger
import os

# Ruta del archivo con las URLs de feeds de Google Alerts
FEEDS_FILE_PATH = "src/data/google_alert_rss.txt"

# Ruta del archivo donde se guardarán las URLs reales extraídas
URLS_FILE_PATH = "src/data/urls_ciberseguridad_ot_it.txt"


def clean_google_redirect_url(url: str) -> str:
    """
    Extrae la URL real de los enlaces con redirección de Google Alerts.
    """
    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)
    real_url = query_params.get("url", [url])[0]
    return real_url


def fetch_and_save_alert_urls():
    if not os.path.exists(FEEDS_FILE_PATH):
        logger.error(f"No se encontró el archivo de feeds: {FEEDS_FILE_PATH}")
        return

    os.makedirs(os.path.dirname(URLS_FILE_PATH), exist_ok=True)

    total_urls = []

    # Leer solo la URL limpia antes del posible separador '|'
    with open(FEEDS_FILE_PATH, "r", encoding="utf-8") as feeds_file:
        feed_urls = []
        for line in feeds_file:
            line = line.strip()
            if not line:
                continue
            url_only = line.split('|')[0].strip()  # Solo la URL, sin el título
            feed_urls.append(url_only)

    for feed_url in feed_urls:
        logger.info(f"Leyendo feed: {feed_url}")
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            logger.warning(f"No se encontraron entradas en: {feed_url}")
            continue

        for entry in feed.entries:
            link = entry.get("link")
            if link:
                clean_url = clean_google_redirect_url(link)
                total_urls.append(clean_url)

    if not total_urls:
        logger.warning("No se extrajeron URLs válidas de ningún feed.")
        return

    with open(URLS_FILE_PATH, "w", encoding="utf-8") as f:
        for url in total_urls:
            f.write(url + "\n")

    logger.info(f"Se guardaron {len(total_urls)} URLs en {URLS_FILE_PATH}")
