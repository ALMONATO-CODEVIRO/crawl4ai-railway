from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from playwright.async_api import async_playwright
import asyncio
import io
import base64

# Carga variables desde .env
load_dotenv()

# Inicia la app FastAPI
app = FastAPI()

# Modelos de entrada y salida
class CrawlInput(BaseModel):
    url: str

class CrawlOutput(BaseModel):
    markdown: str
    metadata: dict

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI + Crawl4AI activo"}

@app.post("/crawl", response_model=CrawlOutput)
def crawl_endpoint(data: CrawlInput):
    try:
        result = asyncio.run(crawl_url(data.url))
        return {
            "markdown": result.markdown,
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función principal que llama a Crawl4AI
async def crawl_url(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    return result

# Endpoint para screenshot y devolver base64
@app.post("/screenshot")
async def take_screenshot(request: Request):
    body = await request.json()
    url = body.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        buffer = await page.screenshot(full_page=True)
        await browser.close()

        # Convertimos a base64
        base64_str = base64.b64encode(buffer).decode("utf-8")

        return {
            "status": "ok",
            "image_base64": base64_str,
            "content_type": "image/png"
        }





