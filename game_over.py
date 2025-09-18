import pygame
import constants

def show_game_over(screen, reason="Tiempo agotado"):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 72)
    text = font.render("GAME OVER", True, (255, 0, 0))
    reason_font = pygame.font.SysFont(None, 36)
    reason_text = reason_font.render(reason, True, (255, 255, 255))
    text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 - 40))
    reason_rect = reason_text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 + 40))
    screen.blit(text, text_rect)
    screen.blit(reason_text, reason_rect)
    pygame.display.flip()
    pygame.time.wait(2500)  # Espera 2.5 segundos antes de cerrar
