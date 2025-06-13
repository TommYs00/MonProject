import pygame, sys
from Player import Player
from GameMenu import GameMenu
from MapManager import MapManager
import settings

class MonProject:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("MonProject")
        self.display = pygame.display.set_mode(settings.RESOLUTION)
        self.clock = pygame.time.Clock()
        self.status = {"running": True,
                       "paused": False,
                       "battle": False,
                       "player_menu": False,
                       "game_menu": False}

        self.game_menu = GameMenu(self)
        self.game_map = MapManager(self)

        self.player = Player()

    def update_display(self):
        self.display.fill((0, 0, 0))
        self.game_map.draw()
        self.display.fill((100,0 , 0), self.player.rect)


        if self.status["game_menu"]:
            self.game_menu.draw()

        pygame.display.flip()

    def check_key_events(self):
        key_events = pygame.event.get()
        dt = self.clock.tick() / 1000

        if not self.status["paused"]:
            self.player.move(pygame.key.get_pressed(), dt)

        for event in key_events:
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_menu.toggle_menu()
                elif self.status["game_menu"]:
                    self.game_menu.check_action(event.key)
                elif self.status["player_menu"]:
                    pass


    def quit(self):
        self.status["running"] = False
        pygame.quit()
        sys.exit()

    def run(self):
        while self.status["running"]:
            self.update_display()
            self.check_key_events()


if __name__ == "__main__":
    game = MonProject()
    pygame.init()
    game.run()
