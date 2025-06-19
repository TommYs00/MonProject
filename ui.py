import pygame
from pygame import SRCALPHA

import settings
from const import *
from abc import ABC, abstractmethod
from creature import Ally, Enemy

class MenuUI(ABC):
    status = {}
    created = {}

    def __init__(self, game, menu_type, status):
        MenuUI.created[menu_type] = self
        MenuUI.status[menu_type] = status
        self.game = game
        self.type = menu_type
        self.font = pygame.font.Font(size=64)
        self.color = (255, 255, 255)
        self.s_color = (200, 200, 200)
        self.bg_color = (0, 0, 0)

        self.state = "default"
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 0, 0
        self.options = []
        self.positions = []

    def draw(self):
        surf = pygame.surface.Surface((300, 400), flags=SRCALPHA).convert_alpha()
        surf_rect = surf.get_rect()
        surf.fill((0, 0, 0, 100))

        selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
        for i, string in enumerate(self.options):
            if i == selected:
                text = self.font.render(string, True, self.color, self.s_color)
            elif string == "—":
                text = self.font.render(string, True, self.color)
            else:
                text = self.font.render(string, True, self.color, self.bg_color)
            text_rect = text.get_rect()
            text_rect.midtop = self.positions[i]
            surf.blit(text, text_rect)

        surf_rect.center = settings.WIDTH // 2, settings.HEIGHT // 2
        self.game.display.blit(surf, surf_rect)

    def check_action(self, just_pressed):
        self.menu_index["col"] = (self.menu_index["col"] + just_pressed[pygame.K_RIGHT] - just_pressed[
            pygame.K_LEFT]) % self.cols
        self.menu_index["row"] = (self.menu_index["row"] + just_pressed[pygame.K_DOWN] - just_pressed[
            pygame.K_UP]) % self.rows

        selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
        while self.options[selected] == "—":
            self.menu_index["col"] = (self.menu_index["col"] + just_pressed[pygame.K_RIGHT] - just_pressed[
                pygame.K_LEFT]) % self.cols
            self.menu_index["row"] = (self.menu_index["row"] + just_pressed[pygame.K_DOWN] - just_pressed[
                pygame.K_UP]) % self.rows
            selected = self.menu_index["col"] + self.menu_index["row"] * self.cols

        if just_pressed[pygame.K_RETURN]:
            selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
            self._select_option(selected)

    def toggle(self):
        self.state = "default"
        MenuUI.status[self.type] = not MenuUI.status[self.type]
        self.game.status[PAUSED] = any([i for i in MenuUI.status.values()])

    @abstractmethod
    def _select_option(self, selected):
        pass

    @abstractmethod
    def _default_menu(self):
        pass

class GameMenuUI(MenuUI):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self._default_menu()

    def _default_menu(self):
        self.state = UI_DEFAULT
        self.menu_index = {"col": 0, "row": 0}
        self.options = ["RESUME", "QUIT"]
        self.cols, self.rows = 1, 2
        self.positions = [(150, 50 + i * 70) for i in range(len(self.options))]

    def _select_option(self, selected):
        if self.options[selected] == "RESUME":
            self.toggle()
        elif self.options[selected] == "QUIT":
            self.game.quit()


class BattleMenuUI(MenuUI):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self._default_menu()

        self.ally = None
        self.enemy = None

        self.enemy_ui = None
        self.ally_ui = None

    def prepare_fight(self, ally, enemy):
        self.ally = ally
        self.enemy = enemy
        self.enemy_ui = CreatureUI(enemy)
        self.ally_ui = CreatureUI(ally)

    def check_action(self, just_pressed):
        super().check_action(just_pressed)
        if just_pressed[pygame.K_ESCAPE] and not self.state == UI_DEFAULT:
            self._default_menu()

    def _select_option(self, selected):
        if self.options[selected] == "FIGHT":
            self._selected_fight()
        elif self.options[selected]  == "ESCAPE":
            self.toggle()
        elif self.state == UI_FIGHT:
            self.ally.use_ability(selected, self.enemy)

    def _default_menu(self):
        self.state = UI_DEFAULT
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 1, 2
        self.options = ["FIGHT", "ESCAPE"]
        self.positions = [(150, 50 + i * 70) for i in range(len(self.options))]

    def _selected_fight(self):
        self.state = UI_FIGHT
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 1, 4
        self.options = [i[ABILITY_NAME] if i else "—" for i in self.ally.abilities.values()]
        self.positions = [(150, 50 + i * 70) for i in range(len(self.options))]

    def draw(self):
        self.game.display.fill((190, 255, 190))
        self.enemy_ui.draw(self.game.display)
        self.ally_ui.draw(self.game.display)
        self.game.display.fill((190, 190, 255), pygame.Rect(0, settings.HEIGHT - 250, settings.WIDTH, 250))
        super().draw()

# TODO: zaimplementować
# pos = []
#         for r in range(1, self.rows + 1):
#             for c in range(1, self.cols + 1):
#                 pos.append((150 * c, 50 + r * 70))
#         self.positions = pos

class CreatureUI:
    def __init__(self, creature):
        self.creature = creature

        # surface and images
        self.surf = pygame.surface.Surface((384, 400), pygame.SRCALPHA).convert_alpha()
        self.platform = pygame.image.load("images/floor.png").convert_alpha()
        self.creature_image = creature.image

        # rects
        self.s_rect = self.surf.get_rect()
        self.p_rect = self.platform.get_rect()
        self.c_rect = self.creature_image.get_rect()

        self._set_rects()

    def draw(self, main_surf):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.platform, self.p_rect)
        self.surf.blit(self.creature_image, self.c_rect)
        main_surf.blit(self.surf, self.s_rect)

    def _set_rects(self):
        if isinstance(self.creature, Enemy):
            self.c_rect.center = (self.s_rect.centerx, self.s_rect.centery)
            self.p_rect.topleft = (0, 180)
            self.s_rect.right = settings.WIDTH - 200
        elif isinstance(self.creature, Ally):
            self.p_rect.topleft = (-50, 280)
            self.s_rect.bottom = settings.HEIGHT - 170
