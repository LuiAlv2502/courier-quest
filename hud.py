def draw_inventory(screen, inventory, order=None):
    font = pygame.font.SysFont(None, 32)
    title = font.render("Inventario de trabajos aceptados", True, (255,255,0))
    screen.blit(title, (50, 50))
    # Obtener lista ordenada si corresponde
    if order == 'deadline':
        jobs = inventory.filter_by_deadline()
        order_text = font.render("Orden: Deadline (D)", True, (200,200,255))
    elif order == 'priority':
        jobs = inventory.filter_by_priority()
        order_text = font.render("Orden: Prioridad (P)", True, (200,255,200))
    else:
        jobs = inventory.jobs
        order_text = font.render("Orden: Default", True, (180,180,180))
    screen.blit(order_text, (50, 90))
    # Mostrar cada trabajo, limitando el ancho
    y = 130
    max_width = constants.WIDTH_SCREEN - 100
    for job in jobs:
        text_raw = f"ID: {job.id} | Pago: ${job.payout} | Peso: {job.weight} | Prioridad: {job.priority} | Deadline: {job.deadline}"
        job_text = font.render(text_raw, True, (255,255,255))
        if job_text.get_width() > max_width:
            avg_char_width = job_text.get_width() / len(text_raw)
            max_chars = int(max_width / avg_char_width)
            text_raw = text_raw[:max_chars-3] + '...'
            job_text = font.render(text_raw, True, (255,255,255))
        screen.blit(job_text, (50, y))
        y += 40
    info_text = font.render("Presiona D para deadline, P para prioridad, I para cerrar", True, (255,200,100))
    screen.blit(info_text, (50, y+20))

import pygame

import character
import constants


