import pygame
from abc import ABC, abstractmethod

import settings
from const import *
from monster import Monster, Ally, Enemy
from battlemenager import BattleManager

class UI:
    def __init__(self, game):
        self.game = game
        self.strategy = None # -> obj
        self.infobox_queue = []

        self.font = None # -> pygame.font.Font
        self.menu_index = {"col": 0, "row": 0} # -> dict[str: int, str: int]
        self.cols, self.rows = None, None  # -> int, int
        self.options = None  # -> list[str]
        self.positions = None  # -> list[tuple]
        self.surf = None  # -> pygame.surface.Surface
        self.surf_rect = None  # -> pygame.rect.Rect

        self.battle_manager = BattleManager()
        self.ally_ui = MonsterUI()
        self.enemy_ui = MonsterUI()

    def toggle(self, strategy=None):
        self.strategy = strategy
        self.game.status[PAUSED] = True if strategy is not None else False

    def initialize_battle(self):
        self.battle_manager.initialize()
        self.ally_ui.set(Monster.ally)
        self.enemy_ui.set(Monster.enemy)

        self.toggle(StrategyBattle(self))

    def check_keys(self, just_pressed):
        if self.strategy is not None:
            selected = self._return_selected(just_pressed)
            if just_pressed[pygame.K_RETURN]:
                self._select_option(selected)
            elif just_pressed[pygame.K_ESCAPE] and self.strategy.parent is not None:
                self.toggle(self.strategy.parent(self))
        elif self.strategy is None:
            if just_pressed[pygame.K_ESCAPE]:
                self.toggle(StrategyESC(self))

    def _return_selected(self, just_pressed):
        selected = None
        while selected is None or self.options[selected] == "":
            self.menu_index["col"] = (self.menu_index["col"] + just_pressed[pygame.K_RIGHT] - just_pressed[
                pygame.K_LEFT]) % self.cols
            self.menu_index["row"] = (self.menu_index["row"] + just_pressed[pygame.K_DOWN] - just_pressed[
                pygame.K_UP]) % self.rows
            selected = self.menu_index["col"] + self.menu_index["row"] * self.cols
        return selected

    def _select_option(self, selected):
        if self.options[selected] == RESUME or self.options[selected] == RUN:
            self.toggle()
        elif self.options[selected] == QUIT:
            self.game.quit()
        elif self.options[selected] == FIGHT:
            self.toggle(StrategyFight(self))

        elif self.strategy.type == UI_FIGHT or self.strategy.type == UI_INFO:
            if not self._check_if_infobox():
                if all([not self.battle_manager.attack_queue,
                        self.strategy.type == UI_INFO,
                        self.battle_manager.fighting]):
                    self.toggle(StrategyBattle(self))
                else:
                    fighting = self.battle_manager.control_battle(selected)

                    if not self._check_if_infobox():
                        if not fighting:
                            self.toggle()
                        elif fighting:
                            self.toggle(StrategyBattle(self))


    def _check_if_infobox(self):
        self.infobox_queue.extend(self.battle_manager.return_info_queue())
        if self.infobox_queue:
            if self.strategy.type != UI_INFO:
                self.toggle(StrategyInfo(self))
            self.options = [self.infobox_queue.pop(0)]
            return True
        return False

    def draw(self):
        if self.strategy is not None:
            if self.strategy.type == UI_FIGHT or self.strategy.type == UI_INFO:
                self.game.display.fill((190, 255, 190))
                self.enemy_ui.draw(self.game.display)
                self.ally_ui.draw(self.game.display)
                self.game.display.fill((220, 220, 220), pygame.Rect(0, settings.HEIGHT - 250, settings.WIDTH, 250))
                self.game.display.fill((240, 240, 240), pygame.Rect(0, settings.HEIGHT - 240, settings.WIDTH, 250))

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

# ------------------------------- Menu Strategies -------------------------------
class MenuStrategy(ABC):
    _type = None
    _parent_strategy = None

    def __init__(self, ui):
        self.ui = ui
        self.initialize()

    @property
    def parent(self):
        return self._parent_strategy

    @property
    def type(self):
        return self._type

    @abstractmethod
    def initialize(self):
        pass

