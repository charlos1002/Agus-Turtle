# src/scene/level_select.py

import pygame
from src.constants import LEVELS, COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH

class LevelSelect:
    # Modifikasi __init__ untuk menerima 'game' sebagai argumen ketiga
    def __init__(self, screen, game): # Tambahkan 'game' di sini
        self.screen   = screen
        self.game = game # Simpan instance game
        self.selected = 0
        # Gunakan font dari instance game
        # Anda bisa memilih font_medium atau font_small, sesuaikan ukurannya di game.py jika perlu
        # Misalnya, jika item level select lebih kecil, font_small mungkin lebih cocok.
        # Untuk contoh ini, kita gunakan font_medium, asumsikan ukurannya (misal 48 atau 42) cocok.
        # Jika Anda ingin ukuran font yang berbeda, pastikan itu diinisialisasi di game.py (misal, self.game.font_level_select)
        self.font     = self.game.font_medium # Atau self.game.font_small jika lebih sesuai

        # Precompute rect untuk setiap level
        self.item_rects = []
        for idx, lvl in enumerate(LEVELS):
            surf = self.font.render(lvl, True, COLOR_WHITE) # Font sudah dari game instance
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, 250 + idx * 60))
            self.item_rects.append(rect)

    def handle_input(self, event):
        # Keyboard navigasi
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(LEVELS)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(LEVELS)
                return None
            elif event.key == pygame.K_RETURN:
                return LEVELS[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "Back" # Untuk kembali ke menu utama

        # Mouse hover
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    self.selected = idx

        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    return LEVELS[idx]

        return None

    def update(self):
        pass # Tidak ada logika update spesifik untuk level select saat ini

    def draw(self):
        # self.screen.fill((0, 0, 0)) # Pengisian layar biasanya dilakukan di game loop utama
        for idx, lvl in enumerate(LEVELS):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            surf = self.font.render(lvl, True, color)
            rect = self.item_rects[idx]
            self.screen.blit(surf, rect)
