
import pygame

import constants


def draw_hud(screen, character):
    hud_height = 60
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
    font = pygame.font.SysFont(None, 36)  # tamaño un poco más grande para destacar
    score_text = font.render(f"Puntuación: {getattr(character, 'score', 0)}", True, (0, 0, 0))

# Calculamos posición para centrar horizontalmente
    text_rect = score_text.get_rect(center=(constants.WIDTH_SCREEN // 2, 20))  # 20 píxeles desde el top
    screen.blit(score_text, text_rect)