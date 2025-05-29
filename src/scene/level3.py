import pygame
from src.constants import COLOR_BROWN, SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.resource_manager import ResourceManager
import math

# --- Kelas untuk Tuas (Lever) ---
# Dipertahankan
class Lever(pygame.Rect):
    def __init__(self, x, y, width, height, up_img, down_img):
        super().__init__(x, y, width, height)
        self.up_img = up_img
        self.down_img = down_img
        self.is_up = True # Status awal tuas (misal: ke atas)
        self.is_interactable = False # Status apakah pemain cukup dekat untuk berinteraksi

    def draw(self, screen):
        # Gambar tuas sesuai statusnya
        if self.is_up:
            screen.blit(self.up_img, self.topleft)
        else:
            screen.blit(self.down_img, self.topleft)

    def toggle(self):
        # Mengubah status tuas
        self.is_up = not self.is_up

# ---------------------------------------------


class Level3:
    def __init__(self, player, resources):
        self.player = player
        self.resources = resources

        # --- Rintangan Statis (Obstacles) ---
        self.obstacles = [
            pygame.Rect(0, 550, 800, 50),   # lantai
        ]

        # --- Aset Gambar ---
        self.block_img = self.resources.load_image("block")
        self.exit_img = self.resources.load_image("signExit")
        self.bridge_img = self.resources.load_image("bridge")

        # Muat gambar tuas
        lever_up_orig = self.resources.load_image("lever_up")
        lever_down_orig = self.resources.load_image("lever_down")

        # Muat aset kunci dan gembok
        key_red_orig = self.resources.load_image("keyRed")
        lock_red_orig = self.resources.load_image("lock_red")


        # Tentukan ukuran untuk tuas (sesuaikan jika perlu)
        lever_width = lever_up_orig.get_width()
        lever_height = lever_down_orig.get_height() # Gunakan gambar down untuk tinggi agar konsisten
        self.lever_up_img = pygame.transform.scale(lever_up_orig, (lever_width, lever_height))
        self.lever_down_img = pygame.transform.scale(lever_down_orig, (lever_width, lever_height))

        # Tentukan ukuran untuk kunci dan gembok (sesuaikan jika perlu)
        key_size = 30 # Ukuran kunci
        lock_size = 50 # Ukuran gembok
        # Skala kunci proporsional
        self.key_red_img = pygame.transform.scale(key_red_orig, (key_size, int(key_size * key_red_orig.get_height() / key_red_orig.get_width())))
        # Skala gembok persegi
        self.lock_red_img = pygame.transform.scale(lock_red_orig, (lock_size, lock_size))


        self.orig_w = self.block_img.get_width()
        self._cache = {}


        # --- Goal (Tanda Exit) ---
        # Mengembalikan definisi exit_rect ke versi asli dari unggahan Anda
        exit_width = self.exit_img.get_width()
        exit_height = self.exit_img.get_height()
        exit_x = SCREEN_WIDTH - exit_width - 20
        exit_y = SCREEN_HEIGHT - 500 - exit_height # Ini adalah posisi dari unggahan Anda
        self.exit_rect = pygame.Rect(exit_x, exit_y, exit_width, exit_height)


        # --- Platform Bridge ---
        self.bridge_platforms_rects = []

        # Platform yang akan digerakkan oleh tuas (Platform Utama yang Bergerak)
        # Mengembalikan definisi movable_platform ke versi asli dari unggahan Anda
        self.movable_platform_start_pos = pygame.Vector2(500, 525) 
        self.movable_platform_end_pos = pygame.Vector2(500, 100) 
        self.movable_platform_speed = 100 

        movable_bridge_width = 100
        movable_bridge_height = self.bridge_img.get_height()
        self.movable_platform_rect = pygame.Rect(
            self.movable_platform_start_pos.x,
            self.movable_platform_start_pos.y,
            movable_bridge_width,
            movable_bridge_height
        )
        self.bridge_platforms_rects.append(self.movable_platform_rect)
        self.obstacles.append(self.movable_platform_rect)

        # Platform bridge kedua (platform statis dekat exit)
        # Mengembalikan definisi platform statis ke versi asli dari unggahan Anda
        bridge_platform_width_static = 200 
        bridge_platform_height_static = self.bridge_img.get_height()
        bridge_platform_x_static = 600 
        bridge_platform_y_static = 100 
        bridge_rect_top_static = pygame.Rect(bridge_platform_x_static, bridge_platform_y_static, bridge_platform_width_static, bridge_platform_height_static)
        self.bridge_platforms_rects.append(bridge_rect_top_static)
        self.obstacles.append(bridge_rect_top_static)
        
        # Platform bridge lainnya (contoh) - Mengembalikan ke versi asli dari unggahan Anda
        bridge_platform_width = 100
        bridge_platform_height = self.bridge_img.get_height()
        
        bridge_platform_x_1 = 100 # Menggunakan nama variabel yang berbeda untuk kejelasan
        bridge_platform_y_1 = 450
        another_bridge_rect1 = pygame.Rect(bridge_platform_x_1, bridge_platform_y_1, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(another_bridge_rect1)
        self.obstacles.append(another_bridge_rect1)
        
        bridge_platform_x_2 = 200
        bridge_platform_y_2 = 350
        another_bridge_rect2 = pygame.Rect(bridge_platform_x_2, bridge_platform_y_2, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(another_bridge_rect2)
        self.obstacles.append(another_bridge_rect2)
        
        bridge_platform_x_3 = 100
        bridge_platform_y_3 = 250
        another_bridge_rect3 = pygame.Rect(bridge_platform_x_3, bridge_platform_y_3, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(another_bridge_rect3)
        self.obstacles.append(another_bridge_rect3)


        # --- Tuas (Lever) ---
        lever_x = 400
        lever_y = SCREEN_HEIGHT - 50 - lever_height # Di atas lantai
        self.lever = Lever(lever_x, lever_y, lever_width, lever_height, self.lever_up_img, self.lever_down_img)
        self._can_interact_lever = True
        self._lever_cooldown_timer = 0

        # --- Gembok (Lock) ---
        lock_width, lock_height = self.lock_red_img.get_size()
        lock_x = self.lever.centerx - (lock_width // 2)
        lock_y = self.lever.bottom - lock_height 
        self.lock_red_rect = pygame.Rect(lock_x, lock_y, lock_width, lock_height)
        self.is_lever_unlocked = False


        # --- Kunci (Key) ---
        key_x = 150 
        key_y = SCREEN_HEIGHT - 450 - self.key_red_img.get_height() 
        self.key_red_rect = pygame.Rect(key_x, key_y, self.key_red_img.get_width(), self.key_red_img.get_height())
        self.player_has_key_red = False 
        self.key_used = False


        # Simpan posisi Y saat ini dari platform yang dapat digerakkan
        self._current_platform_y = self.movable_platform_start_pos.y
        
        # --- DEKORASI ---
        self.decoration_level3 = []
        try:
            # Pastikan file gambar "hill_small.png" dan "hill_smallAlt.png" ada di folder assets/images/
            aset_dekorasi_1 = self.resources.load_image("hill_small") 
            aset_dekorasi_2 = self.resources.load_image("hill_smallAlt")

            # 1. Muat gambar awan asli (yang besar)
            awan_asli = self.resources.load_image("cloud_1") # Ganti "cloud_1" dengan nama file awan Anda

            # 2. Tentukan ukuran baru yang Anda inginkan untuk awan
            lebar_awan_baru = 150 # Sesuaikan lebar ini
            tinggi_awan_baru = 80  # Sesuaikan tinggi ini

            # 3. Buat gambar awan baru dengan ukuran yang sudah diubah
            aset_dekorasi_3_awan_kecil = pygame.transform.scale(awan_asli, (lebar_awan_baru, tinggi_awan_baru))


            decoration_definition_lv3 = [
                (aset_dekorasi_1, (50, SCREEN_HEIGHT - 50 - aset_dekorasi_1.get_height())), 
                (aset_dekorasi_2, (700, SCREEN_HEIGHT - 50 - aset_dekorasi_2.get_height())),
                # 4. Gunakan awan yang sudah dikecilkan untuk dekorasi
                # Ganti (100,50) dengan posisi x,y yang Anda inginkan untuk awan
                (aset_dekorasi_3_awan_kecil, (100, 1)), 
            ]
            
            for img, pos in decoration_definition_lv3:
                self.decoration_level3.append({'image': img, 'position':pos})

        except pygame.error as e:
            print(f"Gagal memuat gambar dekorasi di level 3: {e}")
        except Exception as ex: 
            print(f"Error lain saat memuat dekorasi level 3: {ex}")


    def update(self, dt, player_rect):
        # --- Logika Kunci (Key) ---
        if not self.key_used:
            if not self.player_has_key_red:
                if player_rect.colliderect(self.key_red_rect):
                     self.player_has_key_red = True
            else: 
                offset_x = 10 
                offset_y = -10
                self.key_red_rect.centerx = player_rect.centerx + offset_x
                self.key_red_rect.centery = player_rect.centery + offset_y

                if not self.is_lever_unlocked and self.lock_red_rect is not None:
                     if self.key_red_rect.colliderect(self.lock_red_rect):
                          self.is_lever_unlocked = True 
                          self.key_used = True


        # --- Logika Tuas (Lever) ---
        if self.is_lever_unlocked:
            interaction_area = self.lever.inflate(10, 10)
            if player_rect.colliderect(interaction_area):
                self.lever.is_interactable = True
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e] and self._can_interact_lever:
                     self.lever.toggle()
                     self._can_interact_lever = False
                     self._lever_cooldown_timer = 0.5
            else:
                self.lever.is_interactable = False
        else:
            self.lever.is_interactable = False

        if not self._can_interact_lever:
             self._lever_cooldown_timer -= dt
             if self._lever_cooldown_timer <= 0:
                  self._can_interact_lever = True

        # --- Logika Pergerakan Platform Utama (Dikontrol Tuas) ---
        target_y = self.movable_platform_start_pos.y if self.lever.is_up else self.movable_platform_end_pos.y
        distance_to_target = target_y - self._current_platform_y
        move_amount = self.movable_platform_speed * dt
        old_movable_platform_y = self.movable_platform_rect.y

        if distance_to_target > 0:
             self._current_platform_y += min(move_amount, distance_to_target)
        elif distance_to_target < 0:
             self._current_platform_y += max(-move_amount, distance_to_target)

        self.movable_platform_rect.y = int(self._current_platform_y)
        actual_platform_move_y = self.movable_platform_rect.y - old_movable_platform_y

        if player_rect.colliderect(self.movable_platform_rect):
             if self.player.vel.y >= 0 and \
                abs(player_rect.bottom - self.movable_platform_rect.top) < max(5, abs(actual_platform_move_y) + 2) : 
                  player_rect.y += actual_platform_move_y 
                  player_rect.bottom = self.movable_platform_rect.top 
                  self.player.on_ground = True 
                  self.player.vel.y = 0 

        # --- Cek Selesai Level ---
        if player_rect.colliderect(self.exit_rect):
            self.completed = True


    def draw(self, screen):
        # --- GAMBAR DEKORASI TERLEBIH DAHULU ---
        for decor in self.decoration_level3:
            screen.blit(decor['image'],decor['position'])

        # Gambar rintangan (lantai dan platform statis lainnya)
        for rect in self.obstacles:
             is_bridge_rect = rect in self.bridge_platforms_rects
             if not is_bridge_rect: 
                 h = rect.height
                 if h not in self._cache:
                     scaled = pygame.transform.scale(self.block_img, (self.orig_w, h))
                     self._cache[h] = scaled
                 tile_surf = self._cache[h]
                 count = math.ceil(rect.width / self.orig_w)
                 for i in range(count):
                     x_pos = rect.x + i * self.orig_w
                     screen.blit(tile_surf, (x_pos, rect.y))
        
        # Gambar Tanda Exit
        screen.blit(self.exit_img, self.exit_rect.topleft)

        # --- Gambar Platform Bridge ---
        w_bridge, h_bridge = self.bridge_img.get_size()
        for rect in self.bridge_platforms_rects:
             if rect in self.obstacles: 
                  for x_coord in range(rect.left, rect.right, w_bridge): 
                       current_tile_width = min(w_bridge, rect.right - x_coord)
                       screen.blit(self.bridge_img, (x_coord, rect.top), (0, 0, current_tile_width, h_bridge))


        # Gambar Tuas
        self.lever.draw(screen)

        # --- Gambar Gembok (Lock) ---
        if not self.is_lever_unlocked and self.lock_red_rect is not None:
             screen.blit(self.lock_red_img, self.lock_red_rect.topleft)

        # --- Gambar Kunci (Key) ---
        if not self.player_has_key_red and not self.key_used:
             screen.blit(self.key_red_img, self.key_red_rect.topleft)
        elif self.player_has_key_red and not self.key_used:
             screen.blit(self.key_red_img, self.key_red_rect.topleft)

        # Opsional: Gambar indikator interaksi tuas
        if self.lever.is_interactable:
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Press E", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lever.centerx, self.lever.top - 20))
             screen.blit(text_surf, text_rect)

        # Opsional: Gambar indikator untuk mengambil kunci
        if not self.player_has_key_red and not self.key_used and self.player.rect.colliderect(self.key_red_rect.inflate(10,10)):
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Touch to take key", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.key_red_rect.centerx, self.key_red_rect.top - 20))
             screen.blit(text_surf, text_rect)

        # Opsional: Gambar indikator untuk membuka gembok
        if self.player_has_key_red and not self.is_lever_unlocked and self.lock_red_rect is not None and self.player.rect.colliderect(self.lock_red_rect.inflate(10,10)):
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Touch lock with key", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lock_red_rect.centerx, self.lock_red_rect.top - 20))
             screen.blit(text_surf, text_rect)
