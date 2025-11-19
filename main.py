from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
import asyncio

# Carga variables desde .env (si lo necesitas)
load_dotenv()

# Inicia la app FastAPI
app = FastAPI()

# Modelo de entrada (una URL)
class CrawlInput(BaseModel):
    url: str

# Modelo de salida (lo que devolveremos al cliente)
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

# Función principal que llama a Crawl4AI de forma asíncrona
async def crawl_url(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    return result




