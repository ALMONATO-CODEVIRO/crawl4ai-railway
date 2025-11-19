FROM ubuntu:22.04

# Evitar preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar Python y dependencias básicas
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    git wget curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar dependencias del sistema necesarias para Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libxcomposite1 libxrandr2 \
    libxdamage1 libxfixes3 libpango-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libasound2 libxshmfence1 libgbm1 \
    libx11-6 libx11-xcb1 libxcb1 libxcursor1 libxi6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Directorio de trabajo
WORKDIR /app

# 4. Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instalar Playwright + navegadores
RUN playwright install
RUN playwright install-deps

# 6. Copiar código
COPY . .

# 7. Exponer puerto
ENV PORT=8000

# 8. Ejecutar API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
