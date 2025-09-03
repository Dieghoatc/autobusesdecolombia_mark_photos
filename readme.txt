Project Structure

mi-proyecto/
├─ .devcontainer/
│  ├─ Dockerfile
│  └─ devcontainer.json
├─ .vscode/
│  └─ launch.json
├─ app/
│  └─ main.py
├─ requirements.txt

1. Up dev environment with: dev container: reopen in container
2. Before up dev environment, we only have running the environment
3. Up server FastAPI with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Perfecto 🙌, aquí tienes tu README.md completo y listo para pegar en tu repo.

Incluye títulos, pasos claros, y algunos badges para que quede más pro.

🚀 FastAPI Dev Container

Entorno de desarrollo de FastAPI + Python corriendo dentro de Docker con soporte para VS Code Dev Containers.
No necesitas instalar Python en tu máquina local 🚫🐍.

📋 Requisitos previos

Docker Desktop

Visual Studio Code

Extensión de VS Code: Dev Containers

📂 Estructura del proyecto
mi-proyecto/
├─ .devcontainer/
│  ├─ Dockerfile
│  └─ devcontainer.json
├─ .vscode/
│  └─ launch.json
├─ app/
│  └─ main.py
└─ requirements.txt

🐳 Configuración del Dev Container
.devcontainer/Dockerfile
FROM python:3.12-slim

WORKDIR /workspace

# Dependencias útiles de sistema
RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Herramientas de desarrollo opcionales
RUN pip install --no-cache-dir black ruff mypy

.devcontainer/devcontainer.json
{
  "name": "Python DevContainer",
  "build": {
    "dockerfile": "Dockerfile"
  },
  "workspaceFolder": "/workspace",
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind"
  ],
  "settings": {
    "python.defaultInterpreterPath": "/usr/local/bin/python",
    "python.linting.enabled": true,
    "python.formatting.provider": "black"
  },
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance"
  ],
  "postCreateCommand": "pip install -r requirements.txt"
}

📦 Dependencias de Python
requirements.txt
fastapi
uvicorn[standard]

📝 Código base
app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hola Mundo desde Docker + Python + FastAPI"}

🐞 Debugging en VS Code
.vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI (Uvicorn)",
      "type": "python",
      "request": "launch",
      "program": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "console": "integratedTerminal"
    }
  ]
}

▶️ Levantar el entorno

Abre el proyecto en VS Code.

Ctrl + Shift + P → Dev Containers: Reopen in Container.

En la terminal integrada (ya dentro del contenedor), ejecuta:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

🌐 Probar el servidor

http://localhost:8000
 → Respuesta JSON.

http://localhost:8000/docs
 → Documentación interactiva (Swagger).

🔍 Depuración con breakpoints

Abre la pestaña Run & Debug en VS Code.

Selecciona FastAPI (Uvicorn).

Inicia con F5.

Coloca breakpoints en tu código y VS Code se detendrá ahí.

🚀 Arranque automático (opcional)

Si quieres que el servidor se inicie solo al abrir el Dev Container, agrega a .devcontainer/devcontainer.json:

"postStartCommand": "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
