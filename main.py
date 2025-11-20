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
    wait_until: str = "domcontentloaded"

class SelectorItem(BaseModel):
    selector: str
    label: Optional[str] = None
    attr: Optional[str] = None

class SelectorRequest(BaseModel):
    url: str
    wait_until: Optional[str] = "networkidle"
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
            "html": html
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📸 /SCREENSHOT – Devuelve imagen base64 en PNG
@app.post("/screenshot")
async def screenshot(request: URLRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            page = await context.new_page()

            try:
                await page.goto(request.url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                raise HTTPException(status_code=504, detail=f"Error en carga de la página: {str(e)}")

            try:
                await page.wait_for_selector("span.box__price--current", timeout=15000)
            except:
                pass  # No rompas si no encuentra el selector, igual toma screenshot

            image = await page.screenshot(full_page=True, type="png")
            await browser.close()

        return {
            "image_base64": base64.b64encode(image).decode("utf-8"),
            "content_type": "image/png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo general: {str(e)}")

# 🧪 /SELECTORS – Extrae texto desde selectores CSS

@app.post("/precios")
async def precios(request: Request):
    body = await request.json()
    url = body.get("url")

    if not url:
        raise HTTPException(status_code=400, detail="La URL es requerida")

    # 🌐 Detectar tienda según dominio
    if "farmatodo" in url:
        selectors = [
            {"label": "precio_actual", "selector": "span.box__price--current"},
            {"label": "precio_anterior", "selector": "span.box__price--before"},
        ]
    elif "cruzverde" in url:
        selectors = [
            {"label": "precio_actual", "selector": "span.font-bold.text-prices"},
            {"label": "precio_anterior", "selector": "div.line-through.order-3.ng-star-inserted"},
        ]
    elif "tudrogueriavirtual" in url:
        selectors = [
            {"label": "precio_actual", "selector": "span.vtex-store-components-3-x-sellingPriceValue"},
            {"label": "precio_anterior", "selector": "span.vtex-store-components-3-x-listPriceValue"},
        ]
    else:
        raise HTTPException(status_code=400, detail="Tienda no soportada")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Esperar cada selector
            for item in selectors:
                try:
                    await page.wait_for_selector(item["selector"], timeout=15000)
                except:
                    pass  # Si no aparece el selector, lo ignoramos

            html = await page.content()
            await browser.close()

        soup = BeautifulSoup(html, "html.parser")
        results = {}

        for item in selectors:
            label = item["label"]
            selector = item["selector"]
            element = soup.select_one(selector)

            if element:
                results[label] = element.get_text(strip=True)
            else:
                results[label] = ""

        return {
            "url": url,
            "resultados": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))










