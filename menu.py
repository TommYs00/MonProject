import pygame
import settings
from const import *
from abc import ABC, abstractmethod

class Menu(ABC):
    status = {}
    created = {}

    def __init__(self, game, menu_type, status):
        Menu.created[menu_type] = self
        Menu.status[menu_type] = status
        self.game = game
        self.type = menu_type
        self.font = pygame.font.Font(size=64)
        self.color = (255, 255, 255)
        self.bg_color = (0, 0, 0)

        self.menu = {OPTIONS: [None],
                     ACTION: [None],
                     SELECTED: [None],
                     POSITION: [None]}

    def _draw_under(self):
        pass

    def draw(self):
        self._draw_under()
        for i, text in enumerate(self.menu[OPTIONS]):
            if self.menu[SELECTED][i]:
                render = self.font.render("> " + text + " <", True, self.color, self.bg_color)
            else:
                render = self.font.render(text, True, self.color, self.bg_color)
            rect = render.get_rect()
            rect.midtop = self.menu[POSITION][i]
            self.game.display.blit(render, rect)

    def check_action(self, key):
        if key == pygame.K_UP:
            self.menu[SELECTED] = self.menu[SELECTED][1:] + [self.menu[SELECTED][0]]
        elif key == pygame.K_DOWN:
            self.menu[SELECTED] = [self.menu[SELECTED][-1]] + self.menu[SELECTED][:-1]
        elif key == pygame.K_RETURN:
            for i, state in enumerate(self.menu[SELECTED]):
                if state:
                    self.menu[ACTION][i]()

    @abstractmethod
    def toggle(self):
        pass

class GameMenu(Menu):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self.menu = {OPTIONS: ["RESUME", "QUIT"],
                     ACTION: [self.toggle, self.game.quit],
                     SELECTED: [True, False],
                     POSITION: [pygame.Vector2(settings.WIDTH // 2, settings.HEIGHT // 2 + i * 70) for i in range(2)]}

    def toggle(self):
        Menu.status[self.type] = not Menu.status[self.type]
        self.game.status[PAUSED] = any([i for i in Menu.status.values()])


class BattleMenu(Menu):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self.menu = {OPTIONS: ["FIGHT", "ESCAPE"],
                            ACTION: [self._fight, self.toggle],
                            SELECTED: [True, False],
                            POSITION: [pygame.Vector2(settings.WIDTH - 300, settings.HEIGHT - 200 + i * 70) for i in range(2)]}

    def _fight(self):
        self.menu = {OPTIONS: ["TACKLE", "DEBFF", "go back"],
                     ACTION: [None, None, self._default],
                     SELECTED: [True, False, False],
                     POSITION: [pygame.Vector2(settings.WIDTH - 300, settings.HEIGHT - 200 + i * 70) for i in range(3)]}

    def _default(self):
        self.menu = {OPTIONS: ["FIGHT", "ESCAPE"],
                     ACTION: [self._fight, self.toggle],
                     SELECTED: [True, False],
                     POSITION: [pygame.Vector2(settings.WIDTH - 300, settings.HEIGHT - 200 + i * 70) for i in range(2)]}

    def toggle(self):
        Menu.status[self.type] = not Menu.status[self.type]
        self.game.status[PAUSED] = any([i for i in Menu.status.values()])

    def _draw_under(self):
        self.game.display.fill((255, 255, 255))
