
import pygame

import constants


def draw_hud(screen, character):

    hud_height = 60
    # --- Top bar ---
    top_bar_height = constants.TOP_BAR_HEIGHT
    pygame.draw.rect(screen, (60, 60, 60), (0, 0, constants.WIDTH_SCREEN, top_bar_height))
    # --- HUD inferior ---
    pygame.draw.rect(screen, (40, 40, 40), (0, constants.HEIGHT_SCREEN - hud_height, constants.WIDTH_SCREEN, hud_height))

    # --- Barra de resistencia ---
    max_width = 200
    bar_height = 20
    x, y = 20, constants.HEIGHT_SCREEN - hud_height + 20
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

    timer_text = font.render("Tiempo: 00:00", True, (255, 255, 255))
    screen.blit(timer_text, (600, constants.HEIGHT_SCREEN - hud_height + 18))

# --- Puntuación centrada en la parte superior ---
    # --- Puntuación centrada en la parte superior ---
    font_top = pygame.font.SysFont(None, 36)
    score_text = font_top.render(f"Puntuación: {getattr(character, 'score', 0)}", True, (255, 255, 255))
    text_rect = score_text.get_rect(center=(constants.WIDTH_SCREEN // 2, top_bar_height // 2))
    screen.blit(score_text, text_rect)

    # --- Control de devolver en la esquina derecha ---
    font_info = pygame.font.SysFont(None, 24)
    info_text = font_info.render("[Z] Deshacer movimiento", True, (200, 200, 0))
    info_rect = info_text.get_rect(topright=(constants.WIDTH_SCREEN - 20, 10))
    screen.blit(info_text, info_rect)