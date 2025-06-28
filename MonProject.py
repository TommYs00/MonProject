import pygame, sys

import settings
from const import *
from ui import UI
from map import MapManager
from player import Player
from monster import Ally


class MonProject:
    _instance = None

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._initialized = True
        pygame.init()
        pygame.display.set_caption("MonProject")
        self.display = pygame.display.set_mode(settings.RESOLUTION)
        self.clock = pygame.time.Clock()
        self.status = {RUNNING: True,
                       PAUSED: False}

        self.ui = UI(self)
        self.game_map = MapManager(self.display)

        self.player = Player(self.display, self.game_map.collider_tiles, Ally())

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def update_display(self):
        self.display.fill((0, 0, 0))
        self.game_map.draw()
        self.player.draw()
        self.ui.draw()

        pygame.display.flip()

    def check_key_events(self):
        self.quit() if pygame.event.get(pygame.QUIT) else None

        pressed = pygame.key.get_pressed()
        just_pressed = pygame.key.get_just_pressed()
        dt = self.clock.tick() / 1000

        self.ui.check_keys(just_pressed)

        if not self.status[PAUSED]:
            self.player.move(pressed, just_pressed, dt)
            self._check_collision()

        if self.game_map.battle_encounter <= 0:
            self.game_map.new_encounter()
            self.ui.initialize_battle()

    def _check_collision(self):
       if pygame.sprite.spritecollideany(self.player, self.game_map.bush_tiles):
           self.game_map.count_down(self.player.movement)

    def quit(self):
        self.status[RUNNING] = False
        pygame.quit()
        sys.exit()

    def run(self):
        while self.status[RUNNING]:
            self.update_display()
            self.check_key_events()


if __name__ == "__main__":
    game = MonProject()
    pygame.init()
    game.run()
