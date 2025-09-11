from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pathlib import Path

import io
from wand.image import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_image(
    image: UploadFile = File(...),
    author: str = Form(...),
    location: str = Form(...)
):
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="The file must be an image")
        
        toStream = io.BytesIO()

        with Image(file=image.file) as img:
            # Redimensionar si es demasiado grande
            MAX_WIDTH = 2000
            if img.width > MAX_WIDTH:
                img.resize(MAX_WIDTH, int((MAX_WIDTH / img.width) * img.height))

            # Cambiar formato a AVIF
            img.format = "avif"
            img.save(file=toStream)

        toStream.seek(0)

        return StreamingResponse(
            toStream,
            media_type="image/avif",
            headers={"Content-Disposition": "attachment; filename=output.avif"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Servidor de watermark funcionando correctamente"}
