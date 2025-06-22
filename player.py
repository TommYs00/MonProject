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
        self.player_upper = self.tmx_data.get_layer_by_name("Upper")
        self.player_lower = self.tmx_data.get_layer_by_name("Lower")
        self.player_upper = [i for i in self.player_upper.tiles()]
        self.player_lower = [i for i in self.player_lower.tiles()]

        # image and rects
        self.upper_image = pygame.transform.scale_by(self.player_upper[0][2], 4)
        self.lower_image = pygame.transform.scale_by(self.player_lower[0][2], 4)
        self.image_rect = self.upper_image.get_rect()
        self.rect = pygame.rect.FRect(settings.staring_x, settings.starting_y, settings.tile_size, settings.tile_size)
        self.rect.center = settings.staring_x, settings.starting_y

        # movement
        self.direction = pygame.Vector2(0, 0) # kierunek ruchu w danej iteracji
        self.movement = pygame.Vector2(0, 0) # ruch w danej iteracji
        self.speed = 350

    def move(self, actions, dt):
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

    def draw(self):
        self.image_rect.midbottom = self.rect.midtop
        self.display.blit(self.upper_image, self.image_rect)
        self.image_rect.midtop = self.rect.midtop
        self.display.blit(self.lower_image, self.image_rect)

    def _check_collision(self):
        return pygame.sprite.spritecollide(self, self.collide_group, False)