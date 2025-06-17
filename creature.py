import pygame
import settings
from const import *
import random
from abc import ABC, abstractmethod
from typing import Optional, List

# TODO: dodać domyśle wartości dla classy self.image i self.rect
# TODO: zaimplementować wyświetlanie stworka w panelu walki

class Creature(ABC):
    _enemy: Optional["Enemy"] = None
    _allies: Optional[List["Ally"]] = []

    def __init__(self, new_creature):
        self._add(new_creature)

        self.id: int
        self.level: int
        self.exp: tuple
        self._health: int
        self.attack: int
        self.defence: int
        self.speed: int

        self.abilities:dict

        if True: # ----------------------------------- TODO Na potrzeby testów ustawione na True
            self._load_data()

    def attack(self):
            pass

    def _load_data(self):  # ---------TODO na potrzeby testów z góry ustala statystyki bez ich faktycznego wczytywania
        self.id = 0
        self.name = "Chubboink"
        self.level = random.randint(1, 3)
        self.exp = 0
        self._health = 40
        self.attack = (3, 3)
        self.defence = (2, 2)
        self.speed = (2, 2)
        self.abilities = {1: {"name": "Fang Slam",
                              "dmg_base": 5,
                              "dmg_mod": 4,
                              "debuff_dmg": (0, 0, 0)},
                          2: {"name": "Roar",
                              "dmg_base": 0,
                              "dmg_mod": 0,
                              "debuff_dmg": (0, 1, 0)},
                          3: None,
                          4: None}

    @property
    def health(self):
        return self._health
    @health.setter
    def health(self, v):
        self._health = v if self._health - v > 0 else 0

    @abstractmethod
    def _dead(self):
        pass

    @classmethod
    def return_data(cls):
        pass

    @classmethod
    def _add(cls, creature):
        if isinstance(creature, Enemy):
            cls._enemy = creature
        elif isinstance(creature, Ally):
            cls._allies.append(creature)


class Enemy(Creature):
    def __init__(self):
        super().__init__(self)
        self.image = pygame.transform.scale_by(pygame.image.load("images/CHUBBOINK.png"), 2).convert_alpha()  # TODO: na potrzeby testów

    def _dead(self):
        return NotImplementedError

class Ally(Creature):
    def __init__(self):
        super().__init__(self)
        self.image = pygame.transform.scale_by(pygame.image.load("images/CHUBBOINK_B.png"),2).convert_alpha()  # TODO: na potrzeby testów

    def _dead(self):
        return NotImplementedError