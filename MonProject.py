import pygame, sys
from player import Player
from ui import UI, GameUI, BattleUI
from creature import Enemy, Ally
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

        self.esc_screen = GameUI(self, GAME_MENU)
        self.battle_screen = BattleUI(self, BATTLE_MENU)
        self.game_map = MapManager(self)

        self.player = Player(Ally)

    def update_display(self):
        self.display.fill((0, 0, 0))
        self.game_map.draw()
        self.display.fill((100,0 , 0), self.player.rect)

        if UI.status[BATTLE_MENU]:
            self.battle_screen.draw()
        if UI.status[GAME_MENU]:
            self.esc_screen.draw()

        pygame.display.flip()

    def check_key_events(self):
        key_events = pygame.event.get()
        dt = self.clock.tick() / 1000

        if not self.status[PAUSED]:
            self.player.move(pygame.key.get_pressed(), dt)

        for event in key_events:
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.esc_screen.toggle()
                elif UI.status[GAME_MENU]:
                    self.esc_screen.check_action(event.key)
                elif event.key == pygame.K_b: # --------------------------- TODO NA POTRZEBY TESTÓW
                    self.battle_screen.prepare_fight(self.player.ally, Enemy())
                    self.battle_screen.toggle()
                elif UI.status[BATTLE_MENU]:
                    self.battle_screen.check_action(event.key)

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
