import pygame
import settings
from pytmx.util_pygame import load_pygame
import random

class MapManager:
    def __init__(self, display):
        self.display = display

        # tmx data
        self._tmx_data = load_pygame("images/tilesets/game_map.tmx")
        self._ground = self._tmx_data.get_layer_by_name("Ground")
        self._bush = self._tmx_data.get_layer_by_name("Bushes")
        self._colliders = self._tmx_data.get_layer_by_name("Colliders")

        # sprite groups
        self.bush_tiles = pygame.sprite.Group()
        self.collider_tiles = pygame.sprite.Group()

        # creating sprite objects
        for x, y, surf in self._bush.tiles():
            BushTile(x, y, surf, self.bush_tiles)
        for x, y, surf in self._colliders.tiles():
            ColliderTile(x, y, surf, self.collider_tiles)

        self.battle_encounter = None
        self.new_encounter()


    def draw(self):
        for x, y, surf in self._ground.tiles():
            surf = pygame.transform.scale_by(surf, settings.tile_size // surf.width)
            self.display.blit(surf, (x * settings.tile_size, y * settings.tile_size))

        self.bush_tiles.draw(self.display)
        self.collider_tiles.draw(self.display)

    def new_encounter(self):
        self.battle_encounter = random.randint(500, 3000)

    def count_down(self, movement):
        self.battle_encounter -= (abs(movement.x) + abs(movement.y))

class BushTile(pygame.sprite.Sprite):
    def __init__(self, x, y, img, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale_by(img, settings.tile_size // img.width).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = x * settings.tile_size, y * settings.tile_size


class ColliderTile(pygame.sprite.Sprite):
    def __init__(self, x, y, img, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale_by(img, settings.tile_size // img.width).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = x * settings.tile_size, y * settings.tile_size
