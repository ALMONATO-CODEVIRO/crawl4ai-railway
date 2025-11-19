FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app

# ---- Dependencias ----
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Código de la app ----
COPY . .

# Playwright (como lo tenías)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Solo a nivel documental, no afecta a Railway pero ayuda localmente
EXPOSE 8080

# 👉 IMPORTANTE: usar el puerto que venga en $PORT (y si no existe, 8080)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers"]










