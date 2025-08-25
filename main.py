import pygame 
import constants
from character import Character
import requests
import json
import api
from mapa import Mapa

api.api_request()
mapa = Mapa("json_files/city_map.json", tile_size=20)



#screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
pygame.display.set_caption("Courier Quest")
#define variables of movement of the character
move_left = False
move_right = False
move_up = False
move_down = False

character = Character(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2)

clock = pygame.time.Clock()
run = True

while run:
    #control frame rate
    clock.tick(constants.FPS)
    #screen.fill(constants.COLOR_BACKGROUND)

    #calculate the movement of the player
    delta_x = 0
    delta_y = 0

    if move_left:
        delta_x = -3
    if move_right:
        delta_x = 3
    if move_up:
        delta_y = -3
    if move_down:
        delta_y = 3
    #move character
    character.movement(delta_x, delta_y)

    #character.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_left = True
            if event.key == pygame.K_RIGHT:
                move_right = True
            if event.key == pygame.K_UP:
                move_up = True
            if event.key == pygame.K_DOWN:
                move_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                move_left = False
            if event.key == pygame.K_RIGHT:
                move_right = False
            if event.key == pygame.K_UP:
                move_up = False
            if event.key == pygame.K_DOWN:
                move_down = False
    screen.fill((0, 0, 0))
    mapa.dibujar(screen)
    character.draw(screen)
    pygame.display.update()
    pygame.display.flip()

pygame.quit()