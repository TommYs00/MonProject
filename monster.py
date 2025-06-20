import pygame
import settings
from const import *
import random
from abc import ABC, abstractmethod
from typing import Optional, List
import json

# TODO: dodać domyśle wartości dla classy self.image i self.rect
# TODO: zaimplementować wyświetlanie stworka w panelu walki

class Monster(ABC):
    _enemy: Optional["Enemy"] = None
    _allies: Optional[List["Ally"]] = []

    def __init__(self, new_monster):
        self._add(new_monster)

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
        print(ability)
        print(self.stats)

    def return_health_ratio(self):
        return self.stats[HP][0] / self.stats[HP][1]

    def _load_data(self, index=0):
        with open("monsters.json", "r") as json_data:
            data = json.load(json_data)[str(index)]
            self.id = data[ID]
            self.name = data[NAME]
            self.images = {FRONT_IMG: data[FRONT_IMG],
                           BACK_IMG: data[BACK_IMG]}
            self.stats = data[STATS]
            self.abilities = {}
            for k, v in data[ABILITIES].items():
                self.abilities[int(k)] = v

    @abstractmethod
    def _dead(self):
        pass

    @classmethod
    def return_data(cls):
        pass

    @classmethod
    def _add(cls, monster):
        if isinstance(monster, Enemy):
            cls._enemy = monster
        elif isinstance(monster, Ally):
            cls._allies.append(monster)


class Enemy(Monster):
    def __init__(self):
        super().__init__(self)
        self.image = pygame.transform.scale_by(pygame.image.load(f"{self.images[FRONT_IMG]}"), 2).convert_alpha()  # TODO: na potrzeby testów

    def _dead(self):
        return NotImplementedError


class Ally(Monster):
    def __init__(self):
        super().__init__(self)
        self.image = pygame.transform.scale_by(pygame.image.load(f"{self.images[BACK_IMG]}"), 2).convert_alpha()  # TODO: na potrzeby testów

    def _dead(self):
        return NotImplementedError