def draw_hud(screen, character, tiempo_restante=None, objetivo_dinero=None, reputacion=None):
    # --- Dibujar puntos de pickup y dropoff de los trabajos aceptados ---
    for job in character.inventario.jobs:
        # Solo mostrar pickup si no ha sido recogido
        if not getattr(job, 'recogido', False):
            px, py = job.pickup
            pickup_pos = (px * character.tile_size + character.tile_size // 2,
                         py * character.tile_size + character.tile_size // 2 + constants.TOP_BAR_HEIGHT)
            pygame.draw.circle(screen, (0, 120, 255), pickup_pos, character.tile_size // 3)
        # Dropoff: naranja (si ya fue recogido)
        if getattr(job, 'recogido', False):
            dx, dy = job.dropoff
            dropoff_pos = (dx * character.tile_size + character.tile_size // 2,
                          dy * character.tile_size + character.tile_size // 2 + constants.TOP_BAR_HEIGHT)
            pygame.draw.circle(screen, (255, 140, 0), dropoff_pos, character.tile_size // 3)

    hud_height = 60
    # --- Top bar ---
    top_bar_height = constants.TOP_BAR_HEIGHT
    pygame.draw.rect(screen, (60, 60, 60), (0, 0, constants.WIDTH_SCREEN, top_bar_height))
    # --- HUD inferior ---
    from mapa import Mapa
    # Si el mapa está disponible, coloca el HUD justo debajo del último tile
    # Calcular hud_y correctamente, solo el cálculo dentro del try/except
    try:
        hud_y = character.screen.get_height() - hud_height
        if hasattr(character, 'tile_size') and hasattr(character, 'top_bar_height'):
            from mapa import Mapa
            mapa = None
            for obj in globals().values():
                if isinstance(obj, Mapa):
                    mapa = obj
                    break
            if mapa:
                hud_y = mapa.get_hud_bottom_y()
    except Exception:
        hud_y = constants.HEIGHT_SCREEN - hud_height
    # El resto de la función sigue fuera del try/except
    pygame.draw.rect(screen, (40, 40, 40), (0, hud_y, constants.WIDTH_SCREEN, hud_height))

    # --- Barra de resistencia ---
    max_width = 200
    bar_height = 20
    x, y = 20, hud_y + 20
    resistencia_ratio = character.resistencia / 100
    resistencia_width = int(max_width * resistencia_ratio)

    # Color dinámico (verde → rojo)
    if resistencia_ratio > 0.5:
        color = (0, 200, 0)
    elif resistencia_ratio > 0.25:
        color = (200, 200, 0)
    else:
        color = (200, 0, 0)

    pygame.draw.rect(screen, (100, 100, 100), (x, y, max_width, bar_height))  # fondo
    pygame.draw.rect(screen, color, (x, y, resistencia_width, bar_height))   # barra

    # --- Texto HUD ---
    font = pygame.font.SysFont(None, 28)

    # Peso actualizado (sumando los trabajos recogidos)
    peso_actual = character.peso_total
    peso_text = font.render(f"Peso actual: {peso_actual}", True, (255, 255, 255))
    screen.blit(peso_text, (250, constants.HEIGHT_SCREEN - hud_height + 18))

    # Reputación destacada
    rep = reputacion if reputacion is not None else getattr(character, 'reputacion', 100)
    if rep >= 70:
        rep_color = (0, 200, 255)
    elif rep >= 30:
        rep_color = (255, 200, 0)
    else:
        rep_color = (255, 50, 50)
    rep_text = font.render(f"Reputación: {rep}", True, rep_color)
    screen.blit(rep_text, (400, constants.HEIGHT_SCREEN - hud_height + 18))

    # Eliminar letras azules de los trabajos en el HUD inferior
    # Ya no se muestra la lista de trabajos aquí

    # Tiempo en minutos:segundos
    if tiempo_restante is not None:
        minutos = int(tiempo_restante) // 60
        segundos = int(tiempo_restante) % 60
        timer_text = font.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, (255, 255, 255))
    else:
        timer_text = font.render("Tiempo: 00:00", True, (255, 255, 255))
    screen.blit(timer_text, (600, constants.HEIGHT_SCREEN - hud_height + 18))

    # --- Puntuación centrada en la parte superior ---
    font_top = pygame.font.SysFont(None, 36)
    dinero_ganado = getattr(character, 'score', 0)
    if objetivo_dinero is not None:
        score_text = font_top.render(f"Puntuación: ${dinero_ganado} / ${objetivo_dinero}", True, (255, 255, 0))
    else:
        score_text = font_top.render(f"Puntuación: ${dinero_ganado}", True, (255, 255, 0))
    text_rect = score_text.get_rect(center=(constants.WIDTH_SCREEN // 2, top_bar_height // 2))
    screen.blit(score_text, text_rect)

    # --- Control de devolver en la esquina derecha ---
    font_info = pygame.font.SysFont(None, 24)
    info_text = font_info.render("[Z] Deshacer movimiento", True, (200, 200, 0))
    info_rect = info_text.get_rect(topright=(constants.WIDTH_SCREEN - 20, 10))
    screen.blit(info_text, info_rect)

def draw_job_decision(screen, pending_job, job_decision_message=None):
    rect_width = 600
    rect_height = 130
    rect_x = (constants.WIDTH_SCREEN - rect_width) // 2
    rect_y = (constants.HEIGHT_SCREEN - rect_height) // 2 - 25
    pygame.draw.rect(screen, (0, 0, 0), (rect_x, rect_y, rect_width, rect_height))
    if not pending_job:
        return
    font = pygame.font.SysFont(None, 32)
    job_text = font.render(f"Pedido: {pending_job.id} | Pago: ${pending_job.payout} | Peso: {pending_job.weight} | Prioridad: {pending_job.priority}", True, (255,255,255))
    rect = job_text.get_rect(center=(constants.WIDTH_SCREEN//2, constants.HEIGHT_SCREEN//2 - 40))
    screen.blit(job_text, rect)
    info_text = font.render("[A] Aceptar   [N] Rechazar", True, (200,200,0))
    info_rect = info_text.get_rect(center=(constants.WIDTH_SCREEN//2, constants.HEIGHT_SCREEN//2))
    screen.blit(info_text, info_rect)
    if job_decision_message:
        msg_text = font.render(job_decision_message, True, (255,100,100))
        msg_rect = msg_text.get_rect(center=(constants.WIDTH_SCREEN//2, constants.HEIGHT_SCREEN//2 + 40))
        screen.blit(msg_text, msg_rect)