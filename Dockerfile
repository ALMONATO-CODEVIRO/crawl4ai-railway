FROM python:3.11-slim

# Evitar preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar dependencias base
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Crear carpeta de la app
WORKDIR /app

# 3. Copiar requirements
COPY requirements.txt .

# 4. Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instalar navegadores de Playwright
RUN playwright install --with-deps chromium

# 6. Copiar el proyecto
COPY . .

# 7. Exponer puerto Railway
EXPOSE 8000

# 8. Comando para correr FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

