"""labels_api.py

REST API to process a JSON text file using named entity recognition with spaCy.

This endpoint reads a `result.json` file, processes it to extract named
entities, and returns a generated `etiquetas_resultado.json` file.

Author: Stefan Stan
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.spacy.text_processor import process_json

router = APIRouter(

    tags=["spacy"],
    responses={
        200: {"description": "Processed file returned successfully"},
        404: {"description": "Input file result.json not found"},
        500: {"description": "Failed to generate output file "
                "etiquetas_resultado.json"
            }
    }
)

@router.get("/process-spacy")
async def process_result_json():
    '''
    Process the result.json file and return the processed output.

    This endpoint checks for the presence of `result.json`, processes it
    using spaCy to extract named entities, and writes the output to
    `etiquetas_resultado.json`. The resulting file is returned as a JSON
    response.

    Returns:
        FileResponse: The generated etiquetas_resultado.json file.

    Raises:
        HTTPException: 404 if result.json is not found.
        HTTPException: 500 if etiquetas_resultado.json could not be created.
    '''
    input_path = "src/outputs/result.json"
    output_path = "src/outputs/labels_result.json"

    if not os.path.exists(input_path):
        raise HTTPException(
            status_code=404,
              detail="File result.json not found"
            )

    # Process and tag the file
    process_json(input_path, output_path)

    if not os.path.exists(output_path):
        raise HTTPException(
            status_code=500,
            detail="Could not generate etiquetas_resultado.json"
        )

    return FileResponse(output_path, media_type='application/json')
