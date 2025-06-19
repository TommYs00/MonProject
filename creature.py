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

        self.name: str
        self.id: int
        self.stats: dict[
                   LV: int,
                   EXP: list[int],
                   HP: list[int],
                   ATT: list[int],
                   DEF: list[int],
                   SPD: list[int]]

        self.abilities: dict[int: {
                ABILITY_NAME: str,
                DMG_BASE: int,
                DMG_MOD: int,
                DEBUFF_DMG: dict[str:int]}]

        if True: # ----------------------------------- TODO Na potrzeby testów ustawione na True
            self._load_data()

    def use_ability(self, ability, target):
        target.receive_dmg(self.abilities[ability], self.stats[ATT][0])

    def receive_dmg(self, ability, att):
        print(ability)
        hp_dmg =  ability[DMG_MOD] * max(0, att - max(0, self.stats[DEF][0])) + ability[DMG_BASE]
        self.stats[HP][0] -= hp_dmg
        self.stats[HP][0] = 0 if self.stats[HP][0] < 0 else self.stats[HP][0]
        if ability[DEBUFF_DMG]:
            for k,v in ability[DEBUFF_DMG].items():
                if k == ATT:
                    self.stats[ATT][0] -= v if self.stats[DEF][0] - v >= 0 else 0
                if k == DEF:
                    self.stats[DEF][0] -= v if self.stats[DEF][0] - v >= 0 else 0
                if k == SPD:
                    self.stats[SPD][0] -= v if self.stats[DEF][0] - v >= 0 else 0
        print(self.stats)

    def _load_data(self):  # ---------TODO na potrzeby testów z góry ustala statystyki bez ich faktycznego wczytywania
        self.name = "Chubboink"
        self.id = 0
        self.stats = {
                    LV: random.randint(1, 3),
                    EXP: [0, 30],
                    HP: [40, 40],
                    ATT: [3, 3],
                    DEF: [2, 2],
                    SPD: [2, 2]
        }
        self.abilities = {
            0: {
                ABILITY_NAME: "Fang Slam",
                DMG_BASE: 8,
                DMG_MOD: 4,
                DEBUFF_DMG: 0,
            },
            1: {
                NAME: "Roar",
                DMG_BASE: 0,
                DMG_MOD: 0,
                DEBUFF_DMG: {
                    ATT: 0,
                    DEF: 1,
                    SPD: 0
                }},
            2: None,
            3: None
        }

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