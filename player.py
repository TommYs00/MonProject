from collections import defaultdict

import pygame
import settings
from pytmx import load_pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, display, collide_group, ally, *groups):
        super().__init__(*groups)
        self.display = display
        self.collide_group = collide_group
        self.ally = ally

        # tmx data
        self.tmx_data = load_pygame("images/player/player.tmx")
        self.image_dict = defaultdict(dict)
        for sprite, direction, surf in self.tmx_data.get_layer_by_name("player").tiles():
            self.image_dict[direction][sprite] = surf

        self.image_dict = dict(self.image_dict)
        self.sprite_counter = 0
        self.sprite_direction = 0 # y: 0 - front; y: 1 - left; y: 2 - right; y: 3 - back

        # image and rects
        self.image= pygame.transform.scale_by(self.image_dict[0][2], 4)
        self.image_rect = self.image.get_rect()
        self.rect = pygame.rect.FRect(settings.staring_x, settings.starting_y, 5, 5)
        self.rect.center = settings.staring_x, settings.starting_y

        # movement
        self.direction = pygame.Vector2(0, 0) # kierunek ruchu w danej iteracji
        self.movement = pygame.Vector2(0, 0) # ruch w danej iteracji
        self.speed = 350

    def move(self, actions, just_pressed, dt):
        self.direction.x = int(actions[pygame.K_d]) - int(actions[pygame.K_a])
        self.direction.y = int(actions[pygame.K_s]) - int(actions[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.movement = self.direction * self.speed * dt

        self.rect.centerx += self.movement.x
        if self._check_collision():
            self.rect.centerx -= self.movement.x
            self.movement.x = 0
        self.rect.centery += self.movement.y
        if self._check_collision():
            self.rect.centery -= self.movement.y
            self.movement.y = 0

        self._check_sprite(just_pressed, dt)

    def draw(self):
        self.image_rect.midbottom = self.rect.midbottom
        self.display.blit(self.image, self.image_rect)

    def _check_sprite(self, just_pressed, dt):
        self.sprite_counter += dt * 1000

        if self.movement == (0, 0):
            self.sprite_counter = 0
        if just_pressed[pygame.K_s]:
            self.sprite_direction = 0
        if just_pressed[pygame.K_a]:
            self.sprite_direction = 1
        if just_pressed[pygame.K_d]:
            self.sprite_direction = 2
        if just_pressed[pygame.K_w]:
            self.sprite_direction = 3

        self.image = pygame.transform.scale_by(self.image_dict[self.sprite_direction][self.sprite_counter // 150 % 4], 4)

    def _check_collision(self):
        return pygame.sprite.spritecollide(self, self.collide_group, False)