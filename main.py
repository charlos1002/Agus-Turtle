import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, IMAGES_DIR # Tambahkan IMAGES_DIR
from src.game import Game
import os # Tambahkan import os untuk menggabungkan path

def main():
    pygame.init()
    pygame.mixer.init()

    #logo
    try:
        # Bentuk path yang benar ke ikon Anda
        icon_path = os.path.join(IMAGES_DIR, "kurakura.png")
        game_icon = pygame.image.load(icon_path)
        pygame.display.set_icon(game_icon)
    except pygame.error as e:
        print(f"Tidak dapat memuat ikon: {icon_path} - {e}")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Agus Turtle") # Caption tetap bisa ada
    game = Game(screen)
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()