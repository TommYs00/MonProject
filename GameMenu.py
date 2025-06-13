import pygame
import settings

class GameMenu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(size=64)
        self.color = (255, 255, 255)
        self.menu = {"string": ["RESUME", "QUIT"],
                     "function": [self.toggle_menu, self.game.quit],
                     "selected": [True, False],
                     "location": [pygame.Vector2(settings.WIDTH // 2, settings.HEIGHT // 2 + i * 70) for i in range(2)]}

    def draw(self):
        for i, text in enumerate(self.menu["string"]):
            if self.menu["selected"][i]:
                render = self.font.render("> " + text + " <", True, self.color)
            else:
                render = self.font.render(text, True, self.color)
            rect = render.get_rect()
            rect.midtop = self.menu["location"][i]
            self.game.display.blit(render, rect)

    def check_action(self, key):
            if key == pygame.K_UP:
                self.menu["selected"] = self.menu["selected"][1:] + [self.menu["selected"][0]]
            elif key == pygame.K_DOWN:
                self.menu["selected"] = [self.menu["selected"][-1]] + self.menu["selected"][:-1]
            elif key == pygame.K_RETURN:
                for i, state in enumerate(self.menu["selected"]):
                    if state:
                        self.menu["function"][i]()

    def toggle_menu(self):
        self.game.status["paused"] = not self.game.status["paused"]
        self.game.status["game_menu"] = not self.game.status["game_menu"]