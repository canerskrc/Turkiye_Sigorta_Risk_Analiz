"""
Saha fotoğraflarını doğrulayan, yeniden boyutlandıran ve güvenli saklayan yardımcı modül.
"""
from pathlib import Path
from PIL import Image
import uuid
from config.settings import UPLOADS_DIR

def save_and_compress_image(uploaded_file_bytes: bytes, original_filename: str, max_size=(1200, 1200)) -> str:
    """Yüklenen fotoğrafı sıkıştırıp UPLOADS_DIR içine kaydeder, göreceli dosya yolunu döner."""
    extension = Path(original_filename).suffix.lower()
    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        extension = ".jpg"
    
    unique_name = f"photo_{uuid.uuid4().hex[:10]}{extension}"
    target_path = UPLOADS_DIR / unique_name
    
    # Geçici dosyaya yazıp Pillow ile açalım
    import io
    img = Image.open(io.BytesIO(uploaded_file_bytes))
    
    # RGB formatına dönüştür (PNG transparanlığı veya CMYK için)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(target_path, "JPEG", quality=85, optimize=True)
    
    return str(target_path)
