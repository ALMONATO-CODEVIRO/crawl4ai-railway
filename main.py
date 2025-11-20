from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import base64
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from fastapi import Request
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
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
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
# 🧪 /SELECTORS – Extrae texto desde selectores CSS (versión funcional universal)
@app.post("/selectors")
async def extract_selectors(request: SelectorRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            page = await browser.new_page()
            await page.goto(request.url, wait_until=request.wait_until, timeout=60000)

            # ✅ Esperar a que cada selector esté presente antes de capturar el contenido
            for item in request.selectors:
                try:
                    await page.wait_for_selector(item.selector, timeout=15000)
                except Exception:
                    # Si no aparece, continuamos sin romper todo
                    pass

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


@app.post("/precios")
async def precios(request: URLRequest):
    url = request.url

    if not url:
        raise HTTPException(status_code=400, detail="La URL es requerida")

    # 🌐 Detectar tienda según dominio y definir selectores
    if "farmatodo" in url:
        selectors = [
            SelectorItem(label="precio_actual", selector="span.box__price--current"),
            SelectorItem(label="precio_anterior", selector="span.box__price--before"),
        ]
    elif "cruzverde" in url:
        selectors = [
            SelectorItem(label="precio_actual", selector="span.font-bold.text-primary"),
            SelectorItem(label="precio_anterior", selector="span.line-through.text-gray-500"),
        ]
    elif "tudrogueriavirtual" in url:
        selectors = [
            SelectorItem(label="precio_actual", selector="span.product-price"),
            SelectorItem(label="precio_anterior", selector="span.old-price"),
        ]
    else:
        raise HTTPException(status_code=400, detail="Tienda no soportada")

    # 🧪 Reutilizar la lógica del endpoint /selectors
    selector_request = SelectorRequest(
        url=url,
        wait_until="networkidle",
        selectors=selectors
    )

    return await extract_selectors(selector_request)
    

class MultiURLRequest(BaseModel):
    urls: List[str]







