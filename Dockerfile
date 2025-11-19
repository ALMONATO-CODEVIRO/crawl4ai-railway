FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 1. Dependencias del sistema
RUN apt-get update && apt-get install -y \
    git curl wget unzip build-essential \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Requisitos Python
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 3. Instalar Playwright y Chromium
RUN playwright install-deps
RUN playwright install chromium

# 4. Copiar proyecto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



