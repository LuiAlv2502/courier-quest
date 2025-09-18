import pygame
import constants

def show_victory(screen, reason="¡Has llegado al objetivo!"):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 72)
    text = font.render("VICTORIA", True, (0, 255, 0))
    reason_font = pygame.font.SysFont(None, 36)
    reason_text = reason_font.render(reason, True, (255, 255, 255))
    text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 - 40))
    reason_rect = reason_text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 + 40))
    screen.blit(text, text_rect)
    screen.blit(reason_text, reason_rect)
    pygame.display.flip()
    pygame.time.wait(2500)
