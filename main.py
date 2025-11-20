from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, RootModel
from typing import List, Optional, Union
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

# ------------------------- MODELOS ---------------------------

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

class PreciosRequest(RootModel[Union[SelectorRequest, List[SelectorRequest]]]):
    pass


# -------------------- FUNCIÓN EXTRA INVIMA VTEX --------------------

async def extract_invima_vtex(page):
    """
    Extrae el INVIMA de una página VTEX buscando filas dinámicas de especificaciones.
    """
    try:
        await page.wait_for_selector(
            "div.vtex-product-specifications-1-x-specificationsTableRow",
            timeout=8000
        )

        rows = page.locator("div.vtex-product-specifications-1-x-specificationsTableRow")
        count = await rows.count()

        for i in range(count):
            row = rows.nth(i)

            header_el = row.locator(
                "div.vtex-product-specifications-1-x-specificationsTableHead"
            )
            header = await header_el.inner_text()

            if "invima" in header.lower():
                value_el = row.locator(
                    "span.vtex-product-specifications-1-x-specificationValue"
                )
                return await value_el.inner_text()

    except:
        pass

    return ""


# --------------------------- /CRAWL ---------------------------

@app.post("/crawl")
async def crawl(request: URLRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            page = await context.new_page()
            await page.goto(request.url, wait_until=request.wait_until, timeout=60000)
            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        main = soup.find("main") or soup.body or soup
        html = str(main)
        markdown = md(html)

        return {"url": request.url, "markdown": markdown, "html": html}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------- /SCREENSHOT ---------------------------

@app.post("/screenshot")
async def screenshot(request: URLRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(request.url, wait_until="domcontentloaded", timeout=60000)

            try:
                await page.wait_for_selector("span.box__price--current", timeout=15000)
            except:
                pass

            image = await page.screenshot(full_page=True)
            await browser.close()

        return {
            "image_base64": base64.b64encode(image).decode(),
            "content_type": "image/png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------- /SELECTORS ---------------------------

@app.post("/selectors")
async def extract_selectors(request: SelectorRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(request.url, wait_until=request.wait_until, timeout=60000)

            # Esperar selectores dinámicos
            for item in request.selectors:
                try:
                    await page.wait_for_selector(item.selector, timeout=10000)
                except:
                    pass

            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        results = {}

        for item in request.selectors:
            label = item.label or item.selector
            element = soup.select_one(item.selector)

            if element:
                results[label] = (
                    element.get(item.attr) if item.attr else element.get_text(strip=True)
                )
            else:
                results[label] = ""

        return {"url": request.url, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------- /PRECIOS ---------------------------

@app.post("/precios")
async def precios(request: PreciosRequest):

    data = request.root

    # --------- SI ES SOLO UN BLOQUE ----------
    if isinstance(data, SelectorRequest):
        return await extract_selectors(data)

    # --------- SI ES LISTA DE BLOQUES ----------
    elif isinstance(data, list):

        results = []

        for block in data:

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(block.url, wait_until=block.wait_until, timeout=60000)

                # Ejecutar tus selectores normales
                select_results = await extract_selectors(block)

                # Extraer INVIMA dinámico si es VTEX
                invima_auto = await extract_invima_vtex(page)

                await browser.close()

            # Mezclar resultados
            select_results["results"]["invima_auto"] = invima_auto

            results.append(select_results)

        return results

    else:
        raise HTTPException(status_code=400, detail="Formato inválido")


class MultiURLRequest(BaseModel):
    urls: List[str]








