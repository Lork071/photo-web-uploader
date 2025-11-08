from PIL import Image
from io import BytesIO
import os
from typing import Tuple, Optional


class ImageProcessor:
    """Třída pro zpracování obrázků - vytváření thumbnailů a komprimace"""
    
    # Podporované formáty
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    
    def __init__(self, thumbnail_size: int = 400, compress_quality: int = 85):
        """
        Args:
            thumbnail_size: maximální rozměr thumbnailů (px)
            compress_quality: kvalita komprimace (1-100)
        """
        self.thumbnail_size = thumbnail_size
        self.compress_quality = compress_quality
    
    @staticmethod
    def is_image(filename: str) -> bool:
        """Zkontroluje, zda je soubor obrázek"""
        return filename.lower().endswith(ImageProcessor.SUPPORTED_FORMATS)
    
    def create_thumbnail(self, image_path: str) -> Tuple[bool, Optional[bytes], str]:
        """
        Vytvoří thumbnail z obrázku
        Returns: (success, thumbnail_bytes, message)
        """
        try:
            with Image.open(image_path) as img:
                # Konverze RGBA na RGB pokud potřeba (kvůli JPEG)
                if img.mode == 'RGBA':
                    # Vytvoř bílé pozadí
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Alpha channel jako maska
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Vypočítej nové rozměry (zachovej poměr stran)
                img.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
                
                # Ulož do BytesIO
                output = BytesIO()
                
                # Urči formát
                format_to_save = 'JPEG'
                if image_path.lower().endswith('.png'):
                    format_to_save = 'PNG'
                
                img.save(output, format=format_to_save, quality=self.compress_quality, optimize=True)
                
                return True, output.getvalue(), "Thumbnail vytvořen"
        
        except Exception as e:
            return False, None, f"Chyba při vytváření thumbnailů: {str(e)}"
    
    def compress_image(self, image_path: str) -> Tuple[bool, Optional[bytes], str]:
        """
        Zkomprimuje obrázek
        Returns: (success, compressed_bytes, message)
        """
        try:
            with Image.open(image_path) as img:
                # Konverze RGBA na RGB pokud potřeba
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                output = BytesIO()
                
                # Urči formát
                format_to_save = 'JPEG'
                if image_path.lower().endswith('.png'):
                    format_to_save = 'PNG'
                
                # Komprimuj
                img.save(output, format=format_to_save, quality=self.compress_quality, optimize=True)
                
                original_size = os.path.getsize(image_path)
                compressed_size = len(output.getvalue())
                saved_percent = int((1 - compressed_size / original_size) * 100)
                
                return True, output.getvalue(), f"Komprimováno (ušetřeno {saved_percent}%)"
        
        except Exception as e:
            return False, None, f"Chyba při komprimaci: {str(e)}"
    
    def get_image_info(self, image_path: str) -> Tuple[bool, dict]:
        """
        Získá informace o obrázku
        Returns: (success, info_dict)
        """
        try:
            with Image.open(image_path) as img:
                info = {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': os.path.getsize(image_path)
                }
                return True, info
        except Exception as e:
            return False, {'error': str(e)}
    
    def create_thumbnail_from_bytes(self, image_bytes: bytes) -> Tuple[bool, Optional[bytes], str]:
        """
        Vytvoří thumbnail z byte dat
        Returns: (success, thumbnail_bytes, message)
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            
            # Konverze RGBA na RGB pokud potřeba
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            img.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=self.compress_quality, optimize=True)
            
            return True, output.getvalue(), "Thumbnail vytvořen"
        
        except Exception as e:
            return False, None, f"Chyba při vytváření thumbnailů: {str(e)}"
    
    def set_thumbnail_size(self, size: int):
        """Nastaví velikost thumbnailů"""
        self.thumbnail_size = size
    
    def set_compress_quality(self, quality: int):
        """Nastaví kvalitu komprimace (1-100)"""
        if 1 <= quality <= 100:
            self.compress_quality = quality
