# Proyecto Cebolla — Fase 1: Agregador de Noticias OT/IT

## Introducción

Esta aplicación forma parte de la primera fase del desarrollo del proyecto Cebolla. En esta etapa inicial se plantea la implementación de un sistema automatizado para la agregación de noticias relacionadas con ciberseguridad en los ámbitos de las tecnologías operativas (OT) y las tecnologías de la información (IT). Para llevar a cabo esta tarea se emplea Tiny Tiny RSS (TinyRSS) como motor de agregación de contenidos. TinyRSS permite recolectar, organizar y gestionar artículos provenientes de fuentes RSS especializadas en temas de ciberseguridad.

El sistema se complementa con el uso de Scrapy, un framework de scraping que permite rastrear tanto feeds RSS tradicionales como contenidos obtenidos a través de Google Alerts, ya sea mediante el propio feed RSS o aplicando técnicas de scraping sobre resultados web. TinyRSS actúa como plataforma de almacenamiento inicial, mientras que Scrapy procesa y extrae los datos, almacenándolos finalmente en un archivo JSON. Este archivo servirá como base de datos estructurada para la siguiente fase del proyecto, en la que se aplicarán técnicas de procesamiento de lenguaje natural mediante spaCy con el objetivo de analizar, clasificar y enriquecer el contenido recopilado.

## Propósito del Software

El propósito fundamental de esta aplicación es automatizar la recopilación, validación y almacenamiento de noticias relevantes en el campo de la ciberseguridad OT/IT. Esta automatización tiene como objetivo agilizar el acceso a información crítica y especializada, reduciendo la necesidad de intervención manual en la búsqueda y filtrado de contenidos. A través del uso de Scrapy, el sistema rastrea sitios especializados en ciberseguridad y extrae sus fuentes RSS, obteniendo artículos actualizados y relevantes. Una vez procesados, estos datos se integran en TinyRSS, desde donde pueden ser visualizados y gestionados.

Además de permitir la gestión directa de las noticias desde TinyRSS, el sistema genera un archivo JSON con todos los artículos recopilados. Este archivo actúa como punto de partida para fases posteriores del proyecto, en las que se planea utilizar técnicas avanzadas de análisis de texto mediante la biblioteca spaCy. A través de esta estructura, el proyecto busca establecer una base tecnológica escalable que no solo sea útil en el campo de la ciberseguridad, sino que también pueda adaptarse a nuevas áreas temáticas en futuras iteraciones, ampliando su alcance y funcionalidad más allá del sector OT/IT.

## Características Principales

- Scraping modular con Scrapy (feeds + artículos)
- API REST con FastAPI para exponer funcionalidades
- Uso de base de datos PostgreSQL (la usada por TinyRSS)
- Exportación de artículos a JSON
- Despliegue con Docker Compose
- Preparado para futuras fases con análisis semántico (spaCy)

## Arquitectura de la Aplicación

```
[Fuentes RSS / Google Alerts]
                ↓
         [Tiny Tiny RSS (Docker)]
                ↓
             [Base de datos PostgreSQL]
                ↓
         [Scrapy → export JSON]
                ↓
            [FastAPI (API REST)]
```

- Scrapy accede directamente a la base de datos de TinyRSS, que contiene todos los feeds y artículos recolectados.

## Componentes

- **TinyRSS (Docker)**: recolecta feeds y muestra artículos vía web.
- **PostgreSQL**: base de datos de TinyRSS, usada por toda la aplicación.
- **Scrapy**: realiza scraping de nuevas fuentes y artículos.
- **FastAPI**: expone los datos y permite lanzar scraping vía endpoints.
- **Archivo JSON**: salida estandarizada para análisis de texto posterior.

# Despliegue de Tiny Tiny RSS con Docker

Cómo desplegar **Tiny Tiny RSS** (TTRSS) utilizando **Docker** y **Docker Compose** para crear un entorno eficiente, mantenible y automatizado para la gestión de feeds RSS.

---

## 1. Requisitos (Debian/Ubuntu)

Para comenzar, asegúrate de tener Docker y Docker Compose instalados en tu sistema. Puedes hacerlo ejecutando los siguientes comandos:

```bash
sudo apt update
sudo apt install docker.io docker-compose
```

---

## 2. Variables de entorno

Crea un archivo llamado **stack.env** con las siguientes variables de entorno necesarias para configurar los servicios:

```env
TTRSS_DB_USER=postgres
TTRSS_DB_NAME=postgres
TTRSS_DB_PASS=password123
HTTP_PORT=0.0.0.0:8280
```

