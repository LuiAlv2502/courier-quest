import pygame
import character
import constants

class HUD:
    def show_game_over(self, reason="Tiempo agotado"):
        """Muestra la pantalla de Game Over con el motivo."""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        reason_font = pygame.font.SysFont(None, 36)
        reason_text = reason_font.render(reason, True, (255, 255, 255))
        text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 - 40))
        reason_rect = reason_text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 + 40))
        self.screen.blit(text, text_rect)
        self.screen.blit(reason_text, reason_rect)
        pygame.display.flip()
        pygame.time.wait(2500)

    def show_victory(self, reason="¡Has llegado al objetivo!"):
        """Muestra la pantalla de Victoria con el motivo."""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 72)
        text = font.render("VICTORIA", True, (0, 255, 0))
        reason_font = pygame.font.SysFont(None, 36)
        reason_text = reason_font.render(reason, True, (255, 255, 255))
        text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 - 40))
        reason_rect = reason_text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 + 40))
        self.screen.blit(text, text_rect)
        self.screen.blit(reason_text, reason_rect)
        pygame.display.flip()
        pygame.time.wait(2500)
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.font_top = pygame.font.SysFont(None, 36)
        self.font_info = pygame.font.SysFont(None, 24)
        self.font_inventory = pygame.font.SysFont(None, 32)
    # Load HUD background image (used for topbar and navbar)
        self.hud_img = pygame.image.load("sprites/hud.png").convert_alpha()
        self.hud_img_top = pygame.transform.scale(self.hud_img, (constants.WIDTH_SCREEN, constants.TOP_BAR_HEIGHT))
        self.hud_img_nav = pygame.transform.scale(self.hud_img, (constants.WIDTH_SCREEN, 60))

    def draw_topbar(self, character, money_objective=None):
        top_bar_height = constants.TOP_BAR_HEIGHT
        # Draw HUD background image for topbar
        self.screen.blit(self.hud_img_top, (0, 0))
        dinero_ganado = character.get_score()
        if money_objective is not None:
            score_text = self.font_top.render(f"Puntuación: ${dinero_ganado} / ${money_objective}", True, (255, 255, 255))
        else:
            score_text = self.font_top.render(f"Puntuación: ${dinero_ganado}", True, (255, 255, 255))
        text_rect = score_text.get_rect(topleft=(constants.WIDTH_SCREEN // 2 + 30, top_bar_height // 2 - 10))
        self.screen.blit(score_text, text_rect)

    def draw_downbar(self, character, tiempo_restante=None, reputacion=None):
        hud_height = 60
        try:
            hud_y = self.screen.get_height() - hud_height
        except Exception:
            hud_y = constants.HEIGHT_SCREEN - hud_height
        # Draw HUD background image for navbar
        self.screen.blit(self.hud_img_nav, (0, hud_y))
        peso_actual = character.peso_total
        peso_text = self.font.render(f"Peso actual: {peso_actual}", True, (255, 255, 255))
        self.screen.blit(peso_text, (250, constants.HEIGHT_SCREEN - hud_height + 18))
        rep = reputacion if reputacion is not None else character.reputacion
        if rep >= 70:
            rep_color = (0, 200, 255)
        elif rep >= 30:
            rep_color = (255, 200, 0)
        else:
            rep_color = (255, 50, 50)
        rep_text = self.font.render(f"Reputación: {rep}", True, rep_color)
        self.screen.blit(rep_text, (400, constants.HEIGHT_SCREEN - hud_height + 18))
        if tiempo_restante is not None:
            minutos = int(tiempo_restante) // 60
            segundos = int(tiempo_restante) % 60
            timer_text = self.font.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, (255, 255, 255))
        else:
            timer_text = self.font.render("Tiempo: 00:00", True, (255, 255, 255))
        self.screen.blit(timer_text, (600, constants.HEIGHT_SCREEN - hud_height + 18))
        #info_text = self.font_info.render("[Z] Deshacer movimiento", True, (255, 255, 255))
        #info_rect = info_text.get_rect(topright=(constants.WIDTH_SCREEN - 20, 10))
        #self.screen.blit(info_text, info_rect)

    def draw_resistencia(self, character):
        hud_height = 60
        try:
            hud_y = self.screen.get_height() - hud_height
        except Exception:
            hud_y = constants.HEIGHT_SCREEN - hud_height
        # Si la resistencia es 0 o menos, mostrar siempre stamina_0
        if character.resistencia == 0:
            sprite_index = 0
        else:
            stamina_val = max(0, min(100, int(character.resistencia)))
            sprite_index = stamina_val // 10
            #si el stamina val es menor a 10 y mayor a 0, forzar a 1
            if sprite_index < 1:
                sprite_index = 1
        sprite_path = f"sprites/stamina/stamina_{sprite_index}.png"
        stamina_img = pygame.image.load(sprite_path).convert_alpha()
        # Limitar el ancho a 100 px, mantener la altura original del sprite

        stamina_img = pygame.transform.scale(stamina_img, (145, 48))
        x, y = 50, hud_y + 5
        self.screen.blit(stamina_img, (x, y))

    def draw_inventory(self, inventory, order=None):
        title = self.font_inventory.render("Inventario de trabajos aceptados", True, (255,255,0))
        self.screen.blit(title, (50, 50))
        if order == 'deadline':
            jobs = inventory.filter_by_deadline()
            order_text = self.font_inventory.render("Orden: Deadline (D)", True, (200,200,255))
        elif order == 'priority':
            jobs = inventory.filter_by_priority()
            order_text = self.font_inventory.render("Orden: Prioridad (P)", True, (200,255,200))
        else:
            jobs = inventory.jobs
            order_text = self.font_inventory.render("Orden: Default", True, (180,180,180))
        self.screen.blit(order_text, (50, 90))
        y = 130
        max_width = constants.WIDTH_SCREEN - 100
        for job in jobs:
            text_raw = f"ID: {job.id} | Pago: ${job.payout} | Peso: {job.weight} | Prioridad: {job.priority} | Deadline: {job.deadline}"
            job_text = self.font_inventory.render(text_raw, True, (255,255,255))
            if job_text.get_width() > max_width:
                avg_char_width = job_text.get_width() / len(text_raw)
                max_chars = int(max_width / avg_char_width)
                text_raw = text_raw[:max_chars-3] + '...'
                job_text = self.font_inventory.render(text_raw, True, (255,255,255))
            self.screen.blit(job_text, (50, y))
            y += 40
        info_text = self.font_inventory.render("Presiona D para deadline, P para prioridad, I para cerrar", True, (255,200,100))
        self.screen.blit(info_text, (50, y+20))

    def draw_job_decision(self, pending_job, job_decision_message=None):
        rect_width = 600
        rect_height = 130
        rect_x = (constants.WIDTH_SCREEN - rect_width) // 2
        rect_y = (constants.HEIGHT_SCREEN - rect_height) // 2 - 25
        # Draw HUD sprite as background for decision window
        hud_decision_img = pygame.transform.scale(self.hud_img, (rect_width, rect_height))
        self.screen.blit(hud_decision_img, (rect_x, rect_y))
        if not pending_job:
            return
        font = pygame.font.SysFont(None, 32)
        job_text = font.render(f"Pedido: {pending_job.id} | Pago: ${pending_job.payout} | Peso: {pending_job.weight} | Prioridad: {pending_job.priority}", True, (255,255,255))
        rect = job_text.get_rect(center=(constants.WIDTH_SCREEN//2, constants.HEIGHT_SCREEN//2 - 40))
        self.screen.blit(job_text, rect)
        info_text = font.render("[A] Aceptar   [N] Rechazar", True, (0,0,0))
        info_rect = info_text.get_rect(center=(constants.WIDTH_SCREEN//2, constants.HEIGHT_SCREEN//2))
        self.screen.blit(info_text, info_rect)
        if job_decision_message:
            msg_text = font.render(job_decision_message, True, (255,100,100))
            msg_rect = msg_text.get_rect(center=(constants.WIDTH_SCREEN//2, constants.HEIGHT_SCREEN//2 + 40))
            self.screen.blit(msg_text, msg_rect)

    def draw(self, character, tiempo_restante=None, money_objective=None, reputacion=None):
        # --- Dibujar puntos de pickup y dropoff de los trabajos aceptados ---
        for job in character.inventario.jobs:
            # Solo mostrar pickup si no ha sido recogido
            if not job.is_recogido():
                px, py = job.pickup
                pickup_pos = (px * character.tile_size + character.tile_size // 2,
                             py * character.tile_size + character.tile_size // 2 + constants.TOP_BAR_HEIGHT)
                pygame.draw.circle(self.screen, (0, 120, 255), pickup_pos, character.tile_size // 3)
            # Dropoff: naranja (si ya fue recogido)
            if job.is_recogido():
                dx, dy = job.dropoff
                dropoff_pos = (dx * character.tile_size + character.tile_size // 2,
                              dy * character.tile_size + character.tile_size // 2 + constants.TOP_BAR_HEIGHT)
                pygame.draw.circle(self.screen, (255, 140, 0), dropoff_pos, character.tile_size // 3)
        self.draw_topbar(character, money_objective)
        self.draw_downbar(character, tiempo_restante, reputacion)
        self.draw_resistencia(character)