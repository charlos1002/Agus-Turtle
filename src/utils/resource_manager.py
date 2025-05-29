from pathlib import Path
import pygame
import sys
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.cache = {}

    def load_image(self, base_filename: str) -> pygame.Surface:
        """
        Memuat gambar.
        Jika base_filename sudah memiliki ekstensi (misal "image.png"), akan memuat itu.
        Jika tidak ada ekstensi (misal "image"), akan mencoba ".png", ".jpeg", ".jpg".
        """
        if base_filename in self.cache:
            return self.cache[base_filename]

        possible_paths = []
        
        # Cek apakah base_filename sudah mengandung ekstensi
        name_part, ext_part = os.path.splitext(base_filename)
        
        if ext_part: # Jika sudah ada ekstensi di base_filename
            possible_paths.append(self.base_path / base_filename)
        else: # Jika tidak ada ekstensi, coba beberapa ekstensi umum
            possible_paths.append(self.base_path / f"{base_filename}.png")
            possible_paths.append(self.base_path / f"{base_filename}.jpeg")
            possible_paths.append(self.base_path / f"{base_filename}.jpg")

        img_path_to_load = None
        for path_option in possible_paths:
            if path_option.exists():
                img_path_to_load = path_option
                break
        
        if img_path_to_load is None:
            logger.error(f"Gagal menemukan image. Nama dasar/file: '{base_filename}'. Path dicoba: {[str(p) for p in possible_paths]}")
            sys.exit(1) # Keluar jika file tidak ditemukan

        try:
            image = pygame.image.load(str(img_path_to_load))
            # Coba convert_alpha(). Jika gagal (misalnya untuk JPG/JPEG), gunakan convert().
            try:
                image = image.convert_alpha()
            except pygame.error:
                image = image.convert()
                logger.info(f"Gambar {img_path_to_load} di-convert (bukan convert_alpha karena mungkin tidak ada alpha channel).")

            self.cache[base_filename] = image # Cache menggunakan nama dasar yang diminta
            logger.info(f"Loaded image: {img_path_to_load} (diminta sebagai '{base_filename}')")
            return image
        except pygame.error as e:
            logger.error(f"Gagal memuat image setelah ditemukan: {img_path_to_load} - {e}")
            sys.exit(1)