> Este archivo ya está incluido en el repositorio. Puedes personalizar las variables según tus necesidades.

---

## 3. Ejecutar TinyRSS

Ubícate en el directorio **docker/** y ejecuta el siguiente comando para levantar todos los servicios:

```bash
docker-compose --env-file stack.env up -d
```

Este comando desplegará los siguientes contenedores:

- **app**: contenedor principal que ejecuta TinyRSS.
- **db**: contenedor con PostgreSQL.
- **updater**: actualiza automáticamente los feeds.

---

## 4. Acceso

Una vez desplegado, puedes acceder a TinyRSS desde:

- Navegador local: `http://localhost:8280`
- Red local: `http://<IP-del-host>:8280`

---

## 5. Almacenamiento de feeds y artículos

Los feeds RSS y sus artículos se almacenan en la base de datos PostgreSQL desplegada en Docker. TinyRSS administra la recopilación y actualización periódica mediante el contenedor **updater**.

### Flujo de almacenamiento

1. TinyRSS agrega los feeds RSS.
2. El servicio updater actualiza periódicamente esos feeds.
3. Los artículos se almacenan en PostgreSQL.
4. Scrapy accede a esta base de datos para transformar y exportar la información.

---

## 6. Conexión de la API a PostgreSQL (TinyRSS)

Para acceder desde una API externa al contenedor de PostgreSQL de TinyRSS, puedes usar asyncpg con una función como esta que esta situada en el main.py:

```python
# Create a connection pool for the PostgreSQL database
async def create_pool() -> None:
    """
    Inicializa un pool de conexiones a PostgreSQL usando asyncpg.
    """
    try:
        logger.info("Database connecting...")
        app.state.pool = await asyncpg.create_pool(
            user='postgres',
            password='password123',
            database='postgres',
            host='127.0.0.1',  # Solo en entorno de desarrollo
            port=5432,
            min_size=5,
            max_size=20
        )
        logger.info("Database connection pool created successfully.")
    except Exception as e:
        logger.error(f"Error creating database connection pool: {str(e)}")
        raise e
```

---

### Cómo encontrar la red Docker para conectar tu API

Para conectar tu API al contenedor de PostgreSQL (TinyRSS) en producción, se recomienda que ambos estén en la misma red de Docker.

1. **Busca el nombre de la red de Docker:**

```bash
docker network ls
```

2. **Inspecciona la red para verificar los contenedores conectados:**

```bash
docker network inspect <nombre-de-la-red>
```

3. **Usa el nombre del servicio PostgreSQL como host en tu conexión si están en la misma red:**
   Por ejemplo: host='db' (si así se llama el servicio en docker-compose.yml)

---

## ¿Cómo se almacenan los feeds y noticias?

TinyRSS gestiona los **feeds RSS** y los **artículos** dentro de su base de datos PostgreSQL que ha sido levantada previamente
en docker con el archivo docker-composble:
tinytinyrss.yml.

### Flujo de Almacenamiento

1. TinyRSS agrega los feeds RSS.
2. El **servicio updater** se encarga de actualizar periódicamente estos feeds.
3. Los artículos se almacenan en la base de datos **postgres**.
4. Scrapy accede directamente a esta base de datos, extrae los artículos, los transforma y los exporta.

# Integración entre Scrapy y la API vía Base de Datos PostgreSQL

Los scripts Scrapy (`spider_rss.py` y `spider_factory.py`) con una API FastAPI, compartiendo una base de datos PostgreSQL como canal de comunicación.

---

## Arquitectura General

```
+-------------+           +------------------+           +-----------------+
| Scrapy RSS  |  --->     |  PostgreSQL DB   |  <---     |     API FastAPI |
|  Spider     |           |    (TinyRSS)     |           |  (lectura y     |
+-------------+           +------------------+           |  transformación)|
                                                         +-----------------+
```

---

## Interacción por Componentes

### 1. Scrapy (spider_rss.py y spider_factory.py)

- **Objetivo:** detectar y extraer feeds RSS/Atom o contenido web estructurado.
- **Ejecución:** cada spider corre como un proceso separado (usando `multiprocessing.Process`).
- **Resultado:** los datos extraídos (feeds, títulos, contenidos) se insertan directamente en la base de datos PostgreSQL mediante una conexión asíncrona (`asyncpg`).

### 2. API FastAPI

- **Objetivo:** exponer endpoints REST para consumir los datos almacenados por Scrapy.
- **Conexión a DB:** utiliza un `pool` de conexiones a PostgreSQL con `asyncpg` para eficiencia.

## Flujo de Trabajo

1. Scrapy detecta feeds desde un archivo de URLs.
2. Extrae y parsea los feeds.
3. Inserta los datos en la base de datos compartida.
4. La API expone endpoints que consultan esta información.
5. Otros servicios pueden acceder a los datos vía HTTP/JSON usando la API.

---

## Ventajas de este enfoque

- Desacopla el scraping de la presentación/API.
- Permite escalar ambos servicios de forma independiente.
- Separa responsabilidades: Scrapy se enfoca en recopilación, la API en consumo.

---

## Conclusión

Esta arquitectura permite una integración flexible y escalable entre Scrapy y FastAPI, usando PostgreSQL como punto de integración. Esto facilita el procesamiento asincrónico y multiproceso sin acoplar lógicamente ambas aplicaciones.

## Preparación del Entorno para FastAPI y Scrapy

### 1. Clonar el repositorio

```bash
git clone https://github.com/empresa/proyecto-cebolla.git
cd proyecto-cebolla
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia y edita:

```bash
cp .env.example .env
nano .env
```

Asegúrate de que las credenciales de PostgreSQL coincidan con las del **stack.env**.

## Arrancar la API FastAPI

```bash
uvicorn app.main:app --reload
```
También se puede correr el archivo main.py

Documentación disponible en para interactuar con suagger de FastApi:
http://localhost:8000/docs

## Manual de Uso — Endpoints

| Método  | Endpoint                              | Descripción                                                                |
|--------|----------------------------------------|----------------------------------------------------------------------------|
| `GET`  | `/postgre-ttrss/feeds`                 | Devuelve todos los feeds registrados en TinyRSS desde la base de datos.    |
| `POST` | `/postgre-ttrss/feeds`                 | Inserta un nuevo feed RSS a partir de una URL proporcionad .               |
| `GET`  | `/postgre-ttrss/search-and-insert-rss` | Extrae y almacena feeds RSS desde un archivo con URLs.                     |
| `POST` | `/scrape/feeds`                        | Ejecuta el spider que rastrea nuevas fuentes RSS desde la web.             |
| `GET`  | `/export/json`                         | Exporta todos los artículos en formato result.json.                      |

> El endpoint **/export/json** se utiliza para generar el archivo que se utilizará en la siguiente fase del proyecto, donde un módulo en Python procesará los textos con **spaCy** para análisis semántico.

