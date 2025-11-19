from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
from typing import Optional, Dict
import asyncio

load_dotenv()
app = FastAPI()

# Modelo de entrada
class CrawlInput(BaseModel):
    url: str
    selectors: Optional[Dict[str, str]] = None  # Selectores opcionales

# Modelo de salida
class CrawlOutput(BaseModel):
    markdown: str
    html: str
    metadata: dict
    screenshot_base64: str
    extracted: Optional[dict] = None

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI + Crawl4AI activo"}

@app.post("/crawl", response_model=CrawlOutput)
def crawl_endpoint(data: CrawlInput):
    try:
        result = asyncio.run(crawl_url(data.url, data.selectors))
        response = {
            "markdown": result.markdown,
            "html": result.html,
            "metadata": result.metadata,
            "screenshot_base64": result.screenshot_base64,
        }
        if hasattr(result, "extracted") and result.extracted:
            response["extracted"] = result.extracted
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función asíncrona que llama a Crawl4AI
async def crawl_url(url: str, selectors: Optional[dict] = None):
    async with AsyncWebCrawler() as crawler:
        if selectors:
            result = await crawler.arun(url=url, selectors=selectors)
        else:
            result = await crawler.arun(url=url)
    return result






