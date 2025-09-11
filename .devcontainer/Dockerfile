FROM python:3.12-slim

WORKDIR /workspace

# Instalar dependencias + libvips + herramientas de imagen
RUN apt-get update && apt-get install -y \
    libvips-dev \
    libvips-tools \
    libvips42 \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar linters/formatters opcionales
RUN pip install --no-cache-dir black ruff mypy





