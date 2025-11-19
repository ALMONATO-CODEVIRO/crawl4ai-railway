from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

class SelectorRequest(BaseModel):
    url: str
    selectors: list[str]
    wait_until: str = "domcontentloaded"

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

        for label in request.selectors:
            found = False
            for item in soup.select(".item"):
                title = item.select_one(".title")
                description = item.select_one(".description")
                if title and description and label.lower() in title.text.lower():
                    results[label] = description.get_text(strip=True)
                    found = True
                    break
            if not found:
                results[label] = ""  # o None si prefieres

        return {
            "url": request.url,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))








