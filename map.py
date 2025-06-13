import pygame
import settings

class MapManager:
    def __init__(self, game):
        self.game = game
        self.tile_map = settings.map_0
        self.tile_type = settings.tile_type
        self.size = settings.tile_size
        self.colliders = pygame.sprite.Group()
        self.rect = pygame.rect.FRect(0, 0, self.size, self.size)

    def draw(self):
        for r, row in enumerate(self.tile_map):
            for c, col in enumerate(row):
                self.rect.top = r * 64 - 16
                self.rect.left = c * 64
                self.game.display.fill(self.tile_type[col], self.rect)
