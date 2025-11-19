from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, LLMExtractor
import json

class ProductRequest(BaseModel):
    url: str

@app.post("/extract-product")
async def extract_product(req: ProductRequest):
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=req.url,
                extractors=[
                    LLMExtractor(
                        schema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "price": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["name", "price"]
                        },
                        llm="openai:gpt-4o-mini"
                    )
                ]
            )

        data = json.loads(result.extracted_content)

        return {
            "url": req.url,
            "product": data
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
