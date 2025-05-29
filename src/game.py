import pygame
from pathlib import Path
from src.utils.resource_manager import ResourceManager
from src.characters.player import Player
from src.scene.main_menu   import MainMenu
from src.scene.level_select import LevelSelect
from src.scene.level1      import Level1
from src.scene.level2      import Level2
from src.scene.level3      import Level3
from src.constants import * # Ini akan mengimpor SOUNDS_DIR juga
import os 
import logging # <-- MODIFIKASI: Tambahkan logging

logger = logging.getLogger(__name__) # <-- MODIFIKASI: Setup logger untuk game.py

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
        sound_dir = base_dir / SOUNDS_DIR # <-- MODIFIKASI: Path untuk suara
        self.resources = ResourceManager(img_dir, sound_dir) # <-- MODIFIKASI: Berikan sound_dir

        # --- Pengaturan Font (kode font Anda yang sudah ada) ---
        font_folder = base_dir / "assets" / "fonts" 
        custom_font_filename = "arial.ttf" 
        font_path = os.path.join(font_folder, custom_font_filename)
        # ... (sisa kode pemuatan font Anda) ...
        try:
            if os.path.exists(font_path):
                self.font_large = pygame.font.Font(font_path, 72)
                self.font_medium = pygame.font.Font(font_path, 48) 
                self.font_small = pygame.font.Font(font_path, 36)
                # print(f"Berhasil memuat font kustom: {custom_font_filename}") # Komentari print jika tidak perlu
            else:
                # print(f"File font kustom '{custom_font_filename}' tidak ditemukan di '{font_folder}'. Menggunakan SysFont default.")
                self.font_large = pygame.font.SysFont(None, 72) 
                self.font_medium = pygame.font.SysFont(None, 48) 
                self.font_small = pygame.font.SysFont(None, 36) 
        except pygame.error as e:
            # print(f"Gagal memuat font '{custom_font_filename}'. Menggunakan font default Pygame. Error: {e}")
            self.font_large = pygame.font.SysFont(None, 72)
            self.font_medium = pygame.font.SysFont(None, 48) 
            self.font_small = pygame.font.SysFont(None, 36)
        # --- Akhir Pengaturan Font ---

        # --- Muat Gambar Latar Belakang Bersama (kode Anda yang sudah ada) ---
        try:
            background_original = self.resources.load_image("background") 
            self.shared_background_image = pygame.transform.scale(background_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
            # print("Berhasil memuat dan menskalakan shared_background_image.")
        except (FileNotFoundError, pygame.error) as e: # MODIFIKASI: Tangkap FileNotFoundError juga
            print(f"Peringatan: Gambar latar belakang bersama (background) tidak ditemukan atau gagal dimuat: {e}")
            self.shared_background_image = None 
        # --- Akhir Muat Gambar Latar Belakang Bersama ---

        # <-- MODIFIKASI: Muat Sound Effects (SFX) -->
        try:
            self.sfx_jump = self.resources.load_sound("jump")
            self.sfx_key_pickup = self.resources.load_sound("key_pickup")
            self.sfx_lever_toggle = self.resources.load_sound("lever")
            self.sfx_lock_open = self.resources.load_sound("lock_open")
            self.sfx_game_over = self.resources.load_sound("game_over")
            self.sfx_game_clear = self.resources.load_sound("game_clear") # atau nama file yang sesuai
        except FileNotFoundError as e:
            logger.warning(f"Gagal memuat salah satu SFX utama: {e}. Beberapa suara mungkin tidak berfungsi.")
            # Inisialisasi sebagai None agar bisa dicek sebelum dimainkan
            self.sfx_jump = self.sfx_key_pickup = self.sfx_lever_toggle = \
            self.sfx_lock_open = self.sfx_game_over = self.sfx_game_clear = None
        except pygame.error as e: # Tangkap juga error pygame jika terjadi saat load sound
            logger.error(f"Pygame error saat memuat SFX: {e}")


        # Scenes dan level
        self.menu        = MainMenu(self.screen, self) 
        self.level_sel   = LevelSelect(self.screen, self) 
        self.level       = None
        self.player      = None
        
        # ... (kode level_clear_return Anda yang sudah ada) ...
        self.level_clear_return_text = "Kembali ke Pemilihan Level"
        self.level_clear_return_surf = self.font_medium.render(self.level_clear_return_text, True, COLOR_WHITE)
        self.level_clear_return_rect = self.level_clear_return_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.level_clear_return_highlight_surf = self.font_medium.render(self.level_clear_return_text, True, COLOR_HIGHLIGHT)

        # <-- MODIFIKASI: Path dan logika untuk Background Music (BGM) -->
        self.path_bgm_main_menu = None
        self.path_bgm_game_play = None
        try: # Pastikan base_sound_path ada sebelum membuat path BGM
            if self.resources.base_sound_path:
                 # Ganti ekstensi .mp3 dengan ekstensi file Anda jika berbeda (misal .ogg)
                self.path_bgm_main_menu = os.path.join(self.resources.base_sound_path, "main_menu_bgm.mp3")
                self.path_bgm_game_play = os.path.join(self.resources.base_sound_path, "game_play_bgm.mp3")
                # Anda bisa menambahkan path untuk "bgm.mp3" jika itu BGM umum lainnya
        except Exception as e:
            logger.error(f"Error saat menyiapkan path BGM: {e}")

        self.current_bgm_path = None
        if self.path_bgm_main_menu:
            self._play_music(self.path_bgm_main_menu) # Mulai dengan BGM menu utama


    # <-- MODIFIKASI: Metode untuk memainkan BGM -->
    def _play_music(self, music_path, loops=-1):
        if not music_path or not os.path.exists(music_path):
            logger.warning(f"Path BGM tidak valid atau file tidak ditemukan: {music_path}")
            return

        if self.current_bgm_path == music_path and pygame.mixer.music.get_busy():
            return # Musik yang sama sudah berputar

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops) # loops=-1 untuk mengulang terus menerus
            self.current_bgm_path = music_path
            logger.info(f"Playing BGM: {music_path}")
        except pygame.error as e:
            logger.error(f"Tidak dapat memuat atau memainkan BGM: {music_path} - {e}")
            self.current_bgm_path = None

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
                if self.path_bgm_main_menu: self._play_music(self.path_bgm_main_menu) # MODIFIKASI: Putar BGM Menu
                choice = self.menu.handle_input(event)
                if choice == "Start Game":
                    self.state = Game.STATE_LEVEL_SELECT
                elif choice == "Options":
                    # print("Options selected - Implement STATE_OPTION or logic") # Komentari jika tidak perlu
                    self.state = Game.STATE_OPTION 
                elif choice == "Exit":
                    pygame.quit(); exit()

            elif self.state == Game.STATE_LEVEL_SELECT:
                if self.path_bgm_main_menu: self._play_music(self.path_bgm_main_menu) # MODIFIKASI: BGM untuk level select (bisa sama dengan menu)
                choice = self.level_sel.handle_input(event)
                if choice in LEVELS:
                    bob_img_base_name = "bob" 
                    try:
                        bob = self.resources.load_image(bob_img_base_name) 
                    except (FileNotFoundError, pygame.error) as e: # MODIFIKASI: Tangkap error
                        print(f"Gagal memuat gambar pemain: '{bob_img_base_name}'. Error: {e}. Game akan keluar.")
                        pygame.quit()
                        exit()
                        
                    # MODIFIKASI: Berikan sfx_jump ke Player
                    self.player = Player((0, 0), bob, jump_sound=self.sfx_jump) 

                    if choice == "Level 1":
                        # MODIFIKASI: Berikan sfx_lever_toggle ke level
                        self.level  = Level1(self.player, self.resources, sfx_lever=self.sfx_lever_toggle)
                    elif choice == "Level 2": 
                        self.level = Level2(self.player, self.resources, sfx_lever=self.sfx_lever_toggle) 
                    elif choice == "Level 3": 
                        self.level = Level3(self.player, self.resources) 
                        # MODIFIKASI: Berikan SFX yang relevan ke Level3 jika diperlukan
                        # Level3 saat ini tidak memiliki parameter sfx_lever di __init__-nya.
                        # Anda perlu menambahkannya jika ingin menggunakan pola yang sama.
                        # Untuk key_pickup dan lock_open, bisa dimuat di Level3.__init__
                        self.level = Level3(self.player, self.resources) 
                        # Jika Anda ingin Level3 menangani suara kunci & gembok sendiri:
                        # Di Level3.__init__, tambahkan:
                        # try:
                        #     self.sfx_key_pickup = self.resources.load_sound("key_pickup")
                        #     self.sfx_lock_open = self.resources.load_sound("lock_open")
                        # except FileNotFoundError: self.sfx_key_pickup = self.sfx_lock_open = None
                        # Lalu mainkan di Level3.update()

                    if hasattr(self.level, 'player_start_pos'):
                         self.player.rect.topleft = self.level.player_start_pos
                    else:
                         self.player.rect.topleft = (100, SCREEN_HEIGHT - 100) 

                    self.state  = Game.STATE_PLAYING
                    if self.path_bgm_game_play: self._play_music(self.path_bgm_game_play) # MODIFIKASI: Putar BGM Game
                elif choice == "Back":
                    self.state = Game.STATE_MENU
            
            # ... (sisa _handle_events Anda) ...
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
                    pygame.mixer.music.stop() # MODIFIKASI: Hentikan BGM
                    if self.sfx_game_clear: self.sfx_game_clear.play() # MODIFIKASI: Mainkan SFX
                    # print("Level Clear!") 

                elif self.player.rect.top > SCREEN_HEIGHT + 50: # MODIFIKASI: Cek jika pemain jatuh (contoh kondisi game over)
                    self.state = Game.STATE_GAMEOVER
                    pygame.mixer.music.stop() # MODIFIKASI: Hentikan BGM
                    if self.sfx_game_over: self.sfx_game_over.play() # MODIFIKASI: Mainkan SFX
                    # print("Game Over!") 
        # ... (sisa _update Anda)

    # ... (sisa kode _draw Anda, tidak ada perubahan signifikan untuk suara di sini) ...
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