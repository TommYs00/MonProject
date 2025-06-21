import random
from const import *

class BattleManager:
    def __init__(self):
        self.ally = None
        self.enemy = None
        self.player_turn = None
        self.fighting = None

        self.attack_queue = []
        self.info_queue = []

    def initialize(self, ally, enemy):
        ally.restore_stats()
        self.ally = ally
        self.enemy = enemy
        self.fighting = True
        self.attack_queue.clear()

        if self.ally.stats[SPD] > self.enemy.stats[SPD]:
            self.player_turn = True
        elif self.ally.stats[SPD] < self.enemy.stats[SPD]:
            self.player_turn = False
        else:
            self.player_turn = random.choice([True, False])

    def control_battle(self, state, ability_key=None):

        if state == UI_INFO and self.info_queue:
            return UI_INFO

        elif not self.fighting:
            return self.fighting

        elif self.fighting:
            message = ""
            if state == UI_INFO and not self.info_queue and not self.attack_queue:
                return UI_DEFAULT
            elif state != UI_INFO:
                if self.player_turn:
                    message = self._player_attack(ability_key)
                    self.attack_queue.append(self._computer_attack)
                else:
                    message = self._computer_attack()
                    self.attack_queue.append(lambda: self._player_attack(ability_key))

            elif state == UI_INFO and self.attack_queue:
                message = self.attack_queue.pop(0)()

            self._change_turn()
            self.info_queue.append(message)
            self._check_if_alive()
            return UI_INFO

    def return_info_string(self):
        return self.info_queue.pop(0)

    def _check_if_alive(self):
        if not self.ally.alive:
            self.fighting = False
            self.info_queue.append(f'Your {self.ally.name} has been defeated... The battle is over!')
        elif not self.enemy.alive:
            self.fighting = False
            self.info_queue.append(f'The wild {self.enemy.name} has been defeated!')
            self.info_queue.append(f'Your {self.ally.name} just gained {self.ally.gain_exp(self.enemy.stats[LV])} exp. The battle is over!')

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

    def _computer_attack(self):
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
