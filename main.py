from fastapi import FastAPI
from fastapi.responses import JSONResponse
from crawl4ai import AsyncWebCrawler, LLMExtractor

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Crawl4AI service running"}

@app.post("/extract-product")
async def extract_product(payload: dict):
    url = payload.get("url")

    try:
        extractor = LLMExtractor(
            model="gpt-4o-mini",
            schema={
                "title": "string",
                "price": "string",
                "images": ["string"],
                "description": "string",
            }
        )

        crawler = AsyncWebCrawler()
        result = await crawler.run(url, extractor=extractor)

        return result.data

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

