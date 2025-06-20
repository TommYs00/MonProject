import pygame
from pygame import SRCALPHA

import settings
from const import *
from abc import ABC, abstractmethod
from monster import Ally, Enemy

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

        self.state = None
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 0, 0
        self.options = []
        self.positions = []

        self._default_menu()

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
            print(selected)
            self._select_option(selected)

    def toggle(self):
        self._default_menu()
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

        self.ally = None
        self.enemy = None

        self.enemy_ui = None
        self.ally_ui = None

    def prepare_fight(self, ally, enemy):
        self.ally = ally
        self.enemy = enemy
        self.enemy_ui = MonsterUI(enemy)
        self.ally_ui = MonsterUI(ally)

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

class MonsterUI:
    def __init__(self, monster):
        self.monster = monster
        self.font = pygame.font.Font(size=24)

        # surface and images
        self.surf = pygame.surface.Surface((384, 400), pygame.SRCALPHA).convert_alpha()
        self.info_bar = pygame.surface.Surface((280, 50), pygame.SRCALPHA).convert_alpha()
        self.platform = pygame.image.load("images/floor.png").convert_alpha()
        self.monster_image = monster.image

        # rects
        self.surf_rect = self.surf.get_rect()
        self.platform_rect = self.platform.get_rect()
        self.monster_rect = self.monster_image.get_rect()
        self.ib_rect = self.info_bar.get_rect()
        self.hp_rect = pygame.Rect(0, 0, 250, 5)

        self._set_rects()

    def draw(self, main_surf):
        self._draw_monster(main_surf)
        self._draw_info_bar(main_surf)

    def _draw_monster(self, main_surf):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.platform, self.platform_rect)
        self.surf.blit(self.monster_image, self.monster_rect)
        main_surf.blit(self.surf, self.surf_rect)

    def _draw_info_bar(self, main_surf):
        health_ratio = self.monster.return_health_ratio()
        health_ratio_rect = pygame.rect.Rect(self.hp_rect.left, self.hp_rect.top, int(health_ratio * 250), 5)
        text = self.font.render(f"{self.monster.name}   Lv: {self.monster.stats[LV]}", True, (240, 240, 240, 255))

        self.info_bar.fill((0, 0, 0, 100))
        self.info_bar.blit(text, (15, 15))
        self.info_bar.fill((240, 240, 240, 255), self.hp_rect)
        self.info_bar.fill((255, 0, 0, 255), health_ratio_rect)
        pygame.draw.rect(self.info_bar, (100, 0, 0, 255),self.hp_rect, 1)
        main_surf.blit(self.info_bar, self.ib_rect)

    def _set_rects(self):
        self.hp_rect.centerx = self.ib_rect.centerx
        self.hp_rect.bottom = self.ib_rect.bottom - 10
        if isinstance(self.monster, Enemy):
            self.monster_rect.center = (self.surf_rect.centerx, self.surf_rect.centery)
            self.platform_rect.topleft = (0, 180)
            self.surf_rect.right = settings.WIDTH - 200
            self.ib_rect.centerx = settings.WIDTH // 2
            self.ib_rect.y += 80
        elif isinstance(self.monster, Ally):
            self.platform_rect.topleft = (-50, 280)
            self.surf_rect.bottom = settings.HEIGHT - 170
            self.ib_rect.right = settings.WIDTH // 2
            self.ib_rect.y += 400
