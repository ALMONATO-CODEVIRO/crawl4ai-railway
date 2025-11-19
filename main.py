from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from crawl4ai import AsyncWebCrawler
from crawl4ai import LLMExtractor

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Crawl4AI service running"}

@app.get("/crawl")
async def crawl_url(url: str):
    try:
        crawler = AsyncWebCrawler()
        extractor = LLMExtractor()

        result = await crawler.run(url, extractor=extractor)

        return {
            "url": url,
            "content": result.markdown if hasattr(result, "markdown") else str(result)
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