## ¿Por qué usar FastAPI?

- **Rendimiento asíncrono**
- **Documentación automática usable**
- **Validación de datos con Pydantic**
- **Escalable y ligero**
- **Ideal para microservicios**

## Fases Futuras del Proyecto

Este sistema servirá como base para:

- Clasificación de noticias con NLP (spaCy)

## Archivos Importantes del Repositorio

```
proyecto-cebolla/
├── Doxyfile                    # Configuración para generar documentación con Doxygen
├── README.md                   # Documentación principal del proyecto
├── requirements.txt            # Dependencias del entorno Python
├── src/                        # Código fuente del proyecto
│   ├── app/                    # Aplicación principal basada en FastAPI
│   │   ├── controllers/        # Controladores con la lógica de negocio
│   │   │   ├── __init__.py
│   │   │   ├── scrapy_news_controller.py
│   │   │   └── tiny_postgres_controller.py
│   │   ├── models/             # Definición de modelos (Consultas para postgres de ttrss)
│   │   │   ├── __init__.py
│   │   │   └── ttrss_postgre_db.py
│   │   ├── scraping/           # Spiders y lógica de scraping (Scrapy)
│   │   │   ├── sipder_rss.py
│   │   │   └── spider_factory.py
│   │   ├── static/             # Archivos estáticos
│   │   │   └── docs/           # Documentos de apoyo al scraping
│   │   │       ├── urls_ciberseguridad_ot_it.txt
│   │   │       └── use_logs.txt
│   ├── data/                   # Archivos de entrada/salida u otros recursos
│   │   └── urls_ciberseguridad_ot_it.txt
│   ├── outputs/                # Resultados generados (JSON, CSV, etc.)
│   │   └── result.json
│   ├── main.py                 # Punto de entrada de la aplicación
├── test/                       # Pruebas unitarias y de integración
│   ├── routes/                 # Pruebas de las rutas de la API
│   │   └── test_main.py
│   └── services/               # Pruebas para lógica de servicios (OCR, PDF, etc.)
│       ├── test_ocr.py
│       └── test_pdf.py

```
