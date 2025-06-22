import pygame
from pygame import SRCALPHA

import settings
from const import *
from abc import ABC, abstractmethod
from monster import Ally, Enemy
from battlemenager import BattleManager

class MenuUI(ABC):
    status = {}
    created = {}

    def __init__(self, game, menu_type, status):
        MenuUI.created[menu_type] = self
        MenuUI.status[menu_type] = status
        self.game = game
        self.type = menu_type
        self.font = pygame.font.Font(size=48)

        self.state = None
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 0, 0
        self.options = []
        self.positions = []

        self.surf = pygame.surface.Surface((300, 400), flags=SRCALPHA).convert_alpha()
        self.surf_rect = self.surf.get_rect()
        self.surf_rect.center = settings.WIDTH // 2, settings.HEIGHT // 2

        self._menu_default()

    def toggle(self):
        self._menu_default()
        MenuUI.status[self.type] = not MenuUI.status[self.type]
        self.game.status[PAUSED] = any([i for i in MenuUI.status.values()])

    def draw(self):
        self.surf.fill((0, 0, 0, 100))

        selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
        for i, string in enumerate(self.options):
            if i == selected:
                text = self.font.render(string, True, (255, 255, 255))
            elif string == "":
                text = self.font.render("—", True, (200, 200, 200))
            else:
                text = self.font.render(string, True, (200, 200, 200))
            text_rect = text.get_rect()
            text_rect.midtop = self.positions[i]
            self.surf.blit(text, text_rect)

        self.game.display.blit(self.surf, self.surf_rect)

    def check_action(self, just_pressed):
        self.menu_index["col"] = (self.menu_index["col"] + just_pressed[pygame.K_RIGHT] - just_pressed[
            pygame.K_LEFT]) % self.cols
        self.menu_index["row"] = (self.menu_index["row"] + just_pressed[pygame.K_DOWN] - just_pressed[
            pygame.K_UP]) % self.rows

        selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
        while self.options[selected] == "":
            self.menu_index["col"] = (self.menu_index["col"] + just_pressed[pygame.K_RIGHT] - just_pressed[
                pygame.K_LEFT]) % self.cols
            self.menu_index["row"] = (self.menu_index["row"] + just_pressed[pygame.K_DOWN] - just_pressed[
                pygame.K_UP]) % self.rows
            selected = self.menu_index["col"] + self.menu_index["row"] * self.cols

        if just_pressed[pygame.K_RETURN]:
            selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
            self._select_option(selected)

    @abstractmethod
    def _select_option(self, selected):
        pass

    @abstractmethod
    def _menu_default(self):
        pass


class GameMenuUI(MenuUI):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)

    def _select_option(self, selected):
        if self.options[selected] == "RESUME":
            self.toggle()
        elif self.options[selected] == "QUIT":
            self.game.quit()

    def _menu_default(self):
        self.state = UI_DEFAULT
        self.menu_index = {"col": 0, "row": 0}
        self.options = ["RESUME", "QUIT"]
        self.cols, self.rows = 1, 2
        pos = []
        for r in range(self.rows):
            for c in range(self.cols):
                pos.append((150 + 200 * c, 50 + r * 70))
        self.positions = pos


class BattleMenuUI(MenuUI):
    def __init__(self, game, menu_type, status=False):
        super().__init__(game, menu_type, status)
        self.battle_manager = BattleManager()
        self.ally_ui = MonsterUI()
        self.enemy_ui = MonsterUI()

        self.ally = None
        self.enemy = None

    def initialize(self, ally, enemy):
        self.ally = ally
        self.enemy = enemy
        self.battle_manager.initialize(ally, enemy)
        self.ally_ui.set(ally)
        self.enemy_ui.set(enemy)

    def draw(self):
        self.game.display.fill((190, 255, 190))
        self.enemy_ui.draw(self.game.display)
        self.ally_ui.draw(self.game.display)
        self.game.display.fill((220, 220, 220), pygame.Rect(0, settings.HEIGHT - 250, settings.WIDTH, 250))
        self.game.display.fill((240, 240, 240), pygame.Rect(0, settings.HEIGHT - 240, settings.WIDTH, 250))
        super().draw()

    def check_action(self, just_pressed):
        super().check_action(just_pressed)
        if just_pressed[pygame.K_ESCAPE] and not self.state == UI_DEFAULT and not self.state == UI_INFO:
            self._menu_default()

    def _select_option(self, selected):

        if self.options[selected] == "FIGHT":
            self._menu_fight()
        elif self.options[selected]  == "ESCAPE":
            self.toggle()

        elif self.state == UI_FIGHT or self.state == UI_INFO:
            new_state = self.battle_manager.control_battle(self.state, selected)

            if new_state == UI_INFO:
                self._menu_info(self.battle_manager.return_info_string())
            elif new_state == UI_DEFAULT:
                self._menu_default()
            elif not new_state:
                self.toggle()

