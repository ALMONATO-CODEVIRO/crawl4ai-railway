from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import base64
import asyncio

# Cargar variables desde .env
load_dotenv()

# Iniciar la aplicación FastAPI
app = FastAPI()

# Modelos
class CrawlInput(BaseModel):
    url: str

class ScreenshotRequest(BaseModel):
    url: str

class CrawlOutput(BaseModel):
    markdown: str
    html: str
    metadata: dict

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI activo"}

# 📸 Screenshot en base64 PNG
@app.post("/screenshot")
async def screenshot(request: ScreenshotRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(request.url, wait_until="networkidle")
            screenshot_bytes = await page.screenshot(full_page=True, type="png")
            await browser.close()

        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        return {
            "image_base64": screenshot_base64,
            "content_type": "image/png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🌐 Crawl con Crawl4AI
@app.post("/crawl", response_model=CrawlOutput)
def crawl_endpoint(data: CrawlInput):
    try:
        result = asyncio.run(crawl_url(data.url))
        return {
            "markdown": result.markdown,
            "html": result.html,
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función auxiliar para Crawl4AI
async def crawl_url(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    return result







