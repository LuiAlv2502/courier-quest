import pygame
import constants

class Character:
    def __init__(self, tile_x, tile_y, tile_size, screen):
        self.screen = screen
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.tile_size = tile_size
        self.shape = pygame.Rect(
            tile_x * tile_size,
            tile_y * tile_size,
            constants.WIDTH_CHARACTER,
            constants.HEIGHT_CHARACTER
        )
        self.shape.center = (tile_x * tile_size + tile_size // 2,
                             tile_y * tile_size + tile_size // 2)
    def draw(self, screen):
        pygame.draw.rect(screen, constants.COLOR_CHARACTER, self.shape)

    def movement(self, dx, dy, mapa):
        for _ in range(3):
            nueva_x = self.tile_x + dx
            nueva_y = self.tile_y + dy
            if not mapa.is_blocked(nueva_x, nueva_y):
                self.tile_x = nueva_x
                self.tile_y = nueva_y
                self.shape.center = (self.tile_x * self.tile_size + self.tile_size // 2,
                                    self.tile_y * self.tile_size + self.tile_size // 2)
                self.draw(self.screen)
                pygame.display.flip()
            pygame.time.delay(50)
