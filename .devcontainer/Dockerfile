FROM python:3.12-slim

WORKDIR /workspace

# Instalar dependencias necesarias para ImageMagick + Wand
RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    libmagickcore-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
