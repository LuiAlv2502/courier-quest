from job_loader import load_jobs_with_accessible_points
from job_manager import JobManager
from job import Job
from hud import draw_inventory

import pygame 
import constants
from character import Character
import api
from mapa import Mapa
from hud import draw_hud
from stack import Stack
from game_over import show_game_over
from victory import show_victory


def main():
    # Inicializar mapa primero para pasarlo al loader
    mapa = Mapa("json_files/city_map.json", tile_size=25, top_bar_height=constants.TOP_BAR_HEIGHT)
    # Cargar trabajos con puntos accesibles usando job_loader
    jobs_list = load_jobs_with_accessible_points("json_files/city_jobs.json", mapa)
    job_manager = JobManager(jobs_list)
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
    tiempo_inicio = None

    pending_job = None
    show_job_decision = False
    job_decision_message = ""
    first_frame = True
    show_inventory = False
    inventory_order = None  # None, 'deadline', 'priority'
    while run:
        #control frame rate
        clock.tick(constants.FPS)

        # Actualizar trabajos visibles según el tiempo
        if tiempo_inicio is None:
            tiempo_inicio = pygame.time.get_ticks()
        current_time = int((pygame.time.get_ticks() - tiempo_inicio) / 1)  # segundos
        if first_frame:
            job_manager.update_visible_jobs(0)
            first_frame = False
        else:
            job_manager.update_visible_jobs(current_time)

        # Si hay un trabajo nuevo visible y no está aceptado/rechazado, mostrarlo y pausar el juego
        if not show_job_decision:
            # Solo mostrar el primer trabajo visible cuyo release_time ya se cumplió y que no esté aceptado/rechazado
            for job in job_manager.visible_jobs:
                if job not in character.inventario.jobs:
                    # Solo mostrar si el tiempo actual es mayor o igual al release_time
                    release_time = int(getattr(job, 'release_time', 0))
                    if current_time >= release_time:
                        pending_job = job
                        show_job_decision = True
                        break

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
                # Pausa y muestra inventario con I
                if event.key == pygame.K_i:
                    show_inventory = not show_inventory
                    inventory_order = None
                # Si inventario está abierto, solo permite ordenar y cerrar inventario
                elif show_inventory:
                    if event.key == pygame.K_d:
                        inventory_order = 'deadline'
                    elif event.key == pygame.K_p:
                        inventory_order = 'priority'
                # Si hay decisión de trabajo pendiente y el inventario está cerrado
                elif show_job_decision and not show_inventory:
                    if event.key == pygame.K_a:
                        # Intentar aceptar el trabajo
                        if character.inventario.accept_job(pending_job):
                            job_manager.remove_job(pending_job.id)
                            show_job_decision = False
                            pending_job = None
                            job_decision_message = ""
                        else:
                            job_decision_message = "No puedes aceptar el pedido por peso. Debes rechazarlo (N)."
                    elif event.key == pygame.K_n:
                        job_manager.remove_job(pending_job.id)
                        character.reputacion = max(0, character.reputacion - 10)  # Pierde reputación al rechazar
                        show_job_decision = False
                        pending_job = None
                        job_decision_message = ""
                # Si no hay inventario ni decisión de trabajo, el juego sigue normal
                elif not show_job_decision and not show_inventory:
                    if not character.resistencia_exhausto:
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
                    # Pickup y entrega automática desde borde si corresponde
                    for job in character.inventario.jobs[:]:
                        if not getattr(job, 'recogido', False):
                            character.inventario.pickup_job(job, (character.tile_x, character.tile_y))
                        else:
                            character.process_dropoff(job)

        # --- Recuperar resistencia SOLO cuando no hay teclas presionadas ---
        keys = pygame.key.get_pressed()
        if not show_job_decision:
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                character.recuperar_resistencia(1 / constants.FPS)
                # Actualiza la bandera solo en la recuperación
                if character.resistencia_exhausto and character.resistencia >= 30:
                    character.resistencia_exhausto = False

        # --- Dibujo de pantalla ---
        character.update_stats()  # Actualiza puntuación y peso
        screen.fill((0, 0, 0))
        if show_inventory:
            draw_inventory(screen, character.inventario, order=inventory_order)
        else:
            mapa.dibujar(screen)
            character.draw(screen)
            tiempo_restante = max(0, int(tiempo_limite - tiempo_actual))
            draw_hud(screen, character, tiempo_restante=tiempo_restante, objetivo_dinero=objetivo_valor)
            # Mostrar HUD de decisión de trabajo si corresponde
            if show_job_decision and pending_job:
                from hud import draw_job_decision
                draw_job_decision(screen, pending_job, job_decision_message)
        pygame.display.flip()

        # --- Comprobar si llegó a la meta de dinero ---
        if getattr(character, 'score', 0) >= objetivo_valor:
            show_victory(screen)
            run = False
        # --- Comprobar reputación ---
        if getattr(character, 'reputacion', 100) < 30:
            show_game_over(screen, reason="Reputación demasiado baja")
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()