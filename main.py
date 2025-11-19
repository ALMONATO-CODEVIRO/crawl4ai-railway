from fastapi import FastAPI
from fastapi.responses import JSONResponse
from crawl4ai import AsyncWebCrawler, LLMExtractor

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Crawl4AI service running - LLMExtractor active"}

# -------------------------
# ENDPOINT DE SCRAPING SIMPLE
# -------------------------
@app.post("/crawl")
async def crawl_url(data: dict):
    url = data.get("url")

    try:
        crawler = AsyncWebCrawler()
        result = await crawler.run(url)

        return {
            "url": url,
            "content": result.markdown if hasattr(result, "markdown") else str(result)
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------
# ENDPOINT AVANZADO CON IA (LLMExtractor)
# -------------------------
@app.post("/extract-product")
async def extract_product(data: dict):
    url = data.get("url")

    extractor = LLMExtractor(
        query="""
        Extrae la información del producto en formato JSON con estructura:

        {
            "name": "",
            "brand": "",
            "price": "",
            "presentation": "",
            "description": "",
            "image": "",
            "availability": ""
        }
        """
    )

    try:
        crawler = AsyncWebCrawler()
        result = await crawler.run(url, extractor=extractor)

        return {
            "url": url,
            "product": result.extracted_content
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
