# src/scene/main_menu.py

import pygame
from src.constants import MENU_ITEMS, COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH, SCREEN_HEIGHT # Tambahkan SCREEN_HEIGHT

class MainMenu:
    def __init__(self, screen, game): 
        self.screen   = screen
        self.game = game 
        self.selected = 0
        self.font     = self.game.font_medium # Menggunakan font dari instance Game

        # --- Muat Gambar Latar Belakang ---
        try:
            # Ganti dengan nama file gambar latar belakang Anda -> "background.jpeg"
            background_original = self.game.resources.load_image("background") #
            # Skalakan gambar agar sesuai dengan ukuran layar
            self.background_image = pygame.transform.scale(background_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except SystemExit: 
            print("Peringatan: Gambar latar belakang menu (background.jpeg) tidak ditemukan. Menggunakan warna solid.")
            self.background_image = None 
        except pygame.error as e:
            print(f"Peringatan: Gagal memuat atau menskalakan gambar latar belakang menu: {e}. Menggunakan warna solid.")
            self.background_image = None
        # --- Akhir Muat Gambar Latar Belakang ---

        # Hitung rect per item sekali saja
        self.item_rects = []
        for idx, item in enumerate(MENU_ITEMS):
            surf = self.font.render(item, True, COLOR_WHITE) 
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, 250 + idx * 60)) 
            self.item_rects.append(rect)

    def handle_input(self, event):
        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(MENU_ITEMS)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(MENU_ITEMS)
                return None
            elif event.key == pygame.K_RETURN:
                return MENU_ITEMS[self.selected]

        # Mouse movement → hover effect
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    self.selected = idx

        # Mouse click → selection
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # kiri
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    return MENU_ITEMS[idx]

        return None

    def update(self):
        pass 

    def draw(self):
        # --- Gambar Latar Belakang ---
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            pass # Biarkan game loop utama di game.py yang mengisi layar jika background tidak ada

        # --- Gambar Item Menu ---
        for idx, item in enumerate(MENU_ITEMS):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            surf = self.font.render(item, True, color)
            rect = self.item_rects[idx]
            self.screen.blit(surf, rect)
