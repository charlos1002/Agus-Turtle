import pygame
from src.constants import GRAVITY, PLAYER_SPEED, JUMP_STRENGTH

class Player(pygame.sprite.Sprite):
    # MODIFIKASI: Tambahkan jump_sound ke __init__
    def __init__(self, pos, image: pygame.Surface, jump_sound: pygame.mixer.Sound = None):
        super().__init__()
        self.image = image
        self.rect  = self.image.get_rect(topleft=pos)

        self.vel = pygame.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump_strength = JUMP_STRENGTH
        self.on_ground = False
        self.jump_sound = jump_sound # <-- MODIFIKASI: Simpan suara lompat

    def handle_input(self, keys):
        self.vel.x = 0
        if keys[pygame.K_a]:
            self.vel.x = -self.speed
        if keys[pygame.K_d]:
            self.vel.x = self.speed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = self.jump_strength
            self.on_ground = False
            if self.jump_sound: # <-- MODIFIKASI: Mainkan suara lompat
                self.jump_sound.play()

    def update(self, dt, obstacles):
        # ... (sisa kode update Anda) ...
        self.vel.y += self.gravity * dt

        self.rect.x += int(self.vel.x * dt)
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if self.vel.x > 0:
                    self.rect.right = obs.left
                elif self.vel.x < 0:
                    self.rect.left = obs.right

        self.rect.y += int(self.vel.y * dt)
        self.on_ground = False # Set on_ground ke False sebelum cek collision Y
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if self.vel.y > 0: # Jatuh ke atas obstacle
                    self.rect.bottom = obs.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0: # Membentur bagian bawah obstacle dari bawah
                    self.rect.top = obs.bottom
                    self.vel.y = 0 # Hentikan gerakan ke atas


    def draw(self, screen):
        screen.blit(self.image, self.rect)