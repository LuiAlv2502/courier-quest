import pygame
import constants

class Character:
    def __init__(self, x, y):
        self.shape = pygame.Rect(x, y, constants.WIDTH_CHARACTER, constants.HEIGHT_CHARACTER)
        self.shape.center = (x, y)
    
    def draw(self, screen):
        pygame.draw.rect(screen, constants.COLOR_CHARACTER, self.shape)

    def movement(self, dx, dy):
        self.shape.x += dx
        self.shape.y += dy