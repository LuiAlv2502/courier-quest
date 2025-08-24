import pygame 
import constants
from character import Character

pygame.init()


screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
pygame.display.set_caption("Courier Quest")

character = Character(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2)

run = True
while run:
    character.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
    pygame.display.flip()

pygame.quit()