## \file etiquetas_api.py
## \brief API REST para procesar un archivo JSON de texto usando análisis de entidades con spaCy.
## \details Este endpoint permite leer un archivo `result.json`, procesarlo para extraer entidades nombradas
## y devolver un archivo `etiquetas_resultado.json` generado automáticamente.
## \author Stefan Stan

import os
import threading
from fastapi import APIRouter, HTTPException
from loguru import logger
from app.spacy.text_processor import process_json

router = APIRouter(
    tags=["spacy"],
    responses={
        200: {"description": "Processed file returned successfully"},
        404: {"description": "Input file result.json not found"},
        500: {"description": "Failed to generate output file etiquetas_resultado.json"}
    }
)


def background_process_every_24h(input_path: str, output_path: str):
    """
    Executes the JSON NLP processing task and schedules the next execution after 24 hours.

    Args:
        input_path (str): Path to the input JSON file with raw news/texts.
        output_path (str): Path to save the output file with extracted SpaCy labels.
    """
    try:
        logger.info("🔍 [SpaCy] Starting entity labeling on result.json...")
        process_json(input_path, output_path)
        logger.success("[SpaCy] Entity labeling completed. Output saved to labels_result.json")
    except Exception as e:
        logger.error(f"[SpaCy] Error while labeling entities: {e}")

    # Schedule next execution in 24 hours
    timer = threading.Timer(86400, background_process_every_24h, args=(input_path, output_path))
    timer.daemon = True
    timer.start()
    logger.info("[Scheduler] Next SpaCy entity labeling scheduled in 24 hours.")


@router.get("/start-spacy-scheduler")
async def start_background_loop():
    """
    Manually starts the recurring SpaCy processing job every 24 hours in the background.

    Returns:
        dict: Status message confirming that the recurring task has been initiated.

    Raises:
        HTTPException: If the input file `result.json` is not found.
    """
    input_path = "src/outputs/result.json"
    output_path = "src/outputs/labels_result.json"

    if not os.path.exists(input_path):
        logger.warning("[Startup] Input file result.json not found. Aborting scheduler.")
        raise HTTPException(
            status_code=404,
            detail="File result.json not found"
        )

    threading.Thread(
        target=background_process_every_24h,
        args=(input_path, output_path),
        daemon=True
    ).start()

    logger.info("🚀 [Scheduler] SpaCy recurring labeling task initialized.")
    return {"message": "Background process started. Will re-run every 24 hours."}
