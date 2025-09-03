from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont
import io
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio uploads si no existe
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload/")
async def upload_image(image: UploadFile = File(...), author: str = Form(...), location: str = Form(...)):
    try:
        # Validar que el archivo sea una imagen
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Leer y abrir la imagen (mantener tamaño original)
        image_data = await image.read()
        # CAMBIO: Usar un nombre diferente para evitar conflicto con el parámetro
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGBA")

        # --- Añadir texto con fondo oscuro ---
        txt = Image.new("RGBA", pil_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)

        # Fuente más grande para el texto del autor
        try: 
            fontPrimary = ImageFont.truetype("assets/fonts/Segoe UI Bold.ttf", 22)
            fontSecundary = ImageFont.truetype("assets/fonts/Segoe UI Bold.ttf", 20)

        except IOError:
            # Fallback a fuente por defecto
            fontPrimary = ImageFont.load_default()
            fontSecundary = ImageFont.load_default()
        
        authorCopyR = f"{author} ©"

        # Calcular dimensiones del texto usando textbbox
        bbox_author = draw.textbbox((0, 0), authorCopyR, font=fontPrimary)
        author_width = bbox_author[2] - bbox_author[0]
        author_height = bbox_author[3] - bbox_author[1]

        bbox_location = draw.textbbox((0, 0), location, font=fontSecundary)
        location_width = bbox_location[2] - bbox_location[0]
        location_height = bbox_location[3] - bbox_location[1]

        # Calcular posiciones y dimensiones
        spacing = 2
        total_text_height = author_height + location_height + spacing
        max_text_width = max(author_width, location_width)
        
        # Posición del texto (esquina inferior derecha)
        padding = 8
        x_author = pil_image.width - author_width - padding
        x_location = pil_image.width - location_width - padding
        y_start = pil_image.height - total_text_height - padding

        y_author = y_start
        y_location = y_start + author_height + spacing
        
        # Crear fondo con gradiente hacia la izquierda
        gradient_width = max_text_width + 40
        gradient_start_x = pil_image.width - gradient_width
        
        # Crear gradiente de transparente a negro (de izquierda a derecha)
        for i in range(gradient_width):
            # Calcular alpha del gradiente (más opaco hacia la derecha)
            alpha = int(180 * (i / gradient_width))  # De 0 a 180
            if alpha > 0:
                draw.rectangle(
                    [gradient_start_x + i, y_start - 5,
                     gradient_start_x + i + 1, pil_image.height],
                    fill=(90, 90, 90, alpha)
                )

        # Dibujar texto blanco con sombra para mejor legibilidad
        shadow_offset = 1
        # Sombra para author
        draw.text((x_author + shadow_offset, y_author + shadow_offset), authorCopyR, font=fontPrimary, fill=(0, 0, 0, 128))
        # Sombra para location
        draw.text((x_location + shadow_offset, y_location + shadow_offset), location, font=fontSecundary, fill=(0, 0, 0, 128))
        
        # Texto principal
        draw.text((x_author, y_author), authorCopyR, font=fontPrimary, fill=(255, 255, 255, 255))
        draw.text((x_location, y_location), location, font=fontSecundary, fill=(255, 255, 255, 255))

        # Combinar la imagen con el texto
        watermarked = Image.alpha_composite(pil_image, txt)

        # --- Agregar el logo (esquina inferior izquierda - tamaño original) ---
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            try:
                logo = Image.open(logo_path).convert("RGBA")
                
                # Redimensionar solo si el logo es demasiado grande para la imagen
                max_logo_size = min(300, pil_image.width // 4, pil_image.height // 4)
                if logo.width > max_logo_size or logo.height > max_logo_size:
                    logo.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)

                # Posición (esquina inferior izquierda)
                pos_x = 0
                pos_y = watermarked.height - logo.height

                # Pegar logo usando la máscara alpha
                watermarked.paste(logo, (pos_x, pos_y), logo)
            except Exception as e:
                print(f"Error al procesar el logo: {e}")

        # --- Guardar como WebP optimizado ---
        output_filename = f"marked_{image.filename.split('.')[0]}.webp"
        marked_path = UPLOAD_DIR / output_filename
        
        # Convertir a RGB para WebP y guardar
        watermarked.convert("RGB").save(
            marked_path, 
            "WEBP", 
            quality=90, 
            method=6,
            optimize=True
        )

        return FileResponse(
            marked_path, 
            media_type="image/webp",
            filename=output_filename,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mark client process image: {str(e)}")

# Endpoint adicional para verificar el estado del servidor
@app.get("/")
async def root():
    return {"message": "Servidor de watermark funcionando correctamente"}

# Para ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)