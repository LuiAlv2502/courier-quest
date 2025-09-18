
import pygame

import constants


def draw_hud(screen, character, tiempo_restante=None, objetivo_dinero=None):

    hud_height = 60
    # --- Top bar ---
    top_bar_height = constants.TOP_BAR_HEIGHT
    pygame.draw.rect(screen, (60, 60, 60), (0, 0, constants.WIDTH_SCREEN, top_bar_height))
    # --- HUD inferior ---
    from mapa import Mapa
    # Si el mapa está disponible, coloca el HUD justo debajo del último tile
    try:
        hud_y = character.screen.get_height() - hud_height
        if hasattr(character, 'tile_size') and hasattr(character, 'top_bar_height'):
            from mapa import Mapa
            # Buscar instancia de mapa en globals
            mapa = None
            for obj in globals().values():
                if isinstance(obj, Mapa):
                    mapa = obj
                    break
            if mapa:
                hud_y = mapa.get_hud_bottom_y()
    except Exception:
        hud_y = constants.HEIGHT_SCREEN - hud_height
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

    # Peso
    peso_text = font.render(f"Peso: {character.peso_total}", True, (255, 255, 255))
    screen.blit(peso_text, (250, constants.HEIGHT_SCREEN - hud_height + 18))

    # Reputación
    rep_text = font.render(f"Reputación: {character.reputacion}", True, (255, 255, 255))
    screen.blit(rep_text, (400, constants.HEIGHT_SCREEN - hud_height + 18))

    # No mostrar dinero en la barra inferior

    # Tiempo en minutos:segundos
    if tiempo_restante is not None:
        minutos = int(tiempo_restante) // 60
        segundos = int(tiempo_restante) % 60
        timer_text = font.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, (255, 255, 255))
    else:
        timer_text = font.render("Tiempo: 00:00", True, (255, 255, 255))
    screen.blit(timer_text, (600, constants.HEIGHT_SCREEN - hud_height + 18))

# --- Puntuación centrada en la parte superior ---

    # --- Dinero ganado y meta centrados en la parte superior ---
    font_top = pygame.font.SysFont(None, 36)
    dinero_ganado = getattr(character, 'score', 0)
    if objetivo_dinero is not None:
        score_text = font_top.render(f"Dinero: ${dinero_ganado} / ${objetivo_dinero}", True, (255, 255, 255))
    else:
        score_text = font_top.render(f"Dinero: ${dinero_ganado}", True, (255, 255, 255))
    text_rect = score_text.get_rect(center=(constants.WIDTH_SCREEN // 2, top_bar_height // 2))
    screen.blit(score_text, text_rect)

    # --- Tiempo restante y objetivo ---
    # (El tiempo restante ya no se muestra en la parte inferior izquierda)
    # Quitar meta y perder de la esquina superior izquierda

    # --- Control de devolver en la esquina derecha ---
    font_info = pygame.font.SysFont(None, 24)
    info_text = font_info.render("[Z] Deshacer movimiento", True, (200, 200, 0))
    info_rect = info_text.get_rect(topright=(constants.WIDTH_SCREEN - 20, 10))
    screen.blit(info_text, info_rect)