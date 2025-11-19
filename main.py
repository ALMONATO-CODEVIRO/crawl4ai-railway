from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"status": "ok", "message": "Crawl4AI service running"}

@app.post("/crawl")
async def crawl_url(req: CrawlRequest):
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=req.url)

        return {
            "url": req.url,
            "html": result.html,
            "markdown": result.markdown,
            "metadata": result.metadata
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
