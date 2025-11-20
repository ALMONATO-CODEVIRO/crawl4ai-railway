# precios.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

router = APIRouter()

class MultiURLRequest(BaseModel):
    urls: List[str]

@router.post("/precios")
async def obtener_precios(request: MultiURLRequest):
    resultados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in request.urls:
            dominio = url.lower()
            resultado = {"url": url}

            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                # ✅ Cruz Verde
                if "cruzverde.com.co" in dominio:
                    precio_actual = soup.select_one("span.box__price--current")
                    precio_anterior = soup.select_one("span.box__price--old")
                    resultado["precio_actual"] = precio_actual.get_text(strip=True) if precio_actual else ""
                    resultado["precio_anterior"] = precio_anterior.get_text(strip=True) if precio_anterior else ""

                # ✅ Farmatodo
                elif "farmatodo.com.co" in dominio:
                    precio_actual = soup.select_one("div.Price span.MuiTypography-root")
                    precio_anterior = soup.select_one("div.price_old")
                    resultado["precio_actual"] = precio_actual.get_text(strip=True) if precio_actual else ""
                    resultado["precio_anterior"] = precio_anterior.get_text(strip=True) if precio_anterior else ""

                # ✅ Droguería Alemana
                elif "droguerialaalemana.com" in dominio:
                    precio_actual = soup.select_one("span.price")
                    precio_anterior = soup.select_one("span.old-price")
                    resultado["precio_actual"] = precio_actual.get_text(strip=True) if precio_actual else ""
                    resultado["precio_anterior"] = precio_anterior.get_text(strip=True) if precio_anterior else ""

                else:
                    resultado["error"] = "Dominio no soportado aún."

            except Exception as e:
                resultado["error"] = str(e)

            resultados.append(resultado)

        await browser.close()

    return {"resultados": resultados}
