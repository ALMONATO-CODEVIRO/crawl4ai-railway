from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
import asyncio
from typing import Optional, Dict
import base64

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Modelo de entrada
class CrawlInput(BaseModel):
    url: str
    selectors: Optional[Dict[str, str]] = None   # { "precio": ".box__price--current" }


# Modelo de salida
class CrawlOutput(BaseModel):
    markdown: str
    html: str
    metadata: dict
    extracted: Optional[Dict[str, str]] = None
    screenshot_base64: Optional[str] = None


@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI + Crawl4AI activo"}


# -----------------------------
#  ENDPOINT PRINCIPAL /crawl
# -----------------------------
@app.post("/crawl", response_model=CrawlOutput)
def crawl_endpoint(data: CrawlInput):
    try:
        result = asyncio.run(
            crawl_url(
                url=data.url,
                selectors=data.selectors
            )
        )

        return {
            "markdown": result["markdown"],
            "html": result["html"],
            "metadata": result["metadata"],
            "extracted": result["extracted"],
            "screenshot_base64": result["screenshot"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# -----------------------------
#   FUNCIÓN CENTRAL
# -----------------------------
async def crawl_url(url: str, selectors: Optional[Dict[str, str]] = None):

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            selectors=selectors,     # Extrae texto por CSS
            screenshot=True,         # Habilita captura
            return_html=True,        # Devuelve HTML completo
            return_markdown=True     # Devuelve Markdown limpio
        )

    # Convertir screenshot a base64 si existe
    screenshot_b64 = None
    if result.screenshot is not None:
        screenshot_b64 = base64.b64encode(result.screenshot).decode("utf-8")

    return {
        "markdown": result.markdown,
        "html": result.html,
        "metadata": result.metadata,
        "extracted": result.extracted,
        "screenshot": screenshot_b64,
    }


# -----------------------------
#   ENDPOINT PARA SOLO CAPTURA
# -----------------------------
@app.get("/screenshot")
def get_screenshot(url: str):
    try:
        result = asyncio.run(capture_screenshot(url))
        return {"url": url, "screenshot_base64": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def capture_screenshot(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            screenshot=True
        )

    if result.screenshot is None:
        raise Exception("No fue posible generar el screenshot")

    return base64.b64encode(result.screenshot).decode("utf-8")






