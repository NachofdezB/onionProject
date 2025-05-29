import spacy
import json
from langdetect import detect


models = {
    'es': spacy.load("es_core_news_sm"),
    'en': spacy.load("en_core_web_sm"),
    'fr': spacy.load("fr_core_news_sm"),
}

## \brief Detects the language of a given text.
#  \param text String text to analyze.
#  \return ISO 639-1 language code of the detected language (e.g., 'es', 'en', 'fr').
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'es'  # Default fallback

## \brief Tags named entities in a text by automatically detecting the language.
#  \param text Text to process.
#  \return A tuple with the list of found entities [(text, type)] and the detected language.
def tag_text(text):
    language = detect_language(text)
    model = models.get(language, models['es'])  # use Spanish if language not supported
    doc = model(text)
    return [(ent.text, ent.label_) for ent in doc.ents], language

## \brief Processes an input JSON file, tagging texts by language, and saves the results to another JSON.
#  \param input_path Path to the input JSON file. Must contain a list of objects with the key "text".
#  \param output_path Path where the result JSON file will be saved.
#  \return List of results with text, language, tags, and relevance (number of tags).
def process_json(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for entry in data:
        text = entry.get("texto", "")
        tags, detected_language = tag_text(text)
        results.append({
            "text": text,
            "language": detected_language,
            "tags": tags,
            "relevance": len(tags)
        })

    # Sorts texts by number of entities (relevance) from most to least
    results.sort(key=lambda x: x["relevance"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results
