from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import run_crawl
import os
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

# Inicializa la app
app = FastAPI()

# Modelos de entrada y salida
class CrawlInput(BaseModel):
    text: str

class CrawlOutput(BaseModel):
    metadata: dict
    sections: list

# Endpoint de prueba
@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI + crawl4ai activo"}

# Endpoint principal
@app.post("/crawl", response_model=CrawlOutput)
def crawl_endpoint(data: CrawlInput):
    try:
        result = run_crawl(
            text=data.text,
            metadata={"source": "railway"},
            strategy=os.getenv("CRAWL_STRATEGY", "default")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



