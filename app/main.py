from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
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


@app.post("/upload/")
async def upload_image(
    image: UploadFile = File(...),
    author: str = Form(...),
    location: str = Form(...)
):
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

        
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGBA")

      
        text = Image.new("RGBA", pil_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text)

        base_size = pil_image.height // 55   # 1/30 del alto
        fontPrimary = ImageFont.truetype("assets/fonts/Segoe UI Bold.ttf", base_size)
        fontSecundary = ImageFont.truetype("assets/fonts/Segoe UI Bold.ttf", base_size - 2)

        authorCopyR = f"{author} ©"

        bbox_author = draw.textbbox((0, 0), authorCopyR, font=fontPrimary)
        author_width = bbox_author[2] - bbox_author[0]
        author_height = bbox_author[3] - bbox_author[1]

        bbox_location = draw.textbbox((0, 0), location, font=fontSecundary)
        location_width = bbox_location[2] - bbox_location[0]
        location_height = bbox_location[3] - bbox_location[1]

        spacing = pil_image.height // 200
        total_text_height = author_height + location_height + spacing
        max_text_width = max(author_width, location_width)

        padding = pil_image.width // 100
        x_author = pil_image.width - author_width - padding
        x_location = pil_image.width - location_width - padding
        y_start = pil_image.height - total_text_height - padding

        y_author = y_start
        y_location = y_start + author_height + spacing

        gradient_width = int(max_text_width * 1.2)
        gradient_start_x = pil_image.width - gradient_width

        for i in range(gradient_width):
            alpha = int(180 * (i / gradient_width))
            if alpha > 0:
                draw.rectangle(
                    [gradient_start_x + i, y_start - 5,
                     gradient_start_x + i + 1, pil_image.height],
                    fill=(90, 90, 90, alpha)
                )

        shadow_offset = max(1, pil_image.height // 300)
        draw.text((x_author + shadow_offset, y_author + shadow_offset),
                  authorCopyR, font=fontPrimary, fill=(0, 0, 0, 80))
        draw.text((x_location + shadow_offset, y_location + shadow_offset),
                  location, font=fontSecundary, fill=(0, 0, 0, 80))

        draw.text((x_author, y_author), authorCopyR,
                  font=fontPrimary, fill=(255, 255, 255, 255))
        draw.text((x_location, y_location), location,
                  font=fontSecundary, fill=(255, 255, 255, 255))

        watermarked = Image.alpha_composite(pil_image, text)

        # Set Logo
        logo_path = Path("assets/logox3.png")
        if logo_path.exists():
            try:
                logo = Image.open(logo_path).convert("RGBA")
                max_logo_size = int(min(pil_image.width, pil_image.height) * 0.2)
                logo.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
                pos_x = 0
                pos_y = watermarked.height - logo.height
                watermarked.paste(logo, (pos_x, pos_y), logo)
            except Exception as e:
                print(f"Error al procesar el logo: {e}")

        # Response memory
        output_filename = f"marked_{image.filename.split('.')[0]}.avif"
        buf = io.BytesIO()
        max_size = (2000, 2000)
        watermarked.thumbnail(max_size, Image.Resampling.LANCZOS)
        watermarked.save(
            buf, 
            "AVIF", 
            quality=80,  
            method=6, 
            optimize=True
        )
        buf.seek(0)

        return StreamingResponse(
            buf,
            media_type="image/avif",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Servidor de watermark funcionando correctamente"}
