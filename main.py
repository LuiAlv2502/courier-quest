
import pygame 
import constants
from character import Character
import api
from mapa import Mapa
from hud import draw_hud
from stack import Stack
from game_over import show_game_over
from victory import show_victory

# Clase Stack para historial de movimientos

def main():
    pygame.init()
    api.api_request()
    # Leer datos del JSON
    import json
    with open("json_files/city_map.json", "r", encoding="utf-8") as f:
        map_json = json.load(f)["data"]
    tiempo_limite = map_json.get("max_time", 120)
    objetivo_valor = map_json.get("goal", None)
    # Ejemplo: objetivo en tile (puedes adaptar para usar coordenadas si lo agregas al JSON)
    #map
    mapa = Mapa("json_files/city_map.json", tile_size=25, top_bar_height=constants.TOP_BAR_HEIGHT)
    #HUD

    screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
    pygame.display.set_caption("Courier Quest")



    character = Character(0,0, tile_size=25, screen=screen, top_bar_height=constants.TOP_BAR_HEIGHT)

    # Stack para guardar posiciones previas
    move_stack = Stack()

    clock = pygame.time.Clock()
    run = True
    # --- Tiempo de juego ---
    tiempo_inicio = pygame.time.get_ticks()

    while run:
        #control frame rate
        clock.tick(constants.FPS)

        # --- Comprobar tiempo ---
        tiempo_actual = (pygame.time.get_ticks() - tiempo_inicio) / 1000
        if tiempo_actual >= tiempo_limite:
            show_game_over(screen, reason="Tiempo agotado")
            run = False
            continue

        # Manejo de eventos y movimiento
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if character.resistencia > 0:
                    if event.key == pygame.K_LEFT:
                        move_stack.push((character.tile_x, character.tile_y))
                        character.movement(-1, 0, mapa)
                    elif event.key == pygame.K_RIGHT:
                        move_stack.push((character.tile_x, character.tile_y))
                        character.movement(1, 0, mapa)
                    elif event.key == pygame.K_UP:
                        move_stack.push((character.tile_x, character.tile_y))
                        character.movement(0, -1, mapa)
                    elif event.key == pygame.K_DOWN:
                        move_stack.push((character.tile_x, character.tile_y))
                        character.movement(0, 1, mapa)
                    elif event.key == pygame.K_z:
                        prev_pos = move_stack.pop()
                        if prev_pos:
                            character.tile_x, character.tile_y = prev_pos
                            character.shape.center = (
                                character.tile_x * character.tile_size + character.tile_size // 2,
                                character.tile_y * character.tile_size + character.tile_size // 2 + constants.TOP_BAR_HEIGHT
                            )

        # --- Recuperar resistencia SOLO cuando no hay teclas presionadas ---
        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            character.recuperar_resistencia(1 / constants.FPS)

        # --- Dibujo de pantalla ---
        screen.fill((0, 0, 0))
        mapa.dibujar(screen)
        character.draw(screen)
        tiempo_restante = max(0, int(tiempo_limite - tiempo_actual))
        draw_hud(screen, character, tiempo_restante=tiempo_restante, objetivo_dinero=objetivo_valor)
        pygame.display.flip()

        # --- Comprobar si llegó a la meta de dinero ---
        if getattr(character, 'score', 0) >= objetivo_valor:
            show_victory(screen)
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()