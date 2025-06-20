import pygame
import settings
from monster import Ally

class Player:
    def __init__(self, ally):
        self.rect = pygame.rect.FRect(0, 0, 64, 64)
        self.direction = pygame.Vector2(0, 0)
        self.speed = 500
        self.ally = Ally() # TODO: na potrzeby testów

    def move(self, actions, dt):
        self.direction.x = int(actions[pygame.K_d]) - int(actions[pygame.K_a])
        self.direction.y = int(actions[pygame.K_s]) - int(actions[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        self.rect.center += self.direction * self.speed * dt