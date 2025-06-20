import random
from const import *

class BattleManager:
    def __init__(self):
        self.ally = None
        self.enemy = None
        self.player_turn = None

    def initialize(self, ally, enemy):
        self.ally = ally
        self.enemy = enemy

        if self.ally.stats[SPD] > self.enemy.stats[SPD]:
            self.player_turn = True
        elif self.ally.stats[SPD] < self.enemy.stats[SPD]:
            self.player_turn = False
        else:
            self.player_turn = random.choice([True, False])

    def control_battle(self, ability_key=None):
        if self.player_turn:
            self._change_turn()
            return self._player_attack(ability_key)
        else:
            self._change_turn()
            return self._ai_attack()

    def _player_attack(self, ability_key):
        ability = self.ally.use_ability(ability_key, self.enemy)

        string = ''
        if ability[DMG_BASE] or ability[DMG_MOD]:
            string += f'Your {self.ally.name} attacked with "{ability[ABILITY_NAME]}".'
        else:
            string += f'Your {self.ally.name} used "{ability[ABILITY_NAME]}".'

        if ability[DEBUFF_DMG]:
            if ability[DEBUFF_DMG][ATT]:
                string += "\nEnemy's attack has been decreased!"
            elif ability[DEBUFF_DMG][DEF]:
                string += "\nEnemy's defence has been decreased!"

        return string

    def _ai_attack(self):
        ability_key = random.randint(0, 3)
        while self.enemy.abilities[ability_key] == {}:
            ability_key = random.randint(0, 3)

        ability = self.enemy.use_ability(ability_key, self.ally)

        string = ''
        if ability[DMG_BASE] or ability[DMG_MOD]:
            string += f'Wild {self.ally.name} attacked with "{ability[ABILITY_NAME]}".'
        else:
            string += f'Wild {self.ally.name} used "{ability[ABILITY_NAME]}".'

        if ability[DEBUFF_DMG]:
            if ability[DEBUFF_DMG][ATT]:
                string += f"\nYour {self.ally.name}'s attack has been decreased!"
            elif ability[DEBUFF_DMG][DEF]:
                string += f"\nYour {self.ally.name}'s defence has been decreased!"

        return string

    def _change_turn(self):
        self.player_turn = not self.player_turn
