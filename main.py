from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from crawl4ai import Crawl4Ai   # API correcta

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Crawl4AI service running"}

@app.get("/crawl")
async def crawl_url(url: str = Query(..., description="URL a extraer")):
    try:
        crawler = Crawl4Ai()
        result = crawler.run(url)

        return {
            "url": url,
            "content": result.markdown if hasattr(result, "markdown") else str(result)
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
