# Documentación del Proyecto

## Introducción

Esta aplicación corresponde a la primera fase del desarrollo del proyecto **Cebolla**. En esta fase se plantea el uso de **Tiny Tiny RSS (TinyRSS)** como motor de agregación de contenidos que permite recolectar y gestionar noticias de actualidad sobre un tema determinado. En este caso, el enfoque está en noticias relacionadas con ciberseguridad OT (tecnologías operativas) e IT (tecnologías de la información). A medida que se agregan fuentes RSS a TinyRSS, la aplicación analiza estas fuentes, filtra las noticias relevantes y las almacena en una base de datos para su posterior procesamiento y visualización.

## Propósito del Software

El propósito principal de esta aplicación es automatizar la recolección, validación y almacenamiento de noticias relevantes sobre ciberseguridad en los ámbitos OT (tecnología operativa) e IT (tecnología de la información), utilizando técnicas de web scraping. Para ello, la aplicación se apoya en **Scrapy** para rastrear y extraer feeds RSS desde sitios web especializados, los cuales son luego procesados mediante **Tiny Tiny RSS**, permitiendo filtrar y consumir artículos de interés.

El objetivo final es compartir las noticias recolectadas en formato **JSON** con Scrapy, facilitando su integración con otras herramientas o plataformas de análisis. Además, este sistema está diseñado para ser escalable, de modo que en futuras fases también pueda incorporar la recolección de información sobre otras temáticas o sectores más allá de la ciberseguridad.

## Características principales

### Funcionamiento Técnico General

- **Scraping modular con Scrapy**
  - Separación clara entre spiders para obtener feeds RSS y para extraer noticias.
  - Capacidad para ejecutar scraping de forma independiente o desde endpoints API mediante FastAPI.
  - Manejo de errores y reintentos ante fallos de conexión.

- **API REST con FastAPI**
  - Endpoints para lanzar scraping, consultar feeds, obtener noticias en formato JSON, etc.
  - Documentación interactiva disponible en `/docs` gracias a Swagger UI.

- **Base de datos PostgreSQL**
  - Persistencia de feeds y artículos mediante un pool de conexiones asíncrono (por ejemplo, con `asyncpg`).
  - Validación y deduplicación de entradas antes de insertar.

- **Tiny Tiny RSS en Docker**
  - Tiny se despliega en un contenedor Docker para la gestión y lectura de los feeds.
  - Accesible desde navegador para visualizar los artículos de forma cómoda.

- **Formato de salida unificado (JSON)**
  - Las noticias validadas y extraídas se transforman a JSON.
  - Este JSON puede ser reutilizado en otras fases del proyecto, como análisis de datos o visualización.

- **Preparado para ampliaciones futuras**
  - Arquitectura pensada para incluir nuevos temas además de ciberseguridad OT/IT.
  - Posibilidad de integrar machine learning o análisis semántico en fases posteriores.

## Arquitectura de la Aplicación

La arquitectura de esta aplicación está diseñada bajo principios de **modularidad**, **asincronía** y **escalabilidad**, permitiendo combinar la potencia del scraping con una interfaz web moderna y ligera. La solución está compuesta por varios bloques fundamentales:

### Componentes principales

- **Scrapy (Scrapers modulares)**
  - Scrapy es el núcleo de recolección de datos, dividiendo el scraping en dos fases: una para obtener feeds RSS y otra para extraer artículos concretos desde esos feeds.
  - Se ejecuta de forma autónoma o bien como tarea desde la API.

- **FastAPI (Back-end web / API REST)**
  - FastAPI actúa como puerta de entrada para los usuarios o servicios externos que interactúan con la aplicación.
  - Permite lanzar procesos de scraping, consultar noticias almacenadas y acceder al contenido en JSON de forma sencilla y rápida.

- **PostgreSQL (Persistencia de datos)**
  - Los feeds y artículos se almacenan en una base de datos relacional optimizada para consultas eficientes y estructuradas.
  - Se emplea acceso asíncrono para mejorar el rendimiento.

- **Tiny Tiny RSS (Visualización en navegador)**
  - Usado como lector web de los feeds agregados. Se ejecuta en un contenedor Docker aislado y configurable.

## ¿Por qué se ha elegido FastAPI?

FastAPI ha sido seleccionado para este proyecto por varias razones que se alinean con los objetivos técnicos y prácticos de la aplicación:

- **Rendimiento asíncrono y eficiente**
  FastAPI está construido sobre Starlette y permite operaciones asíncronas con `async/await`, lo que es ideal para integrarse con Scrapy y bases de datos asíncronas como `asyncpg`.

