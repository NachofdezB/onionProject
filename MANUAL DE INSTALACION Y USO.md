# Manual de instalacion 

## Instalación de la app
Para realizar la instalacion de la app en debian primeramente nos deberemos situar en la carpeta donde se encuentre el archivo .deb de la app.
- cd /ruta/del/archivo

A continuacion debemos instalarlo mediante el siguiente comando:
- sudo apt install ./nombre_del_archivo.deb

Tras esto el programa instalara todas las dependencias necesarias para el correcto funcionamiento de la app.

### Configuración Inicial

1. Primeramente debemos realizar pequeñas modificaciones en la configuración del servicio de opensearch:
    - Primero accedemos a la carpeta donde se aloje el fichero de configuración del servicio:
        cd opensearch-*/
    - En segundo lugar abriremos el archivo .yml haciendo uso de la herramienta nano 
        nano config/opensearch.yml
    - En tercer lugar sustituimos el contenido del fichero por el siguiente (cabe recalcar que esta configuración es para un uso local de la app
    para uso remoto habría que modificar parte de esta configuración):

    ```yaml 
    # ======================== OpenSearch Configuration =========================
    #
    # NOTE: OpenSearch comes with reasonable defaults for most settings.
    #       Before you set out to tweak and tune the configuration, make sure you
    #       understand what are you trying to accomplish and the consequences.
    #
    # The primary way of configuring a node is via this file. This template lists
    # the most important settings you may want to configure for a production cluster.
    #
    # Please consult the documentation for further information on configuration options:
    # https://www.opensearch.org
    #
    # ---------------------------------- Cluster -----------------------------------
    #
    cluster.name: opensearch-cluster
    #
    # ------------------------------------ Node ------------------------------------
    #
    node.name: node-1
    #
    # Add custom attributes to the node:
    #
    #node.attr.rack: r1
    #
    # ----------------------------------- Paths ------------------------------------
    #
    #path.data: /path/to/data
    #path.logs: /path/to/logs
    #
    # ----------------------------------- Memory -----------------------------------
    #
    bootstrap.memory_lock: true
    #
    # ---------------------------------- Network -----------------------------------
    #
    network.host: 0.0.0.0
    http.port: 9200
    #
    # --------------------------------- Discovery ----------------------------------
    #
    discovery.type: single-node
    #
    # ---------------------------------- Gateway -----------------------------------
    #
    #gateway.recover_after_nodes: 3
    #
    # ---------------------------------- Various -----------------------------------
    #
    action.destructive_requires_name: true
    #
    # ---------------------------------- Security -----------------------------------
    #
    plugins.security.disabled: true
    ```

    - En cuarto lugar solo quedaría arrancar el servicio de opensearch.
        ./opensearch-tar-install.sh

2. Asegúrese de tener un servidor OpenSearch en funcionamiento y accesible desde el script.
3. Prepare un archivo de configuración `cfg.ini` con los parámetros de conexión al servidor OpenSearch y la clave de API para SerpAPI.


# Manual de Uso 

## Flujo de Trabajo

### Búsqueda de PDFs

Utiliza distintos motores de búsqueda (Google Scholar, ArXiv, Sci-Hub) para encontrar archivos PDF relevantes basados en palabras clave proporcionadas por el usuario.

- La función `search_pdfs` envía una consulta a los motores seleccionados y filtra los resultados para obtener solo los enlaces a archivos PDF.

### Descarga de PDFs

La función `download_pdf` descarga un archivo PDF desde un enlace proporcionado y lo guarda en una carpeta local.

### Extracción de Texto con OCR

La función `extract_text_from_pdf` abre cada página del PDF, la convierte en una imagen y luego usa `pytesseract` para extraer el texto.

### Filtrado de Texto

Una vez extraído el texto, se filtra según las palabras clave proporcionadas por el usuario mediante la función `filter_text`. Esto permite extraer solo las secciones del texto que contienen información relevante.

### Análisis de Sentimiento

El texto extraído se procesa para determinar su sentimiento (positivo, negativo o neutral) mediante el uso de un modelo preentrenado basado en `distilbert-base-uncased-finetuned-sst-2-english`.

### Almacenamiento en OpenSearch

Finalmente, la información procesada se almacena en un servidor OpenSearch utilizando la función `store_in_opensearch`, permitiendo consultas rápidas sobre los datos procesados.

### Ejecución del Pipeline de Búsqueda

Para ejecutar el pipeline de búsqueda, se realizara mediante el uso del servicio web que nos proporciona flask , donde debemos indicar la keyword, seleccionar el motor de busqueda
y seleccionar las etiquetas con las cuales se va a almacenar la información en opensearch.