from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont

import io
import pyvips
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
        image_vips = pyvips.Image.new_from_buffer(image_data, "")

        image_vips_base = image_vips.colourspace("srgb")
        
        MAX_WIDTH = 2000
        dpi = 72

        if image_vips_base.width > MAX_WIDTH:
            scale = MAX_WIDTH / image_vips_base.width
            image_vips_base = image_vips_base.resize(scale)

        if image_vips_base.width < 2000:
            font_size = 12
            pad_x, pad_y = 5, 5
        else:
            font_size = 24
            pad_x, pad_y = 20, 10

        
        # Insert Text
        watermark_text = f"{author} ©\n{location}"
        text_mask = pyvips.Image.text(
             watermark_text,
                 width= image_vips_base.width // 2,             
                 font=f"sans bold {font_size}",
                 dpi=dpi,
                 align="high"         
             )              

        white = pyvips.Image.black(text_mask.width, text_mask.height).new_from_image([255, 255, 255])
        text_rgba = white.bandjoin(text_mask).cast("uchar").copy(interpretation="srgb").premultiply() 

        # --- dimensiones ---
        tw, th = text_rgba.width, text_rgba.height
        gw, gh = tw + pad_x * 2, th + pad_y * 2

        # --- gradiente alpha horizontal transparente → opaco ---
        x = pyvips.Image.xyz(gw, gh)[0]
        t = x * (1.0 / max(gw - 1, 1))
        alpha = (t * 180).cast("uchar")   # alpha 0..180

        base_gray = 30
        bg_rgb = pyvips.Image.black(gw, gh).new_from_image(base_gray)
        bg = bg_rgb.bandjoin([bg_rgb, bg_rgb, alpha])  # R,G,B,A
        bg = bg.copy(interpretation="srgb").premultiply()
        
        offset_x, offset_y = pad_x, pad_y
        watermark_with_bg = bg.composite2(text_rgba, "over", x=offset_x, y=offset_y)

        pos_x = max(image_vips_base.width - watermark_with_bg.width, 0)
        pos_y = max(image_vips_base.height - watermark_with_bg.height, 0)
        
        final = image_vips_base.composite2(watermark_with_bg, "over", x = pos_x, y = pos_y)   

        # Set Logo
        logo_path = Path("assets/logox3.png")
        if logo_path.exists():
            logo = pyvips.Image.new_from_file(str(logo_path), access="sequential")
            if logo.bands == 3:
                alpha = pyvips.Image.black(logo.width, logo.height).new_from_image(255)
                logo = logo.bandjoin(alpha)

            # Redimensionar logo si es muy grande
            max_logo_width = int(image_vips_base.width * 0.15)
            max_logo_height = int(image_vips_base.height * 0.15)
            scale_w = min(1.0, max_logo_width / logo.width)
            scale_h = min(1.0, max_logo_height / logo.height)
            scale = min(scale_w, scale_h)
            if scale < 1.0:
                logo = logo.resize(scale)

            # Posición inferior izquierda
            logo_x = 0
            logo_y = image_vips_base.height - logo.height
            final = final.composite2(logo, "over", x=logo_x, y=logo_y)   
        
        buffer: bytes = final.write_to_buffer(".avif", Q=80, effort=6)
        toStream = io.BytesIO(buffer)

        return StreamingResponse(
            toStream,
            media_type="image/avif",
            headers={"Content-Disposition": f"attachment; filename=output.avif"}
        )
           
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Servidor de watermark funcionando correctamente"}


