import pygame 
import constants
from character import Character
import api
from mapa import Mapa
from hud import draw_hud


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
        #añadir si no se presiona ningun boton
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if character.resistencia > 0:
                    if event.key == pygame.K_LEFT:
                        character.movement(-1, 0, mapa)
                    elif event.key == pygame.K_RIGHT:
                        character.movement(1, 0, mapa)
                    elif event.key == pygame.K_UP:
                        character.movement(0, -1, mapa)
                    elif event.key == pygame.K_DOWN:
                        character.movement(0, 1, mapa)

# --- Recuperar resistencia SOLO cuando no hay teclas presionadas ---
        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            character.recuperar_resistencia(1 / constants.FPS)

        screen.fill((0, 0, 0))
        mapa.dibujar(screen)
        character.draw(screen)
        draw_hud(screen, character)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()