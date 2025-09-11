FROM python:3.12-slim

WORKDIR /workspace

# Instalar dependencias necesarias + ImageMagick
RUN apt-get update && apt-get install -y \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements.txt si existe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# Comando por defecto
CMD [ "bash" ]
