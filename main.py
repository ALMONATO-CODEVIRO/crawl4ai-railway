import os
from fastapi import FastAPI
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from crawl4ai.extractors.llm_extractor import LLMExtractor

app = FastAPI()

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
    crawler = AsyncWebCrawler()

    # Iniciar navegador (headless Chromium)
    await crawler.start()

    # LLMExtractor
    extractor = LLMExtractor(
        llm_provider="openai/gpt-4.1-mini",  # Puedes cambiar el modelo
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        extraction_prompt=request.query
    )

    # Ejecutar extracción
    result = await crawler.extract(
        url=request.url,
        extractor=extractor,
        wait_for=2000,            # espera para cargar la página
        screenshot=True,          # útil para debugging
        js=False                  # No forzar JS a menos que sea necesario
    )

    await crawler.close()

    return ExtractResponse(
        success=True,
        data=result.extracted_content,
        raw_text=result.markdown
    )

