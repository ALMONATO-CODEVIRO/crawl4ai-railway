import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import os, json

app = FastAPI()

# ---------- HEALTHCHECK ----------
@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI en Railway está vivo 🚀"}

# ======================
# MODELO REQUEST/RESPONSE
# ======================

class ExtractRequest(BaseModel):
    url: str
    query: str = """
    Extrae SOLO esta información del producto y respóndela en JSON:
    {
        "nombre": "",
        "precio": "",
        "precio_anterior": "",
        "sku": "",
        "marca": "",
        "descripcion": "",
        "imagen": "",
        "disponibilidad": ""
    }
    """

class ExtractResponse(BaseModel):
    success: bool
    data: dict
    raw_text: str


# ======================
# ROUTE /extract
# ======================

@app.post("/extract", response_model=ExtractResponse)
async def extract(request: ExtractRequest):
    # Comprobamos que la API key existe
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ExtractResponse(
            success=False,
            data={"error": "OPENAI_API_KEY no está configurada dentro del contenedor"},
            raw_text=""
        )

    # Estrategia LLM de crawl4ai
    llm_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4.1-mini",   # si falla, luego probamos con otro nombre
        api_token=api_key,
        instruction=request.query,
        extraction_type="json",
        apply_chunking=False,
    )

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=request.url,
                extraction_strategy=llm_strategy,
                screenshot=False,
            )
    except Exception as e:
        # para evitar que el servidor se caiga y Railway devuelva 502
        return ExtractResponse(
            success=False,
            data={"error": str(e)},
            raw_text=""
        )

    data = {}
    if result.extracted_content:
        try:
            data = json.loads(result.extracted_content)
        except Exception:
            data = {"raw": result.extracted_content}

    raw_text = ""
    if hasattr(result, "markdown_v2") and result.markdown_v2:
        raw_text = result.markdown_v2.raw_markdown or ""
    elif hasattr(result, "markdown") and result.markdown:
        raw_text = result.markdown

    return ExtractResponse(
        success=result.success,
        data=data,
        raw_text=raw_text,
    )


