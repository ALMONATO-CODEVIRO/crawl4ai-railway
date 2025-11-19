from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from crawl4ai import WebCrawler  # ajusta si la API es distinta en tu versión

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Crawl4AI service running"}

@app.get("/crawl")
def crawl_url(url: str = Query(..., description="URL a extraer")):
    try:
        crawler = WebCrawler()
        result = crawler.crawl(url)
        # Dependiendo de la versión, adaptas los atributos
        return {
            "url": url,
            "text": result.text if hasattr(result, "text") else str(result),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
