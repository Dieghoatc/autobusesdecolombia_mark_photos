# Imagen ligera de Python con Debian
FROM python:3.12-slim

# Configurar el directorio de trabajo
WORKDIR /app

# Instalar dependencias necesarias para Libvips
RUN apt-get update && apt-get install -y \
    libvips libvips-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tu código
COPY . .

# Exponer el puerto que Railway usará (ej: FastAPI en 8000)
EXPOSE 8000

# Comando de inicio (ajusta según tu framework)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
