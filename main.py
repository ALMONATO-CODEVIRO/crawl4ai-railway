from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
import asyncio

# Cargar variables de entorno si se usan
load_dotenv()

app = FastAPI()

# 📦 MODELOS
class CrawlInput(BaseModel):
    url: str

class SelectorsInput(BaseModel):
    url: str
    selectors: list[str]  # Lista de selectores CSS

class CrawlOutput(BaseModel):
    html: str
    markdown: str
    metadata: dict

class ScreenshotOutput(BaseModel):
    screenshot_base64: str

class SelectorsOutput(BaseModel):
    extracted: dict  # selector → contenido extraído

# ✅ Ruta raíz
@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI + Crawl4AI activo"}

# 🚀 /crawl: markdown + html + metadata
@app.post("/crawl", response_model=CrawlOutput)
def crawl_endpoint(data: CrawlInput):
    try:
        result = asyncio.run(crawl_url(data.url))
        return {
            "html": result.html,
            "markdown": result.markdown,
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔎 /selectors: extraer texto de selectores CSS
@app.post("/selectors", response_model=SelectorsOutput)
def selectors_endpoint(data: SelectorsInput):
    try:
        result = asyncio.run(extract_selectors(data.url, data.selectors))
        return {"extracted": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🖼 /screenshot: imagen base64
@app.post("/screenshot", response_model=ScreenshotOutput)
def screenshot_endpoint(data: CrawlInput):
    try:
        screenshot_data = asyncio.run(capture_screenshot(data.url))
        return {"screenshot_base64": screenshot_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ⚙️ FUNCIONES ASYNC
async def crawl_url(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    return result

async def capture_screenshot(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, screenshot=True)
        return result.screenshot_base64

async def extract_selectors(url: str, selectors: list[str]) -> dict:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        extracted = {}
        for selector in selectors:
            try:
                extracted[selector] = result.select_text(selector)
            except Exception as e:
                extracted[selector] = f"Error: {str(e)}"
        return extracted






