import pygame
import constants
from scoreboard import Scoreboard

class UI:
    def __init__(self, screen):
        self.screen = screen
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)
        self.font_top = pygame.font.SysFont(None, 30)
        self.font_info = pygame.font.SysFont(None, 20)
        self.font_inventory = pygame.font.SysFont(None, 26)
        # Load HUD background image (used for topbar and navbar)
        self.hud_img = pygame.image.load("sprites/hud.png").convert_alpha()
        self.hud_img_top = pygame.transform.scale(self.hud_img, (constants.WIDTH_SCREEN, constants.TOP_BAR_HEIGHT))
        self.hud_img_nav = pygame.transform.scale(self.hud_img, (constants.WIDTH_SCREEN, 55))


    def show_pause_menu(self):
        font = pygame.font.SysFont(None, 40)
        small_font = pygame.font.SysFont(None, 28)
        popup_width = 320
        popup_height = 240
        popup_x = (constants.WIDTH_SCREEN - popup_width) // 2
        popup_y = (constants.HEIGHT_SCREEN - popup_height) // 2
        hud_img = pygame.image.load("sprites/hud.png").convert_alpha()
        hud_popup = pygame.transform.scale(hud_img, (popup_width, popup_height))
        self.screen.blit(hud_popup, (popup_x, popup_y))
        title = font.render("PAUSA", True, (255, 255, 0))
        self.screen.blit(title, (popup_x + 100, popup_y + 25))
        save_text = small_font.render("[G] Guardar partida", True, (200, 255, 200))
        resume_text = small_font.render("[C] Continuar", True, (200, 200, 255))
        exit_text = small_font.render("[Q] Salir", True, (255, 100, 100))
        self.screen.blit(save_text, (popup_x + 50, popup_y + 80))
        self.screen.blit(resume_text, (popup_x + 50, popup_y + 120))
        self.screen.blit(exit_text, (popup_x + 50, popup_y + 160))
        pygame.display.flip()

    def show_game_over(self, reason="Tiempo agotado"):
        """Muestra la pantalla de Game Over con el motivo."""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 60)
        text = font.render("GAME OVER", True, (255, 0, 0))
        reason_font = pygame.font.SysFont(None, 30)
        reason_text = reason_font.render(reason, True, (255, 255, 255))
        text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 - 40))
        reason_rect = reason_text.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN // 2 + 40))
        self.screen.blit(text, text_rect)
        self.screen.blit(reason_text, reason_rect)
        pygame.display.flip()
        pygame.time.wait(2500)

    def show_victory(self, final_score, reason="¡Has llegado al objetivo!"):
        """
        Muestra la pantalla de Victoria, guarda el puntaje y muestra el scoreboard resaltando el nuevo entry si corresponde.
        """
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 60)
        text = font.render("VICTORIA", True, (0, 255, 0))
        reason_font = pygame.font.SysFont(None, 30)
        reason_text = reason_font.render(reason, True, (255, 255, 255))
        text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, 80))
        reason_rect = reason_text.get_rect(center=(constants.WIDTH_SCREEN // 2, 140))
        self.screen.blit(text, text_rect)
        self.screen.blit(reason_text, reason_rect)

        # Guardar puntaje y mostrar scoreboard

        scoreboard = Scoreboard("data/json_files/scores.json")
        highlight_idx = scoreboard.add_score(int(final_score))
        scores = scoreboard.get_scores()

        # Mostrar tabla de puntajes
        table_font = pygame.font.SysFont(None, 32)
        y_start = 200
        line_height = 40
        self.screen.blit(table_font.render("Top 5 Puntajes", True, (255,255,255)), (constants.WIDTH_SCREEN//2 - 100, y_start))
        y = y_start + 40
        for idx, entry in enumerate(scores):
            color = (255, 255, 0) if idx == highlight_idx else (255, 255, 255)
            entry_text = table_font.render(f"{idx+1}. {entry['score']}", True, color)
            self.screen.blit(entry_text, (constants.WIDTH_SCREEN//2 - 100, y))
            y += line_height

        pygame.display.flip()
        pygame.time.wait(3500)

    def show_victory_with_final_score(self, score_data):
        """
        Muestra la pantalla de victoria con detalles del puntaje final y espera hasta que el jugador presione una tecla.
        """
        # Limpiar pantalla
        self.screen.fill((0, 0, 0))

        # Fuentes
        title_font = pygame.font.SysFont(None, 60)
        detail_font = pygame.font.SysFont(None, 30)
        small_font = pygame.font.SysFont(None, 24)
        scoreboard_font = pygame.font.SysFont(None, 28)

        # Título principal
        title = title_font.render("¡VICTORIA!", True, (0, 255, 0))
        title_rect = title.get_rect(center=(constants.WIDTH_SCREEN // 2, 40))
        self.screen.blit(title, title_rect)

        # --- PRIMERA MITAD: Detalles del puntaje ---
        y_pos = 80
        line_spacing = 25

        details = [
            f"Ingresos Base: ${score_data['ingresos_base']}",
            f"Multiplicador Reputación: x{score_data['pay_mult']:.2f}",
            f"Score Base: ${score_data['score_base']}",
            f"Bonus por Tiempo: +${score_data['bonus_tiempo']}",
            "",  # Línea vacía
            f"PUNTAJE FINAL: ${score_data['final_score']}",
            "",
            f"Reputación Final: {score_data['reputacion']}/100",
            f"Tiempo Restante: {int(score_data['tiempo_restante'])}s"
        ]

        for detail in details:
            if detail == "":
                y_pos += line_spacing // 2
                continue

            if "PUNTAJE FINAL" in detail:
                color = (255, 255, 0)  # Amarillo para el puntaje final
                font = detail_font
            else:
                color = (255, 255, 255)  # Blanco para los demás
                font = small_font

            text = font.render(detail, True, color)
            text_rect = text.get_rect(center=(constants.WIDTH_SCREEN // 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos += line_spacing

        # --- SEGUNDA MITAD: Scoreboard ---
        # Guardar puntaje final en scores.json y obtener el índice destacado
        scoreboard = Scoreboard("data/json_files/scores.json")
        highlight_idx = scoreboard.add_score(int(score_data['final_score']))
        scores = scoreboard.get_scores()

        # Título del scoreboard
        scoreboard_y = constants.HEIGHT_SCREEN // 2 + 20
        scoreboard_title = detail_font.render("TOP 5 PUNTAJES", True, (255, 255, 0))
        scoreboard_title_rect = scoreboard_title.get_rect(center=(constants.WIDTH_SCREEN // 2, scoreboard_y))
        self.screen.blit(scoreboard_title, scoreboard_title_rect)

        # Mostrar top 5 scores
        scoreboard_y += 40
        for idx, entry in enumerate(scores):
            if idx >= 5:  # Solo mostrar top 5
                break

            # Destacar el nuevo score añadido
            if idx == highlight_idx:
                color = (255, 255, 0)  # Amarillo para el nuevo score
            else:
                color = (255, 255, 255)  # Blanco para los demás

            score_text = scoreboard_font.render(f"{idx+1}. ${entry['score']}", True, color)
            score_rect = score_text.get_rect(center=(constants.WIDTH_SCREEN // 2, scoreboard_y))
            self.screen.blit(score_text, score_rect)
            scoreboard_y += 30

        # Instrucciones
        instruction = small_font.render("Presiona cualquier tecla para salir", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(constants.WIDTH_SCREEN // 2, constants.HEIGHT_SCREEN - 30))
        self.screen.blit(instruction, instruction_rect)

        pygame.display.flip()

        # Esperar hasta que el jugador presione una tecla
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False

    def draw_weather(self, weather):
        """Muestra el estado actual del clima en la barra superior."""
        if not weather:
            return
        clima_text = self.font.render(
            f"Clima: {weather.current_condition}", True, (107, 40, 20)
        )
        self.screen.blit(clima_text, (475, 17))

    def draw_topbar(self, character, money_objective=None, weather= None):
        top_bar_height = constants.TOP_BAR_HEIGHT
        #Dibuja la imagen del fondo del HUD para el topbar
        self.screen.blit(self.hud_img_top, (0, 0))
        dinero_ganado = character.get_score()
        if money_objective is not None:
            score_text = self.font_top.render(f"Puntuación: ${dinero_ganado} / ${money_objective}", True, (255, 255, 255))
        else:
            score_text = self.font_top.render(f"Puntuación: ${dinero_ganado}", True, (255, 255, 255))
        text_rect = score_text.get_rect(topleft=(constants.WIDTH_SCREEN // 30 + 2, top_bar_height // 2 - 10))
        self.screen.blit(score_text, text_rect)

        if weather:
            self.draw_weather(weather)

    def draw_downbar(self, character, tiempo_restante=None, reputacion=None):
        hud_height = 55
        try:
            hud_y = self.screen.get_height() - hud_height
        except Exception:
            hud_y = constants.HEIGHT_SCREEN - hud_height
        # Draw HUD background image for navbar
        self.screen.blit(self.hud_img_nav, (0, hud_y))
        peso_actual = character.total_weight
        peso_text = self.font.render(f"Peso actual: {peso_actual}", True, (255, 255, 255))
        self.screen.blit(peso_text, (180, constants.HEIGHT_SCREEN - hud_height + 15))
        rep = reputacion if reputacion is not None else character.reputation
        if rep >= 70:
            rep_color = (0, 200, 255)
        elif rep >= 30:
            rep_color = (255, 200, 0)
        else:
            rep_color = (255, 50, 50)
        rep_text = self.font.render(f"Reputación: {rep}", True, rep_color)
        self.screen.blit(rep_text, (300, constants.HEIGHT_SCREEN - hud_height + 15))
        if tiempo_restante is not None:
            minutos = int(tiempo_restante) // 60
            segundos = int(tiempo_restante) % 60
            timer_text = self.font.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, (255, 255, 255))
        else:
            timer_text = self.font.render("Tiempo: 00:00", True, (255, 255, 255))
        self.screen.blit(timer_text, (450, constants.HEIGHT_SCREEN - hud_height + 15))
        #info_text = self.font_info.render("[Z] Deshacer movimiento", True, (255, 255, 255))
        #info_rect = info_text.get_rect(topright=(constants.WIDTH_SCREEN - 20, 10))
        #self.screen.blit(info_text, info_rect)

    def draw_resistencia(self, character):
        hud_height = 55
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
        # Reducir el tamaño del sprite de stamina
        stamina_img = pygame.transform.scale(stamina_img, (120, 40))
        x, y = 40, hud_y + 5
        self.screen.blit(stamina_img, (x, y))

    def draw_inventory(self, inventory, order=None, tiempo_limite=None, selected_job_index=0):
        # Dimensiones de la ventana pop-up
        popup_width = 600
        popup_height = 400
        popup_x = (constants.WIDTH_SCREEN - popup_width) // 2
        popup_y = (constants.HEIGHT_SCREEN - popup_height) // 2
        # Dibujar fondo negro semitransparente
        popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        popup_surface.fill((0, 0, 0, 220))  # Negro con opacidad
        self.screen.blit(popup_surface, (popup_x, popup_y))
        # Título
        title = self.font_inventory.render("Inventario de trabajos aceptados", True, (255,255,0))
        self.screen.blit(title, (popup_x + 30, popup_y + 20))
        # Orden
        if order == 'deadline':
            jobs = inventory.filter_by_deadline()
            order_text = self.font_inventory.render("Orden: Deadline (D)", True, (200,200,255))
        elif order == 'priority':
            jobs = inventory.filter_by_priority()
            order_text = self.font_inventory.render("Orden: Prioridad (P)", True, (200,255,200))
        else:
            jobs = inventory.jobs
            order_text = self.font_inventory.render("Orden: Default", True, (180,180,180))
        self.screen.blit(order_text, (popup_x + 30, popup_y + 60))

        # Listado de trabajos
        y = popup_y + 100
        max_width = popup_width - 45
        # Fuente un poco más grande para los trabajos
        small_job_font = pygame.font.SysFont(None, 22)

        for i, job in enumerate(jobs):
            # Highlight selected job
            if i == selected_job_index:
                highlight_rect = pygame.Rect(popup_x + 25, y - 2, popup_width - 50, 26)
                pygame.draw.rect(self.screen, (50, 50, 100), highlight_rect)

            # Calcular deadline mostrado como (tiempo_limite - deadline_job)
            deadline_display = str(job.deadline)
            if tiempo_limite is not None:
                try:
                    time_part = str(job.deadline).split('T')[1] if 'T' in str(job.deadline) else str(job.deadline)
                    mins = int(time_part.split(':')[0])
                    secs = int(time_part.split(':')[1])
                    deadline_secs = mins * 60 + secs
                    restante = max(0, int(tiempo_limite) - deadline_secs)
                    mm = restante // 60
                    ss = restante % 60
                    deadline_display = f"{mm:02d}:{ss:02d}"
                except Exception:
                    # Si falla el parseo, dejar el valor original
                    deadline_display = str(job.deadline)

            # Mostrar todos los datos del trabajo junto al deadline calculado
            text_raw = f"ID: {job.id} | Pago: ${job.payout} | Peso: {job.weight} | Prioridad: {job.priority} | Deadline: {deadline_display}"
            job_color = (255, 255, 0) if i == selected_job_index else (255, 255, 255)
            job_text = small_job_font.render(text_raw, True, job_color)
            self.screen.blit(job_text, (popup_x + 30, y))
            y += 28  # Ajusta la separación para la nueva fuente

        # Controles de navegación e información
        info_text = self.font_inventory.render("↑↓: Navegar | D: Deadline | P: Prioridad | C: Cancelar trabajo | I: Cerrar", True, (255,200,100))
        self.screen.blit(info_text, (popup_x + 20, y+20))

    def draw_job_decision(self, pending_job, job_decision_message=None):
        rect_width = 480
        rect_height = 110
        rect_x = (constants.WIDTH_SCREEN - rect_width) // 2
        rect_y = (constants.HEIGHT_SCREEN - rect_height) // 2 - 25
        #Dibuja el sprite del HUD como fondo de la ventana de decisión
        hud_decision_img = pygame.transform.scale(self.hud_img, (rect_width, rect_height))
        self.screen.blit(hud_decision_img, (rect_x, rect_y))
        if not pending_job:
            return
        font = pygame.font.SysFont(None, 22)
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

    def draw(self, character, tiempo_restante=None, money_objective=None, reputacion=None, weather= None):
        # --- Dibujar puntos de pickup y dropoff de los trabajos aceptados ---
        for job in character.inventory.jobs:
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
        self.draw_topbar(character, money_objective, weather)
        self.draw_downbar(character, tiempo_restante, reputacion)
        self.draw_resistencia(character)