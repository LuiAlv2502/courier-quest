import pygame 
import constants
from character import Character
import requests
import json
import api
from mapa import Mapa


def main():
    pygame.init()
    api.api_request()
#map
    mapa = Mapa("json_files/city_map.json", tile_size=25)
#HUD

#screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
    screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
    pygame.display.set_caption("Courier Quest")



    character = Character(0,0, tile_size=25, screen=screen)

    clock = pygame.time.Clock()
    run = True
    while run:
        #control frame rate
        clock.tick(constants.FPS)
        #screen.fill(constants.COLOR_BACKGROUND)

        #calculate the movement of the player
        #character.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    character.movement(-1, 0, mapa)
                elif event.key == pygame.K_RIGHT:
                    character.movement(1, 0, mapa)
                elif event.key == pygame.K_UP:
                    character.movement(0, -1, mapa)
                if event.key == pygame.K_DOWN:
                    character.movement(0, 1, mapa)

        screen.fill((0, 0, 0))
        mapa.dibujar(screen)
        character.draw(screen)
        pygame.display.update()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()