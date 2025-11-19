FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    git curl wget unzip build-essential \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Instalar dependencias Python
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# 3. Instalar Chromium para Playwright
RUN playwright install-deps
RUN playwright install chromium

# 4. Copiar proyecto
COPY . .

# 5. Puerto
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


