# src/utils/resource_manager.py
from pathlib import Path
import pygame
import sys
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, base_image_path: Path, base_sound_path: Path): # Tambahkan base_sound_path
        self.base_image_path = base_image_path
        self.base_sound_path = base_sound_path  # Path dasar untuk suara
        self.image_cache = {}  # Ganti nama cache menjadi image_cache
        self.sound_cache = {}  # Cache untuk suara

    def load_image(self, base_filename: str) -> pygame.Surface:
        if base_filename in self.image_cache: # Gunakan image_cache
            return self.image_cache[base_filename]

        possible_paths = []
        name_part, ext_part = os.path.splitext(base_filename)
        
        if ext_part:
            possible_paths.append(self.base_image_path / base_filename)
        else:
            possible_paths.append(self.base_image_path / f"{base_filename}.png")
            possible_paths.append(self.base_image_path / f"{base_filename}.jpeg")
            possible_paths.append(self.base_image_path / f"{base_filename}.jpg")
        
        img_path_to_load = None
        for path_option in possible_paths:
            if path_option.exists():
                img_path_to_load = path_option
                break
        
        if img_path_to_load is None:
            logger.error(f"Gagal menemukan image. Nama dasar/file: '{base_filename}'. Path dicoba: {[str(p) for p in possible_paths]}")
            sys.exit(1)

        try:
            image = pygame.image.load(str(img_path_to_load))
            try:
                image = image.convert_alpha()
            except pygame.error:
                image = image.convert()
            self.image_cache[base_filename] = image # Gunakan image_cache
            logger.info(f"Loaded image: {img_path_to_load} (diminta sebagai '{base_filename}')")
            return image
        except pygame.error as e:
            logger.error(f"Gagal memuat image setelah ditemukan: {img_path_to_load} - {e}")
            sys.exit(1)

    # --- METODE BARU UNTUK MEMUAT SUARA ---
    def load_sound(self, base_filename: str) -> pygame.mixer.Sound:
        if base_filename in self.sound_cache:
            return self.sound_cache[base_filename]

        possible_paths = []
        name_part, ext_part = os.path.splitext(base_filename)

        if ext_part: # Jika nama file sudah menyertakan ekstensi
            possible_paths.append(self.base_sound_path / base_filename)
        else: # Coba ekstensi umum jika tidak ada
            possible_paths.append(self.base_sound_path / f"{base_filename}.wav")
            possible_paths.append(self.base_sound_path / f"{base_filename}.ogg")
            possible_paths.append(self.base_sound_path / f"{base_filename}.mp3")
        
        sound_path_to_load = None
        for path_option in possible_paths:
            if path_option.exists():
                sound_path_to_load = path_option
                break
        
        if sound_path_to_load is None:
            logger.error(f"Gagal menemukan sound: '{base_filename}'. Path dicoba: {[str(p) for p in possible_paths]}")
            # Sebaiknya jangan sys.exit(1) di sini, mungkin return None atau dummy sound
            # Untuk sekarang, kita biarkan error agar jelas jika file tidak ada
            raise FileNotFoundError(f"Sound file '{base_filename}' not found.")

        try:
            sound = pygame.mixer.Sound(str(sound_path_to_load))
            self.sound_cache[base_filename] = sound
            logger.info(f"Loaded sound: {sound_path_to_load} (diminta sebagai '{base_filename}')")
            return sound
        except pygame.error as e:
            logger.error(f"Gagal memuat sound setelah ditemukan: {sound_path_to_load} - {e}")
            raise # Lemparkan kembali errornya