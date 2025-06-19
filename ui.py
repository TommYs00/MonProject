import pygame
import settings
from const import *
from abc import ABC, abstractmethod

class UI(ABC):
    status = {}
    created = {}

    def __init__(self, game, menu_type, status):
        UI.created[menu_type] = self
        UI.status[menu_type] = status
        self.game = game
        self.type = menu_type
        self.font = pygame.font.Font(size=64)
        self.color = (255, 255, 255)
        self.bg_color = (0, 0, 0)


        self.menu = {OPTIONS: [None],
                     ACTION: [None],
                     SELECTED: [None],
                     POSITION: [None]}

    def _draw_before(self):
        pass

    def _draw_text(self):
        for i, text in enumerate(self.menu[OPTIONS]):
            if self.menu[SELECTED][i]:
                render = self.font.render("> " + text + " <", True, self.color, self.bg_color)
            else:
                render = self.font.render(text, True, self.color, self.bg_color)
            rect = render.get_rect()
            rect.midtop = self.menu[POSITION][i]
            self.game.display.blit(render, rect)

    def _draw_after(self):
        pass

    def draw(self):
        self._draw_before()
        self._draw_text()
        self._draw_after()

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
    def _default_menu(self):
        pass

    @abstractmethod
    def toggle(self):
        pass


class GameUI(UI):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self._default_menu()

    def toggle(self):
        UI.status[self.type] = not UI.status[self.type]
        self.game.status[PAUSED] = any([i for i in UI.status.values()])

    def _default_menu(self):
        self.menu[OPTIONS] = ["RESUME", "QUIT"]
        self.menu[ACTION] = [self.toggle, self.game.quit]
        self.menu[SELECTED] = [True, False]
        self.menu[POSITION] = [pygame.Vector2(settings.WIDTH // 2, settings.HEIGHT // 2 + i * 70) for i in range(2)]


class BattleUI(UI):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self._default_menu()

        # Surface & Images
        self.surf_b = pygame.surface.Surface((384, 300), pygame.SRCALPHA).convert_alpha()
        self.platform = pygame.image.load("images/floor.png").convert_alpha()
        self.ally_image = None
        self.enemy_image = None

        # Rects
        self.rect_b = None
        self.ally_rect = None
        self.enemy_rect = None

        # Objects
        self.ally = None
        self.enemy = None

    def prepare_fight(self, ally, enemy):
        self.ally = ally
        self.enemy = enemy

        self.ally_image = ally.image
        self.enemy_image = enemy.image

        self.rect_b = self.surf_b.get_rect()
        self.ally_rect = ally.image.get_rect()
        self.ally_rect.bottom = settings.HEIGHT - 250
        self.enemy_rect = enemy.image.get_rect()
        self.enemy_rect.centerx, self.enemy_rect.centery = self.rect_b.centerx, self.rect_b.centery + 40

        self.rect_b.right = settings.WIDTH - 200

    def _default_menu(self):
        self.menu[OPTIONS] = ["FIGHT", "ESCAPE"]
        self.menu[ACTION] = [self._selected_fight, self.toggle]
        self.menu[SELECTED] = [True, False]
        self.menu[POSITION] = [pygame.Vector2(settings.WIDTH - 300, settings.HEIGHT - 200 + i * 70) for i in range(2)]

    def _selected_fight(self):
        self.menu[OPTIONS] = ["Fang Slam", "Roar", "go back"]
        self.menu[ACTION] = [lambda: self.ally.use_ability(1, self.enemy),
                             lambda: self.ally.use_ability(2, self.enemy),
                             self._default_menu]
        self.menu[SELECTED] = [True, False, False]
        self.menu[POSITION] = [pygame.Vector2(settings.WIDTH - 300, settings.HEIGHT - 200 + i * 70) for i in range(3)]

    def toggle(self):
        UI.status[self.type] = not UI.status[self.type]
        self.game.status[PAUSED] = any([i for i in UI.status.values()])

    def _draw_before(self):
        self.game.display.fill((190, 255, 190))


        self.game.display.blit(self.platform, (-30, 420))
        self.game.display.blit(self.ally_image, self.ally_rect)

        self.surf_b.fill((0, 0, 0, 0))
        self.surf_b.blit(self.platform, (0, 180))
        self.surf_b.blit(self.enemy_image, self.enemy_rect)

        self.game.display.blit(self.surf_b, self.rect_b)

        self.game.display.fill((190, 190, 255), pygame.Rect(0, settings.HEIGHT - 250, settings.WIDTH, 250))