from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import base64
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

openai_api_key = os.getenv("OPENAI_API_KEY")

# 📥 MODELO DE ENTRADA
class URLRequest(BaseModel):
    url: str
    wait_until: str = "domcontentloaded"  # 'load', 'domcontentloaded', 'networkidle'

class SelectorItem(BaseModel):
    label: Optional[str] = None  # Puedes dejarlo sin usar si no te interesa
    selector: str
    attr: Optional[str] = None   # Si quieres extraer 'src', 'href', etc.
    select_all: Optional[bool] = False  # Para futuro uso: múltiples elementos

class SelectorRequest(BaseModel):
    url: str
    wait_until: Optional[str] = "load"
    selectors: List[SelectorItem]

# 🔍 /CRAWL – Devuelve HTML y Markdown
@app.post("/crawl")
async def crawl(request: URLRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(request.url, wait_until=request.wait_until, timeout=60000)
            content = await page.content()
            await browser.close()

        # Parse con BeautifulSoup y Markdown
        soup = BeautifulSoup(content, "html.parser")
        main = soup.find("main") or soup.body or soup
        html = str(main)
        markdown = md(html)

        return {
            "url": request.url,
            "markdown": markdown,
            "html": html,
            "metadata": metadata
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📸 /SCREENSHOT – Devuelve imagen base64 en PNG
@app.post("/screenshot")
async def screenshot(request: URLRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(request.url, wait_until=request.wait_until, timeout=60000)
            image = await page.screenshot(full_page=True, type="png")
            await browser.close()

        return {
            "image_base64": base64.b64encode(image).decode("utf-8"),
            "content_type": "image/png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧪 /SELECTORS – Extrae texto desde selectores CSS
# 🧪 /SELECTORS – Extrae texto desde selectores CSS (versión funcional universal)
@app.post("/selectors")
async def selectors(request: SelectorRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(request.url, wait_until=request.wait_until, timeout=60000)
            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        results = {}

        for item in request.selectors:
            label = item.label or item.selector
            selected_element = soup.select_one(item.selector)

            if selected_element:
                if item.attr:
                    results[label] = selected_element.get(item.attr, "")
                else:
                    results[label] = selected_element.get_text(strip=True)
            else:
                results[label] = ""

        return {
            "url": request.url,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))









