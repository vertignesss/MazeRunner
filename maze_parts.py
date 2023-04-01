import utility
import pygame
import constants
class WallBlock(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect((x * constants.wall_size, y * constants.wall_size, constants.wall_size, constants.wall_size))
        self.color = (200, 200, 200)

    def draw(self, camera, screen):
        utility.draw(self, camera, screen)

class Button(object):
    def __init__(self, x, y):
        self.color = (191, 127, 127)
        self.pressed = False
        self.rect = pygame.rect.Rect(x * constants.wall_size + constants.wall_size / 4, y * constants.wall_size + constants.wall_size / 4, utility.wall_size / 2,
                                     constants.wall_size / 2)

    def update(self, player):
        if pygame.Rect.colliderect(self.rect, player.rect) and not self.pressed:
            self.pressed = True
        if self.pressed:
            self.color = (255, 63, 63)

    def draw(self, camera, screen):
        utility.draw(self, camera, screen)


class SpikedButton(Button):
    def __init__(self, x, y):
        self.color = (191, 127, 127)
        self.pressed = False
        self.rect = pygame.rect.Rect(x * constants.wall_size + constants.wall_size / 4, y * constants.wall_size + constants.wall_size / 4, utility.wall_size / 2,
                                     constants.wall_size / 2)
        self.ticksTillUnspike = 0

    def update(self, player):
        if self.ticksTillUnspike < 0:
            self.pressed = False
            self.color = (191, 127, 127)
        if pygame.Rect.colliderect(self.rect, player.rect) and not self.pressed:
            self.pressed = True
            self.ticksTillUnspike = 100
        if self.pressed:
            self.color = (0, 0, 0)
            if pygame.Rect.colliderect(self.rect, player.rect):
                player.getHit(1)
        self.ticksTillUnspike = self.ticksTillUnspike - 1


class Orb(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x * constants.wall_size + constants.wall_size * 2 / 8, y * constants.wall_size + constants.wall_size * 2 / 8,
                                     constants.wall_size / 2, constants.wall_size / 2)
        self.color = (0, 0, 255)

    def draw(self, camera, screen):
        constants.draw(self, camera, screen)


class Goal(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x * constants.wall_size, y * constants.wall_size, constants.wall_size, constants.wall_size)
        self.color = (255, 0, 255)

    def draw(self, camera, screen):
        utility.draw(self, camera, screen)




