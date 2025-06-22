import pygame, sys
from player import Player
from ui import MenuUI, GameMenuUI, BattleMenuUI
from monster import Enemy, Ally
from map import MapManager
from const import *
import settings

class MonProject:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("MonProject")
        self.display = pygame.display.set_mode(settings.RESOLUTION)
        self.clock = pygame.time.Clock()
        self.status = {RUNNING: True,
                       PAUSED: False}

        self.esc_screen = GameMenuUI(self, GAME_MENU)
        self.battle_screen = BattleMenuUI(self, BATTLE_MENU)
        self.game_map = MapManager(self.display)

        self.player = Player(self.display, self.game_map.collider_tiles, Ally())

    def update_display(self):
        self.display.fill((0, 0, 0))
        self.game_map.draw()
        self.player.draw()

        if MenuUI.status[BATTLE_MENU]:
            self.battle_screen.draw()
        if MenuUI.status[GAME_MENU]:
            self.esc_screen.draw()

        pygame.display.flip()

    def check_key_events(self):
        pressed = pygame.key.get_pressed()
        just_pressed = pygame.key.get_just_pressed()
        dt = self.clock.tick() / 1000

        self.quit() if pygame.event.get(pygame.QUIT) else None

        if just_pressed[pygame.K_ESCAPE]:
            if self.status[PAUSED] and MenuUI.status[GAME_MENU]:
                self.esc_screen.toggle()
            elif not self.status[PAUSED]:
                self.esc_screen.toggle()

        if not self.status[PAUSED]:
            self.player.move(pressed, dt)
            self._check_collision()

        if self.game_map.battle_encounter <= 0:
            self.game_map.new_encounter()
            self.battle_screen.initialize(self.player.ally, Enemy())
            self.battle_screen.toggle()

        if MenuUI.status[GAME_MENU]:
            self.esc_screen.check_action(just_pressed)
        elif MenuUI.status[BATTLE_MENU]:
            self.battle_screen.check_action(just_pressed)

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