# ------ Strategy 1 for MenuStrategy ------
class StrategyESC(MenuStrategy):
    _type = UI_ESC
    _parent_strategy = None

    def __init__(self, ui):
        super().__init__(ui)

    def initialize(self):
        self.ui.font = pygame.font.Font(size=48)
        self.ui.menu_index = {"col": 0, "row": 0}
        self.ui.cols, self.ui.rows = 1, 2
        self.ui.options = [RESUME, QUIT]
        pos = []
        for r in range(self.ui.rows):
            for c in range(self.ui.cols):
                pos.append((150 + 200 * c, 50 + r * 70))
        self.ui.positions = pos
        self.ui.surf = pygame.surface.Surface((300, 400), flags=pygame.SRCALPHA).convert_alpha()
        self.ui.surf_rect = self.ui.surf.get_rect()
        self.ui.surf_rect.center = settings.WIDTH // 2, settings.HEIGHT // 2

# ------ Strategy 2 for MenuStrategy ------
class StrategyBattle(MenuStrategy):
    _type = UI_FIGHT
    _parent_strategy = None

    def __init__(self, ui):
        super().__init__(ui)

    def initialize(self):
        self.ui.font = pygame.font.Font(size=48)
        self.ui.menu_index = {"col": 0, "row": 0}
        self.ui.cols, self.ui.rows = 2, 1
        self.ui.options = ["FIGHT", "RUN"]
        pos = []
        for r in range(self.ui.rows):
            for c in range(self.ui.cols):
                pos.append((100 + 200 * c, 50 + r * 70))
        self.ui.positions = pos
        self.ui.surf = pygame.surface.Surface((400, 200), flags=pygame.SRCALPHA).convert_alpha()
        self.ui.surf_rect = self.ui.surf.get_rect()
        self.ui.surf_rect.right = settings.WIDTH - 20
        self.ui.surf_rect.bottom = settings.HEIGHT - 20

# ------ Strategy 2 for MenuStrategy ------
class StrategyFight(MenuStrategy):
    _type = UI_FIGHT
    _parent_strategy = StrategyBattle

    def __init__(self, ui):
        super().__init__(ui)

    def initialize(self):
        self.ui.font = pygame.font.Font(size=48)
        self.ui.menu_index = {"col": 0, "row": 0}
        self.ui.cols, self.ui.rows = 2, 2
        self.ui.options = [i[ABILITY_NAME] if i else "" for i in Monster.ally.abilities.values()]
        pos = []
        for r in range(self.ui.rows):
            for c in range(self.ui.cols):
                pos.append((200 + 420 * c, 50 + r * 70))
        self.ui.positions = pos
        self.ui.surf = pygame.surface.Surface((800, 200), flags=pygame.SRCALPHA).convert_alpha()
        self.ui.surf_rect = self.ui.surf.get_rect()
        self.ui.surf_rect.left = 20
        self.ui.surf_rect.bottom = settings.HEIGHT - 20

# ------ Strategy 3 for MenuStrategy ------
class StrategyInfo(MenuStrategy):
    _type = UI_INFO
    _parent_strategy = None

    def __init__(self, ui):
        super().__init__(ui)

    def initialize(self):
        self.ui.font = pygame.font.Font(size=48)
        self.ui.menu_index = {"col": 0, "row": 0}
        self.ui.cols, self.ui.rows = 1, 1
        self.ui.options = ["<undefined>"]
        self.ui.surf = pygame.surface.Surface((settings.WIDTH - 40, 200), flags=pygame.SRCALPHA).convert_alpha()
        self.ui.surf_rect = self.ui.surf.get_rect()
        self.ui.surf_rect.centerx = settings.WIDTH // 2
        self.ui.surf_rect.bottom = settings.HEIGHT - 20
        self.ui.positions = [(self.ui.surf_rect.centerx, 40)]