# Documentación del Proyecto Ignacio y Antonio

## Introducción

Este proyecto es una aplicación de **búsqueda e indexación de documentos PDF**, diseñada para facilitar el acceso, análisis y recuperación de información contenida en archivos PDF. La solución tiene como objetivo **automatizar el procesamiento, almacenamiento y búsqueda inteligente de PDFs** mediante tecnologías modernas como **Python (Flask)** y **OpenSearch**.

Está desarrollada principalmente en **Python 3.12** utilizando el framework **Flask**, con integración en un entorno **WSL Debian** donde se ejecuta el servicio de **OpenSearch** para el manejo de índices y consultas.

## Propósito del Software

El propósito principal de esta aplicación es ofrecer una **plataforma ligera y funcional para almacenar, procesar y buscar información contenida en documentos PDF**. Se busca resolver el problema de **búsqueda manual y no estructurada dentro de archivos PDF dispersos**, permitiendo a los usuarios encontrar fácilmente contenido específico mediante una búsqueda optimizada.

### Características principales:
- Subida de archivos PDF a través de una interfaz web.
- Procesamiento automático del contenido de los PDFs (extracción de texto).
- Indexación de contenido en **OpenSearch** para búsqueda eficiente.
- Interfaz de búsqueda donde los usuarios pueden realizar consultas textuales.
- Almacenamiento de los archivos en una estructura de carpetas (`uploads/pdfs`).
- Arquitectura modular dividida en rutas, servicios, modelos y utilidades.
- Conjunto de pruebas unitarias organizadas por componente.
- Sistema ejecutado en entorno Linux (WSL) para mejor integración con servicios como OpenSearch.

## Estructura del Proyecto
{
  "formacion-nivel-medio": {
    "src": {
      "run.py": "Script principal para ejecutar la app Flask",
      "app": {
        "__init__.py": "Archivo de inicialización del paquete de la aplicación",
        "routes": "Rutas de la app (vistas principales)",
        "services": "Lógica de negocio y procesamiento de PDFs",
        "models": "Modelos de datos (si se usan más adelante)",
        "utils": "Funciones auxiliares",
        "static": "CSS y archivos estáticos",
        "templates": "HTML con Jinja2"
      }
    },
    "test": "Pruebas unitarias",
    "uploads": {
      "pdfs": "Carpeta donde se almacenan los PDFs subidos"
    },
    "requirements.txt": "Dependencias del proyecto",
    "README.md": "Documentación principal del proyecto",
    "wiki.md": "Documentación adicional"
  }
}

## Tecnologías Utilizadas

- **Python 3.12**
- **Flask** (Framework web ligero)
- **OpenSearch** (Motor de búsqueda y análisis basado en Elasticsearch)
- **HTML/CSS** con **Jinja2** para plantillas
- **WSL Debian** como entorno de ejecución

## Próximos Pasos / Ideas de Mejora

- Añadir autenticación de usuarios.
- Mejorar la interfaz de búsqueda con filtros avanzados (por fecha, relevancia, etc.).
- Subida múltiple de PDFs.
- Integración con OpenSearch Dashboards para visualización gráfica.
- Panel de administración para gestión de archivos e índices.
- Exportación o descarga de resultados de búsqueda.

## Manual de Uso

A continuación se detalla cómo utilizar la aplicación:

### 1. Instalación

    Para instalar la aplicación, sigue los siguientes pasos:
    1. Clona el repositorio:
    ```bash
    git clone https://gitlab.com/usuario/proyecto.git
