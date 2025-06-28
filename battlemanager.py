import random

from const import *
from monster import Monster, AbilityNotFoundError


class BattleManager:
    def __init__(self):

        self.player_turn = None
        self.fighting = False

        self.attack_queue = []
        self.info_queue = []

    def initialize(self):
        Monster.ally.restore_stats()
        Monster.new_enemy(random.randint(0, 2))
        self.fighting = True
        self.attack_queue.clear()

        if Monster.ally.stats[SPD] > Monster.enemy.stats[SPD]:
            self.player_turn = True
        elif Monster.ally.stats[SPD] < Monster.enemy.stats[SPD]:
            self.player_turn = False
        else:
            self.player_turn = random.choice([True, False])

    def control_battle(self, ability_key=None):
        if self.fighting:
            if self.attack_queue:
                self.attack_queue.pop(0)()
            elif self.player_turn:
                self._player_attack(ability_key)
                self.attack_queue.append(self._computer_attack)
            elif not self.player_turn:
                self._computer_attack()
                self.attack_queue.append(lambda: self._player_attack(ability_key))
            self._check_if_alive()

        return self.fighting

    def return_info_queue(self):
        info_queue = [i for i in self.info_queue]
        self.info_queue.clear()
        return info_queue

    def _check_if_alive(self):
        if not Monster.ally.alive:
            self.fighting = False
            self.info_queue.append(f'Your {Monster.ally.name} has been defeated... The battle is over!')
        elif not Monster.enemy.alive:
            self.fighting = False
            self.info_queue.append(f'The wild {Monster.enemy.name} has been defeated!')
            self.info_queue.append(f'Your {Monster.ally.name} just gained {Monster.ally.gain_exp(Monster.enemy.stats[LV])} exp. The battle is over!')

    def _player_attack(self, ability_key):
        ability, dmg = Monster.ally.use_ability(ability_key, Monster.enemy)
        string = ''

        if ability[DMG_BASE] or ability[DMG_MOD]:
            string += f'Your {Monster.ally.name} attacked with "{ability[ABILITY_NAME]}" ({dmg} DMG).'
        else:
            string += f'Your {Monster.ally.name} used "{ability[ABILITY_NAME]}".'

        if ability[DEBUFF_DMG]:
            if ability[DEBUFF_DMG][ATT]:
                string += "\nEnemy's attack has been decreased!"
            if ability[DEBUFF_DMG][DEF]:
                string += "\nEnemy's defence has been decreased!"

        self._change_turn()
        self.info_queue.append(string)

    def _computer_attack(self):
        try:
            idx = self._pick_ability(Monster.enemy)
            ability, dmg = Monster.enemy.use_ability(idx, Monster.ally)
        except AbilityNotFoundError as e:
            print(e)
            ability, dmg = Monster.enemy.use_ability(0, Monster.ally)

        string = ''

        if ability[DMG_BASE] or ability[DMG_MOD]:
            string += f'Wild {Monster.enemy.name} attacked with "{ability[ABILITY_NAME]}" ({dmg} DMG).'
        else:
            string += f'Wild {Monster.enemy.name} used "{ability[ABILITY_NAME]}".'

        if ability[DEBUFF_DMG]:
            if ability[DEBUFF_DMG][ATT]:
                string += f"\nYour {Monster.ally.name}'s attack has been decreased!"
            if ability[DEBUFF_DMG][DEF]:
                string += f"\nYour {Monster.ally.name}'s defence has been decreased!"

        self._change_turn()
        self.info_queue.append(string)

    def _pick_ability(self, monster):
        idx = random.randint(0, 3)
        ability = monster.abilities.get(idx, monster.name)
        if not ability:
            raise AbilityNotFoundError(idx, monster)
        return idx

    def _change_turn(self):
        self.player_turn = not self.player_turn