- **Documentación automática**
  Genera una documentación interactiva en Swagger UI de forma automática. Esto acelera el desarrollo, la validación y el consumo de la API por terceros.

- **Tipado fuerte con Pydantic**
  Facilita la validación de datos mediante modelos, mejorando la robustez del código y la calidad del desarrollo.

- **Facilidad de uso sin sacrificar potencia**
  Comparado con Flask (más simple pero menos potente para proyectos grandes) o Django (más pesado y orientado a aplicaciones completas con interfaz gráfica), FastAPI ofrece un equilibrio ideal para microservicios rápidos y APIs especializadas.

- **Escalabilidad futura**
  Su diseño modular y enfoque asincrónico lo hacen apto para escalar tanto vertical como horizontalmente en proyectos que crecen.


## Despliegue de Tiny Tiny RSS con Docker y Nginx

El despliegue de TinyRSS se realiza mediante archivos `docker-compose` que permiten orquestar múltiples servicios: la base de datos, la aplicación TinyRSS, y un proxy inverso con Nginx para servirlo bajo un subdominio personalizado utilizando DuckDNS.

### 1. Estructura General del Despliegue

El entorno de despliegue se compone de varios contenedores Docker que trabajan juntos para proporcionar una solución escalable y segura. Los componentes principales son los siguientes:

- **Tiny Tiny RSS (app)**: El contenedor principal que ejecuta TinyRSS. Este servicio maneja la recolección de feeds RSS y la gestión de artículos.

- **Base de datos PostgreSQL (db)**: Contenedor que aloja la base de datos donde se almacenan los feeds RSS y artículos. Se asegura de que la información esté disponible de manera eficiente y persistente.

- **Nginx Proxy (web-nginx)**: Un contenedor con Nginx configurado como proxy inverso. Nginx se encarga de enrutar el tráfico HTTPS al contenedor `app` de TinyRSS, ofreciendo seguridad y mejor rendimiento.

- **Updater**: Este contenedor es responsable de actualizar los feeds y sincronizar la información de TinyRSS de manera periódica.

- **Nginx Proxy Manager**: Utilizado para facilitar la configuración y gestión de los proxies. Este servicio se conecta directamente a la dirección por defecto de TinyRSS, permitiendo la gestión de certificados SSL y la configuración de proxy inverso sin necesidad de editar manualmente los archivos de configuración.

  - **Certificados SSL**: El proxy inverso Nginx gestiona la encriptación SSL, asegurando que el tráfico entre el cliente y el servidor esté protegido. Nginx Proxy Manager puede encargarse de la renovación automática de los certificados SSL utilizando Let's Encrypt.

- **Subdominio proporcionado por DuckDNS**: El acceso a la aplicación se realiza mediante un subdominio configurado en DuckDNS, lo que permite gestionar la IP dinámica de una manera sencilla.

### Flujo de Trabajo del Despliegue:

1. **TinyRSS** se ejecuta en un contenedor que maneja todos los aspectos relacionados con la recolección y visualización de artículos de noticias.

2. **Nginx Proxy** enruta las solicitudes HTTPS de los usuarios hacia el contenedor de **TinyRSS**, permitiendo que el acceso sea seguro y cifrado.

3. **Updater** actualiza los feeds de manera periódica, asegurando que los artículos más recientes sean procesados y almacenados en la base de datos PostgreSQL.

4. **Nginx Proxy Manager** facilita la configuración y administración del proxy inverso, incluyendo la obtención y renovación de certificados SSL de manera automática.

5. Finalmente, el **subdominio de DuckDNS** permite un acceso sencillo y dinámico a la aplicación, sin necesidad de preocuparse por la dirección IP del servidor, que puede cambiar con el tiempo.

Este enfoque modular y basado en Docker asegura que cada componente pueda ser gestionado de manera independiente y escalable, permitiendo una mayor flexibilidad y seguridad en la implementación.


### 2. Requisitos previos

- Tener Docker y Docker Compose instalados.
- Registrar un subdominio gratuito en [https://www.duckdns.org](https://www.duckdns.org).
- Abrir los puertos 80 y 443 en el router si estás en red doméstica.
- Disponer de un token de DuckDNS para actualizar la IP dinámica.

### 3. Variables de entorno

Crea un archivo `stack.env` con valores como:

```stack.env
TTRSS_DB_USER=postgres
TTRSS_DB_NAME=postgres
TTRSS_DB_PASS=password123
HTTP_PORT=127.0.0.1:8280
```

## Manual de Uso

A continuación se detalla cómo utilizar la aplicación:

### 1. Instalación

    Para instalar la aplicación, sigue los siguientes pasos:
    1. Clona el repositorio:
    ```bash
    git clone https://gitlab.com/usuario/proyecto.git
