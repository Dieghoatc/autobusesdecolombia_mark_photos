FROM python:3.12-slim

WORKDIR /workspace

# Instalar dependencias útiles + libvips
RUN apt-get update && apt-get install -y \
    git curl build-essential \
    libvips-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar linters/formatters opcionales
RUN pip install --no-cache-dir black ruff mypy