# ----- MENU ---------------------------------------------
    def _menu_default(self):
        self.state = UI_DEFAULT
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 2, 1
        self.options = ["FIGHT", "ESCAPE"]
        pos = []
        for r in range(self.rows):
            for c in range(self.cols):
                pos.append((100 + 200 * c, 50 + r * 70))
        self.positions = pos

        self.surf = pygame.surface.Surface((400, 200), flags=SRCALPHA).convert_alpha()
        self.surf_rect = self.surf.get_rect()
        self.surf_rect.right = settings.WIDTH - 20
        self.surf_rect.bottom = settings.HEIGHT - 20

    def _menu_fight(self):
        self.state = UI_FIGHT
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 2, 2
        self.options = [i[ABILITY_NAME] if i else "" for i in self.ally.abilities.values()]
        pos = []
        for r in range(self.rows):
            for c in range(self.cols):
                pos.append((200 + 420 * c, 50 + r * 70))
        self.positions = pos

        self.surf = pygame.surface.Surface((800, 200), flags=SRCALPHA).convert_alpha()
        self.surf_rect = self.surf.get_rect()
        self.surf_rect.left = 20
        self.surf_rect.bottom = settings.HEIGHT - 20

    def _menu_info(self, info):
        self.state = UI_INFO
        self.menu_index = {"col": 0, "row": 0}
        self.cols, self.rows = 1, 1
        self.options = [info]

        self.surf = pygame.surface.Surface((settings.WIDTH - 40, 200), flags=SRCALPHA).convert_alpha()
        self.surf_rect = self.surf.get_rect()
        self.surf_rect.centerx = settings.WIDTH // 2
        self.surf_rect.bottom = settings.HEIGHT - 20

        self.positions = [(self.surf_rect.centerx, 40)]


class MonsterUI:
    def __init__(self):
        self.monster = None
        self.font = pygame.font.Font(size=24)

        # surface and images
        self.surf = pygame.surface.Surface((384, 400), pygame.SRCALPHA).convert_alpha()
        self.info_bar = pygame.surface.Surface((280, 50), pygame.SRCALPHA).convert_alpha()
        self.platform = pygame.image.load("images/misc/floor.png").convert_alpha()
        self.monster_image = None

        # rects
        self.surf_rect = None
        self.platform_rect = None
        self.monster_rect = None
        self.ib_rect = None
        self.hp_rect = None

    def set(self, monster):
        self.monster = monster
        self.monster_image = monster.image
        self._set_rects()

    def draw(self, main_surf):
        # info bar
        health_ratio = self.monster.return_health_ratio()
        health_ratio_rect = pygame.rect.Rect(self.hp_rect.left, self.hp_rect.top, int(health_ratio * 250), 5)
        text = self.font.render(f"{self.monster.name}   Lv: {self.monster.stats[LV]}", True, (240, 240, 240, 255))

        self.info_bar.fill((0, 0, 0, 100))
        self.info_bar.blit(text, (15, 15))
        self.info_bar.fill((240, 240, 240, 255), self.hp_rect)
        self.info_bar.fill((255, 0, 0, 255), health_ratio_rect)
        pygame.draw.rect(self.info_bar, (100, 0, 0, 255), self.hp_rect, 1)
        main_surf.blit(self.info_bar, self.ib_rect)

        # monster
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.platform, self.platform_rect)
        self.surf.blit(self.monster_image, self.monster_rect)
        main_surf.blit(self.surf, self.surf_rect)

    def _set_rects(self):
        # creating rects
        self.surf_rect = self.surf.get_rect()
        self.platform_rect = self.platform.get_rect()
        self.monster_rect = self.monster_image.get_rect()
        self.ib_rect = self.info_bar.get_rect()
        self.hp_rect = pygame.Rect(0, 0, 250, 5)

        # setting rects
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
