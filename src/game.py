import pygame
from pathlib import Path
from src.utils.resource_manager import ResourceManager
from src.characters.player import Player
from src.scene.main_menu   import MainMenu
from src.scene.level_select import LevelSelect
from src.scene.level1      import Level1
from src.scene.level2      import Level2
from src.scene.level3      import Level3
from src.constants import *
import os 

class Game:
    STATE_MENU        = 0
    STATE_LEVEL_SELECT= 1
    STATE_PLAYING     = 2
    STATE_OPTION      = 3
    STATE_GAMEOVER    = 4
    STATE_LEVEL_CLEAR = 5

    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.state  = Game.STATE_MENU

        # Resource Manager
        base_dir = Path(__file__).resolve().parent.parent 
        img_dir  = base_dir / IMAGES_DIR 
        self.resources = ResourceManager(img_dir)

        # --- Pengaturan Font ---
        font_folder = base_dir / "assets" / "fonts" 
        custom_font_filename = "arial.ttf" 
        
        font_path = os.path.join(font_folder, custom_font_filename)
        print(f"Mencoba memuat font dari: {font_path}")

        try:
            if os.path.exists(font_path):
                self.font_large = pygame.font.Font(font_path, 72)
                self.font_medium = pygame.font.Font(font_path, 48) 
                self.font_small = pygame.font.Font(font_path, 36)
                print(f"Berhasil memuat font kustom: {custom_font_filename}")
            else:
                print(f"File font kustom '{custom_font_filename}' tidak ditemukan di '{font_folder}'. Menggunakan SysFont default.")
                self.font_large = pygame.font.SysFont(None, 72) 
                self.font_medium = pygame.font.SysFont(None, 48) 
                self.font_small = pygame.font.SysFont(None, 36) 
        except pygame.error as e:
            print(f"Gagal memuat font '{custom_font_filename}'. Menggunakan font default Pygame. Error: {e}")
            self.font_large = pygame.font.SysFont(None, 72)
            self.font_medium = pygame.font.SysFont(None, 48) 
            self.font_small = pygame.font.SysFont(None, 36)
        # --- Akhir Pengaturan Font ---

        # --- Muat Gambar Latar Belakang Bersama ---
        try:
            # Menggunakan nama dasar "background", ResourceManager akan mencari .jpeg atau .png
            background_original = self.resources.load_image("background") 
            self.shared_background_image = pygame.transform.scale(background_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Berhasil memuat dan menskalakan shared_background_image.")
        except SystemExit: 
            print("Peringatan: Gambar latar belakang bersama (background) tidak ditemukan. Beberapa layar mungkin tidak memiliki background kustom.")
            self.shared_background_image = None 
        except pygame.error as e:
            print(f"Peringatan: Gagal memuat atau menskalakan gambar latar belakang bersama: {e}.")
            self.shared_background_image = None
        # --- Akhir Muat Gambar Latar Belakang Bersama ---

        # Scenes dan level (SETELAH font dan background bersama diinisialisasi)
        self.menu        = MainMenu(self.screen, self) 
        self.level_sel   = LevelSelect(self.screen, self) 
        self.level       = None
        self.player      = None
        
        self.level_clear_return_text = "Kembali ke Pemilihan Level"
        self.level_clear_return_surf = self.font_medium.render(self.level_clear_return_text, True, COLOR_WHITE)
        self.level_clear_return_rect = self.level_clear_return_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.level_clear_return_highlight_surf = self.font_medium.render(self.level_clear_return_text, True, COLOR_HIGHLIGHT)


    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if self.state == Game.STATE_MENU:
                choice = self.menu.handle_input(event)
                if choice == "Start Game":
                    self.state = Game.STATE_LEVEL_SELECT
                elif choice == "Options":
                    print("Options selected - Implement STATE_OPTION or logic")
                    self.state = Game.STATE_OPTION 
                elif choice == "Exit":
                    pygame.quit(); exit()

            elif self.state == Game.STATE_LEVEL_SELECT:
                choice = self.level_sel.handle_input(event)
                if choice in LEVELS:
                    bob_img_base_name = "bob" 
                    try:
                        bob = self.resources.load_image(bob_img_base_name) 
                    except SystemExit: 
                        print(f"Gagal memuat gambar pemain: '{bob_img_base_name}'. Game akan keluar.")
                        pygame.quit()
                        exit()
                        
                    self.player = Player((0, 0), bob) 

                    if choice == "Level 1":
                        self.level  = Level1(self.player, self.resources)
                    elif choice == "Level 2": 
                        self.level = Level2(self.player, self.resources) 
                    elif choice == "Level 3": 
                        self.level = Level3(self.player, self.resources) 

                    if hasattr(self.level, 'player_start_pos'):
                         self.player.rect.topleft = self.level.player_start_pos
                    else:
                         self.player.rect.topleft = (100, SCREEN_HEIGHT - 100) 

                    self.state  = Game.STATE_PLAYING
                elif choice == "Back":
                    self.state = Game.STATE_MENU

            elif self.state == Game.STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p: 
                         self.state = Game.STATE_OPTION 
                    
            elif self.state == Game.STATE_OPTION:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_MENU 

            elif self.state == Game.STATE_GAMEOVER:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_MENU 

            elif self.state == Game.STATE_LEVEL_CLEAR:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_LEVEL_SELECT 
                 elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                      if self.level_clear_return_rect.collidepoint(event.pos):
                           self.state = Game.STATE_LEVEL_SELECT


    def _update(self, dt):
        if self.state == Game.STATE_PLAYING:
            if self.player is not None and self.level is not None:
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
                
                obstacles_for_player = []
                if hasattr(self.level, 'obstacles'):
                    obstacles_for_player = self.level.obstacles
                self.player.update(dt, obstacles_for_player)

                self.level.update(dt, self.player.rect)

                if getattr(self.level, 'completed', False):
                     self.state = Game.STATE_LEVEL_CLEAR
                     print("Level Clear!") 

                elif self.player.rect.top > SCREEN_HEIGHT + 50: 
                    self.state = Game.STATE_GAMEOVER
                    print("Game Over!") 


    def _draw(self):
        # Gambar latar belakang bersama jika tersedia, kecuali untuk STATE_PLAYING dan STATE_MENU (karena menu punya background sendiri)
        if self.state not in [Game.STATE_PLAYING, Game.STATE_MENU] and self.shared_background_image:
            self.screen.blit(self.shared_background_image, (0,0))
        elif self.state == Game.STATE_LEVEL_SELECT: # Jika tidak ada shared_background, isi dengan warna
             self.screen.fill(COLOR_BROWN) # Fallback color untuk Level Select
        # Untuk state lain, warna fallback diatur di bawah jika shared_background_image tidak ada

        if self.state == Game.STATE_MENU:
            # MainMenu.draw() akan menangani backgroundnya sendiri
            self.menu.draw()
        elif self.state == Game.STATE_LEVEL_SELECT:
            # Background sudah digambar di atas jika shared_background_image ada
            # Jika tidak, COLOR_BROWN sudah di-fill
            self.level_sel.draw()
        elif self.state == Game.STATE_PLAYING:
            self.screen.fill(COLOR_SKY) 
            if self.level is not None and self.player is not None:
                 self.level.draw(self.screen) 
                 self.player.draw(self.screen) 
            else:
                 self.screen.fill((0,0,0)) 


        elif self.state == Game.STATE_OPTION:
            if not self.shared_background_image: # Fallback jika background bersama tidak ada
                self.screen.fill((50, 50, 50))  
            surf_title = self.font_large.render("Options", True, COLOR_WHITE)
            rect_title = surf_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(surf_title, rect_title)
            
            surf_inst = self.font_medium.render("Press ESC to return", True, COLOR_WHITE)
            rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(surf_inst, rect_inst)


        elif self.state == Game.STATE_GAMEOVER:
            if not self.shared_background_image: # Fallback jika background bersama tidak ada
                self.screen.fill((0, 0, 0)) 
            surf = self.font_large.render("Game Over", True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(surf, rect)
            surf_inst = self.font_medium.render("Press ESC to return to Menu", True, COLOR_WHITE)
            rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(surf_inst, rect_inst)

        elif self.state == Game.STATE_LEVEL_CLEAR:
            if not self.shared_background_image: # Fallback jika background bersama tidak ada
                self.screen.fill(COLOR_SKY) 
            
            surf_clear = self.font_large.render("Level Clear!", True, COLOR_WHITE)
            rect_clear = surf_clear.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(surf_clear, rect_clear)

            mouse_pos = pygame.mouse.get_pos()
            if self.level_clear_return_rect.collidepoint(mouse_pos):
                self.screen.blit(self.level_clear_return_highlight_surf, self.level_clear_return_rect)
            else:
                self.screen.blit(self.level_clear_return_surf, self.level_clear_return_rect)
            
            esc_inst_surf = self.font_small.render("(Atau tekan ESC)", True, COLOR_WHITE)
            esc_inst_rect = esc_inst_surf.get_rect(center=(SCREEN_WIDTH//2, self.level_clear_return_rect.bottom + 20))
            self.screen.blit(esc_inst_surf, esc_inst_rect)

        pygame.display.flip()
