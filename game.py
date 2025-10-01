
import pygame
import constants
from character import Character
from job_loader import load_jobs_with_accessible_points
from job_manager import JobManager
from map import Map
from stack import Stack
import api
import pickle
import os
from UI import UI
from weather import Weather
from save_data import SaveData


class CourierQuestGame:
    def __init__(self):
        self.init_pygame()
        self.load_resources()
        self.running = True
        self.show_inventory = False
        self.inventory_order = None
        self.pending_job = None
        self.show_job_decision = False
        self.job_decision_message = ""
        self.move_stack = Stack()
        self.first_frame = True
        self.tiempo_inicio = None
        self.tiempo_juego_acumulado = 0  # Tiempo acumulado solo cuando no está pausado
        self.tiempo_pausa_inicio = None
        self.last_deadline_penalty = False  
        self.paused = False
        self.save_system = SaveData()  # Inicializar sistema de guardado

    # Método de carga eliminado
    
    def pause_menu(self):
        self.tiempo_pausa_inicio = pygame.time.get_ticks()
        while self.paused:
            self.hud.show_pause_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.paused = False
                        if self.tiempo_pausa_inicio is not None:
                            pausa_duracion = pygame.time.get_ticks() - self.tiempo_pausa_inicio
                            self.tiempo_inicio += pausa_duracion
                            self.tiempo_pausa_inicio = None
                    elif event.key == pygame.K_g:  # Guardar partida
                        if self.save_game():
                            print("¡Juego guardado exitosamente!")
                        else:
                            print("Error al guardar el juego")
                    elif event.key == pygame.K_q:
                        self.running = False
                        self.paused = False

    def get_tiempo_juego_acumulado(self):
        """Devuelve el tiempo de juego acumulado."""
        return getattr(self, 'tiempo_juego_acumulado', 0)
    
    def get_tiempo_limite(self):
        """Devuelve el tiempo límite del juego."""
        return getattr(self, 'tiempo_limite', 120)
    
    def get_objetivo_valor(self):
        """Devuelve el valor objetivo del juego."""
        return getattr(self, 'objetivo_valor', None)
    
    def get_last_deadline_penalty(self):
        """Devuelve si se aplicó la última penalización de deadline."""
        return getattr(self, 'last_deadline_penalty', False)
    
    def get_show_inventory(self):
        """Devuelve si se muestra el inventario."""
        return getattr(self, 'show_inventory', False)
    
    def get_show_job_decision(self):
        """Devuelve si se muestra la decisión de trabajo."""
        return getattr(self, 'show_job_decision', False)
    
    def get_job_decision_message(self):
        """Devuelve el mensaje de decisión de trabajo."""
        return getattr(self, 'job_decision_message', "")
    
    def get_job_manager(self):
        """Devuelve el job manager."""
        return getattr(self, 'job_manager', None)
    
    def get_weather(self):
        """Devuelve el objeto weather."""
        return getattr(self, 'weather', None)

    def create_current_game_state(self):
        """
        Crea el estado actual del juego para guardarlo
        """
        # Datos del personaje usando métodos getter
        character_data = {
            "tile_x": self.character.get_tile_x(),
            "tile_y": self.character.get_tile_y(),
            "reputacion": self.character.get_reputacion(),
            "resistencia": self.character.get_resistencia(),
            "peso_total": self.character.get_peso_total(),
            "score": self.character.get_score(),
            "entregas_sin_penalizacion": self.character.get_entregas_sin_penalizacion(),
            "racha_bonus_aplicado": self.character.get_racha_bonus_aplicado(),
            "primera_tardanza_aplicada": self.character.get_primera_tardanza_aplicada()
        }
        
        # Datos generales del juego usando métodos getter
        game_data = {
            "tiempo_juego_acumulado": self.get_tiempo_juego_acumulado(),
            "tiempo_limite": self.get_tiempo_limite(),
            "objetivo_valor": self.get_objetivo_valor(),
            "last_deadline_penalty": self.get_last_deadline_penalty(),
            "show_inventory": self.get_show_inventory(),
            "show_job_decision": self.get_show_job_decision(),
            "job_decision_message": self.get_job_decision_message()
        }
        
        # Datos del inventario usando métodos getter
        inventario = self.character.get_inventario()
        inventory_data = {
            "max_weight": inventario.get_max_weight() if inventario else 0,
            "current_weight": inventario.get_current_weight() if inventario else 0,
            "jobs": []
        }
        
        # Intentar obtener los jobs del inventario de manera segura
        try:
            if inventario:
                jobs = inventario.get_jobs()
                inventory_data["jobs"] = [job.__dict__ for job in jobs] if jobs else []
        except (AttributeError, TypeError):
            inventory_data["jobs"] = []
        
        # Datos de trabajos activos usando métodos getter
        job_data = {
            "available_jobs": []
        }
        
        # Intentar obtener los jobs del job_manager de manera segura
        try:
            job_manager = self.get_job_manager()
            if job_manager and hasattr(job_manager, 'jobs'):
                job_data["available_jobs"] = [job.__dict__ for job in job_manager.jobs]
        except (AttributeError, TypeError):
            job_data["available_jobs"] = []
        
        # Datos del mapa usando métodos getter
        map_data = {
            "current_position": (
                self.character.get_tile_x(),
                self.character.get_tile_y()
            )
        }
        
        # Datos del clima usando métodos getter
        weather_data = {
            "current_weather": "normal"
        }
        
        # Intentar obtener el clima de manera segura
        try:
            weather = self.get_weather()
            if weather:
                weather_data["current_weather"] = getattr(weather, 'current_weather', 'normal')
        except (AttributeError, TypeError):
            weather_data["current_weather"] = "normal"
        
        return self.save_system.create_game_state(
            character_data, game_data, inventory_data, 
            job_data, map_data, weather_data
        )

    def save_game(self, slot_number=1):
        """
        Guarda el estado actual del juego
        """
        try:
            game_state = self.create_current_game_state()
            return self.save_system.save_game(game_state, slot_number)
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    def load_game(self, slot_number=1):
        """
        Carga un juego guardado
        """
        try:
            game_state = self.save_system.load_game(slot_number)
            if game_state:
                self.restore_game_state(game_state)
                return True
            return False
        except Exception as e:
            print(f"Error al cargar: {e}")
            return False

    def restore_game_state(self, game_state):
        """
        Restaura el estado del juego desde los datos cargados
        """
        components = self.save_system.extract_game_components(game_state)
        
        # Restaurar datos del personaje
        character_data = components["character"]
        self.character.tile_x = character_data.get("tile_x", 0)
        self.character.tile_y = character_data.get("tile_y", 0)
        self.character.reputacion = character_data.get("reputacion", 70)
        self.character.resistencia = character_data.get("resistencia", 100)
        self.character.peso_total = character_data.get("peso_total", 0)
        self.character.score = character_data.get("score", 0)
        self.character.entregas_sin_penalizacion = character_data.get("entregas_sin_penalizacion", 0)
        self.character.racha_bonus_aplicado = character_data.get("racha_bonus_aplicado", False)
        self.character.primera_tardanza_aplicada = character_data.get("primera_tardanza_aplicada", False)
        
        # Actualizar posición del personaje en pantalla
        self.character.shape.center = (
            self.character.tile_x * self.character.tile_size + self.character.tile_size // 2,
            self.character.tile_y * self.character.tile_size + self.character.tile_size // 2 + self.character.top_bar_height
        )
        
        # Restaurar datos del juego
        game_data = components["game"]
        self.tiempo_juego_acumulado = game_data.get("tiempo_juego_acumulado", 0)
        self.tiempo_limite = game_data.get("tiempo_limite", 120)
        self.objetivo_valor = game_data.get("objetivo_valor", None)
        self.last_deadline_penalty = game_data.get("last_deadline_penalty", False)
        self.show_inventory = game_data.get("show_inventory", False)
        self.show_job_decision = game_data.get("show_job_decision", False)
        self.job_decision_message = game_data.get("job_decision_message", "")
        
        print("Estado del juego restaurado correctamente")


    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
        pygame.display.set_caption("Courier Quest")
        #api.api_request()

    def load_resources(self):
        self.mapa = Map("json_files/city_map.json", tile_size=20, top_bar_height=constants.TOP_BAR_HEIGHT)
        jobs_list = load_jobs_with_accessible_points("json_files/city_jobs.json", self.mapa)
        self.job_manager = JobManager(jobs_list)
        self.character = Character(0,0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
        import json
        with open("json_files/city_map.json", "r", encoding="utf-8") as f:
            map_json = json.load(f)["data"]
        self.tiempo_limite = map_json.get("max_time", 120)
        self.objetivo_valor = map_json.get("goal", None)

        self.hud = UI(self.screen)

        from weather import Weather
        self.weather = Weather("json_files/city_weather.json")


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.paused = True
                self.pause_menu()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.inventory_order = None
                elif self.show_inventory:
                    if event.key == pygame.K_d:
                        self.inventory_order = 'deadline'
                    elif event.key == pygame.K_p:
                        self.inventory_order = 'priority'
                elif self.show_job_decision and not self.show_inventory:
                    if event.key == pygame.K_a:
                        if self.character.inventario.accept_job(self.pending_job):
                            self.job_manager.remove_job(self.pending_job.id)
                            self.show_job_decision = False
                            self.pending_job = None
                            self.job_decision_message = ""
                        else:
                            self.job_decision_message = "No puedes aceptar el pedido por peso. Debes rechazarlo (N)."
                    elif event.key == pygame.K_n:
                        self.job_manager.remove_job(self.pending_job.id)
                        self.character.reputacion_cancelar_pedido()
                        self.show_job_decision = False
                        self.pending_job = None
                        self.job_decision_message = ""
                elif not self.show_job_decision and not self.show_inventory:
                    if not self.character.resistencia_exhausto:
                        if event.key == pygame.K_LEFT:
                            self.move_stack.push((self.character.tile_x, self.character.tile_y))
                            # --- PASAR weather a movement ---
                            self.character.movement(-1, 0, self.mapa, weather=self.weather)
                        elif event.key == pygame.K_RIGHT:
                            self.move_stack.push((self.character.tile_x, self.character.tile_y))
                            self.character.movement(1, 0, self.mapa, weather=self.weather)
                        elif event.key == pygame.K_UP:
                            self.move_stack.push((self.character.tile_x, self.character.tile_y))
                            self.character.movement(0, -1, self.mapa, weather=self.weather)
                        elif event.key == pygame.K_DOWN:
                            self.move_stack.push((self.character.tile_x, self.character.tile_y))
                            self.character.movement(0, 1, self.mapa, weather=self.weather)
                        elif event.key == pygame.K_z:
                            prev_pos = self.move_stack.pop()
                        elif event.key == pygame.K_z:
                            prev_pos = self.move_stack.pop()
                            if prev_pos:
                                self.character.tile_x, self.character.tile_y = prev_pos
                                self.character.shape.center = (
                                    self.character.tile_x * self.character.tile_size + self.character.tile_size // 2,
                                    self.character.tile_y * self.character.tile_size + self.character.tile_size // 2 + constants.TOP_BAR_HEIGHT
                                )
                    for job in self.character.inventario.jobs[:]:
                        if not job.is_recogido():
                            self.character.inventario.pickup_job(job, (self.character.tile_x, self.character.tile_y))
                        else:
                            self._process_dropoff_with_reputation(job)

    def _process_dropoff_with_reputation(self, job):
        """
        Procesa la entrega de un trabajo y actualiza la reputación y score según el tiempo de entrega.
        """
        entregado = self.character.inventario.deliver_job(job, (self.character.tile_x, self.character.tile_y))
        if entregado:
            # Calcular tiempo de entrega vs deadline
            import datetime
            try:
                # Obtener tiempo actual y deadline
                now = pygame.time.get_ticks()
                elapsed_seconds = int((now - self.tiempo_inicio) / 1000)
                tiempo_deadline = job.deadline.split('T')[1]
                min_deadline = int(tiempo_deadline.split(':')[0])
                sec_deadline = int(tiempo_deadline.split(':')[1])
                deadline_seconds = min_deadline * 60 + sec_deadline
                # Entrega temprana (≥20% antes)
                if elapsed_seconds <= deadline_seconds - int(0.2 * deadline_seconds):
                    self.character.reputacion_entrega_temprana()
                # Entrega a tiempo
                elif elapsed_seconds <= deadline_seconds:
                    self.character.reputacion_entrega_a_tiempo()
                # Entrega tarde
                else:
                    segundos_tarde = elapsed_seconds - deadline_seconds
                    self.character.reputacion_entrega_tarde(segundos_tarde)
            except Exception:
                self.character.reputacion_entrega_a_tiempo()
            # Multiplicador de pago por reputación
            payout = int(job.payout * self.character.reputacion_multiplicador_pago())
            self.character.score += payout

    def update_game_state(self):
        if self.tiempo_inicio is None:
            self.tiempo_inicio = pygame.time.get_ticks()
        # Calcular tiempo acumulado solo si no está pausado
        self.tiempo_juego_acumulado = pygame.time.get_ticks() - self.tiempo_inicio
        elapsed_seconds = int(self.tiempo_juego_acumulado / 1000)
        tiempo_restante = max(0, int(self.tiempo_limite - elapsed_seconds))
        if self.first_frame:
            self.job_manager.update_visible_jobs(0)
            self.first_frame = False
        else:
            self.job_manager.update_visible_jobs(elapsed_seconds)


    def update_game_state(self):
        if self.tiempo_inicio is None:
            self.tiempo_inicio = pygame.time.get_ticks()
        elapsed_seconds = int((pygame.time.get_ticks() - self.tiempo_inicio) / 1000)
        tiempo_restante = max(0, int(self.tiempo_limite - elapsed_seconds))
        if self.first_frame:
            self.job_manager.update_visible_jobs(0)
            self.first_frame = False
        else:
            self.job_manager.update_visible_jobs(elapsed_seconds)

        # Actualizar clima usando delta_time fijo
        self.weather.update(1 / constants.FPS)

        # Lógica de trabajos pendientes
        if not self.show_job_decision:
            for job in self.job_manager.visible_jobs:
                if job not in self.character.inventario.jobs:
                    release_time = int(job.release_time)
                    if elapsed_seconds >= release_time:
                        self.pending_job = job
                        self.show_job_decision = True
                        break

        # Recuperar resistencia SOLO cuando no hay teclas presionadas
        keys = pygame.key.get_pressed()
        if not self.show_job_decision:
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                self.character.recuperar_resistencia(1 / constants.FPS)
                if self.character.resistencia_exhausto and self.character.resistencia >= 30:
                    self.character.resistencia_exhausto = False

        # Eliminar trabajos cuyo deadline coincide con el timer del juego (hora y minuto)
        minutos_juego = elapsed_seconds // 60
        segundos_juego = elapsed_seconds % 60
        for job in self.character.inventario.jobs[:]:
            try:
                tiempo_deadline = job.deadline.split('T')[1]
                min_deadline = int(tiempo_deadline.split(':')[0])
                sec_deadline = int(tiempo_deadline.split(':')[1])
                if minutos_juego == min_deadline and segundos_juego == sec_deadline:
                    self.character.inventario.remove_job(job.id)
                    self.character.reputacion_expirar_paquete()
                    self.last_deadline_penalty = True
                    print(f"Job {job.id} removed due to deadline at {min_deadline}:{sec_deadline}. Current time: {minutos_juego}:{segundos_juego}")
            except Exception:
                continue

        # Pending job logic
        if not self.show_job_decision:
            for job in self.job_manager.visible_jobs:
                if job not in self.character.inventario.jobs:
                    release_time = int(job.release_time)
                    if elapsed_seconds >= release_time:
                        self.pending_job = job
                        self.show_job_decision = True
                        break

        # Recuperar resistencia SOLO cuando no hay teclas presionadas
        keys = pygame.key.get_pressed()
        if not self.show_job_decision:
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                self.character.recuperar_resistencia(1 / constants.FPS)
                if self.character.resistencia_exhausto and self.character.resistencia >= 30:
                    self.character.resistencia_exhausto = False

        # Eliminar trabajos cuyo deadline coincide con el timer del juego (hora y minuto)
        minutos_juego = elapsed_seconds // 60
        segundos_juego = elapsed_seconds % 60
        for job in self.character.inventario.jobs[:]:
            try:
                tiempo_deadline = job.deadline.split('T')[1]
                min_deadline = int(tiempo_deadline.split(':')[0])
                sec_deadline = int(tiempo_deadline.split(':')[1])
                if minutos_juego == min_deadline and segundos_juego == sec_deadline:
                    self.character.inventario.remove_job(job.id)
                    self.character.reputacion_expirar_paquete()
                    self.last_deadline_penalty = True
                    print(f"Job {job.id} removed due to deadline at {min_deadline}:{sec_deadline}. Current time: {minutos_juego}:{segundos_juego}")
            except Exception:
                continue


    def draw(self):
        self.character.update_stats()
        self.screen.fill((0, 0, 0))
        if self.show_inventory:
            self.hud.draw_inventory(self.character.inventario, order=self.inventory_order)
        else:
            self.mapa.draw_map(self.screen)
            self.character.draw(self.screen)
            tiempo_actual = self.tiempo_juego_acumulado / 1000
            tiempo_restante = max(0, int(self.tiempo_limite - tiempo_actual))
            self.hud.draw(self.character, tiempo_restante=tiempo_restante, money_objective=self.objetivo_valor,
                          reputacion=self.character.reputacion, weather=self.weather)
            if self.show_job_decision and self.pending_job:
                self.hud.draw_job_decision(self.pending_job, self.job_decision_message)
            # Mensaje visual si hubo penalización por deadline
            if self.last_deadline_penalty == True:
                font = pygame.font.SysFont(None, 32)
                msg = font.render("¡Perdiste reputación por no entregar a tiempo!", True, (255, 80, 80))
                self.screen.blit(msg, (constants.WIDTH_SCREEN//2 - 200, 100))
                self.last_deadline_penalty = False
        pygame.display.flip()

    def check_win_loss(self):
        if self.character.score >= self.objetivo_valor:
            self.hud.show_victory()
            self.running = False
        if self.character.reputacion_derrota():
            self.hud.show_game_over(reason="Reputación demasiado baja")
            self.running = False
        tiempo_actual = self.tiempo_juego_acumulado / 1000
        if tiempo_actual >= self.tiempo_limite:
            self.hud.show_game_over(reason="Tiempo agotado")
            self.running = False

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            if not self.paused:
                delta = clock.tick(constants.FPS)
                if self.tiempo_inicio is None:
                    self.tiempo_inicio = pygame.time.get_ticks()
                self.tiempo_juego_acumulado += delta
                self.update_game_state()
                self.draw()
                self.check_win_loss()
            else:
                clock.tick(constants.FPS)
        pygame.quit()

if __name__ == "__main__":
    game = CourierQuestGame()
    game.run()
