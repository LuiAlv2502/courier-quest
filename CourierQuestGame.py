# game.py
# Archivo principal de lógica del juego Courier Quest
# Contiene la clase CourierQuestGame y todos los métodos para gestionar el ciclo de juego, guardado, carga, eventos y lógica principal.
import heapq

import pygame  # Librería para gráficos y eventos

import api
import constants  # Constantes globales del juego
from character import Character  # Clase del personaje principal
from job_loader import load_jobs  # Carga de trabajos desde JSON
from job_manager import JobManager  # Gestión de trabajos disponibles y visibles
from map import Map  # Clase para el mapa de la ciudad
from stack import Stack  # Pila para movimientos del personaje (deshacer)
from UI import UI  # Interfaz de usuario (HUD, menús)
from SaveData import SaveData  # Guardado y carga de partidas
import sys  # Para sys.exit()
import json


class CourierQuestGame:
    def __init__(self, load_saved_game=False, saved_game_state=None, use_plain_jobs=False):
        """
        Constructor principal del juego. Inicializa Pygame, variables de estado, recursos y carga partida si corresponde.
        """
        self.init_pygame()  # Inicializa ventana y entorno gráfico
        self.running = True  # Controla el bucle principal
        self.show_inventory = False  # Muestra/oculta inventario
        self.inventory_order = None  # Orden de inventario (por deadline o prioridad)
        self.selected_job_index = 0  # Índice del trabajo seleccionado en el inventario
        self.pending_job = None  # Trabajo pendiente de aceptar/rechazar
        self.show_job_decision = False  # Muestra menú de decisión de trabajo
        self.job_decision_message = ""  # Mensaje de decisión de trabajo
        self.move_stack = Stack()  # Pila para deshacer movimientos
        self.first_frame = True  # Indica si es el primer frame (para trabajos visibles)
        self.tiempo_inicio = None  # Marca de tiempo de inicio de partida
        self.tiempo_juego_acumulado = 0  # Tiempo acumulado jugado (en ms)
        self.tiempo_pausa_inicio = None  # Marca de tiempo al pausar
        self.last_deadline_penalty = False  # Indica si hubo penalización reciente
        self.paused = False  # Estado de pausa
        self.save_system = SaveData()  # Sistema de guardado/carga

        # Nueva bandera para elegir cómo cargar los trabajos
        self.use_plain_jobs = use_plain_jobs

        if load_saved_game and saved_game_state is not None:
            self.load_resources(minimal=True)
            # Crea un personaje "vacío" antes de restaurar el estado
            self.character = Character(0, 0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
            self.restore_game_state(saved_game_state)
        else:
            self.load_resources()

    def init_pygame(self):
        """
        Inicializa Pygame y la ventana principal del juego.
        """
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('song/persona3.mp3')
        pygame.mixer.music.set_volume(0.09)
        pygame.mixer.music.play(loops=-1)
        self.screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
        pygame.display.set_caption("Courier Quest")
        #api.api_request()
    
    def pause_menu(self):
        """
        Muestra el menú de pausa y gestiona las opciones: continuar, guardar o salir.
        """
        self.tiempo_pausa_inicio = pygame.time.get_ticks()
        while self.paused:
            self.hud.show_pause_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Cerrar el juego completamente al presionar la X
                    self.running = False
                    self.paused = False
                    return
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
                        return
            # Si en cualquier momento self.running es False, salir del menú de pausa
            if not self.running:
                return

    def save_game(self, slot_number=1):
        """
        Guarda el estado actual del juego en un archivo binario usando SaveData.
        """
        try:
            game_state = self.create_current_game_state()
            return self.save_system.save_game(game_state, slot_number)
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    def load_game(self, slot_number=1):
        """
        Carga un juego guardado desde un archivo binario usando SaveData.
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
        Restaura el estado del juego desde los datos cargados (personaje, inventario, trabajos, tiempo, etc).
        """
        components = self.save_system.extract_game_components(game_state)

        self._restore_game_data(components["game"])
        self._restore_character_data(components["character"])
        self._restore_inventory_data(components.get("inventory", {}))
        self._restore_job_manager_data(components.get("jobs", {}))
        # self._filter_accepted_jobs()

        # Resetear cualquier trabajo pendiente mostrado por error
        self.pending_job = None
        print("Estado del juego restaurado correctamente")

    def _restore_game_data(self, game_data):
        """Restaura los datos generales del juego (tiempo, objetivos, etc.)"""
        self.tiempo_juego_acumulado = game_data.get("tiempo_juego_acumulado", 0)
        self.tiempo_limite = game_data.get("tiempo_limite", 120)
        self.objetivo_valor = game_data.get("objetivo_valor", None)
        self.last_deadline_penalty = game_data.get("last_deadline_penalty", False)
        self.show_inventory = game_data.get("show_inventory", False)
        self.show_job_decision = game_data.get("show_job_decision", False)
        self.job_decision_message = game_data.get("job_decision_message", "")

        # Ajustar el inicio del tiempo para que el cronómetro continúe donde se guardó
        self._adjust_game_time()

    def _adjust_game_time(self):
        """Ajusta el tiempo de inicio del juego para continuar desde donde se guardó"""
        try:
            now_ms = pygame.time.get_ticks()
            # tiempo_juego_acumulado está en milisegundos
            self.tiempo_inicio = now_ms - int(self.tiempo_juego_acumulado)
        except Exception:
            # En caso de algún fallo, reiniciar el inicio para evitar crasheos
            self.tiempo_inicio = pygame.time.get_ticks()

    def _restore_character_data(self, character_data):
        """Restaura los datos del personaje (posición, estadísticas, etc.)"""
        self.character.tile_x = character_data.get("tile_x", 0)
        self.character.tile_y = character_data.get("tile_y", 0)
        self.character.reputation = character_data.get("reputacion", 70)
        self.character.resistencia = character_data.get("resistencia", 100)
        self.character.peso_total = character_data.get("peso_total", 0)
        self.character.score = character_data.get("score", 0)
        self.character.entregas_sin_penalizacion = character_data.get("entregas_sin_penalizacion", 0)
        self.character.racha_bonus_aplicado = character_data.get("racha_bonus_aplicado", False)
        self.character.primera_tardanza_aplicada = character_data.get("primera_tardanza_aplicada", False)
        
        # Actualizar posición del personaje en pantalla
        self._update_character_screen_position()

    def _update_character_screen_position(self):
        """Actualiza la posición visual del personaje en pantalla"""
        self.character.shape.center = (
            self.character.tile_x * self.character.tile_size + self.character.tile_size // 2,
            self.character.tile_y * self.character.tile_size + self.character.tile_size // 2 + self.character.top_bar_height
        )

    def _restore_inventory_data(self, inventory_data):
        """Restaura los datos del inventario (trabajos aceptados y recogidos)"""
        from job import Job

        jobs_data = inventory_data.get("jobs", [])
        picked_jobs_data = inventory_data.get("picked_jobs", [])

        # Cargar todos los trabajos
        self.character.inventario.jobs = [Job.from_dict(j) for j in jobs_data]

        # Cargar trabajos recogidos (si existe la información)
        if picked_jobs_data:
            self.character.inventario.picked_jobs = [Job.from_dict(j) for j in picked_jobs_data]
        else:
            # Compatibilidad con guardados antiguos: reconstruir picked_jobs desde jobs
            self.character.inventario.picked_jobs = [job for job in self.character.inventario.jobs if job.is_recogido()]

    def _restore_job_manager_data(self, job_data):
        """Restaura los datos del gestor de trabajos (cola de prioridad y trabajos visibles)"""


        pending_jobs = self._load_pending_jobs(job_data)
        visible_jobs = self._load_visible_jobs(job_data)

        # Crear JobManager con trabajos pendientes
        if pending_jobs or visible_jobs:
            self.job_manager = JobManager(pending_jobs)
            self.job_manager.visible_jobs = visible_jobs

    def _load_pending_jobs(self, job_data):
        """Carga trabajos pendientes desde datos guardados (soporta múltiples formatos)"""
        from job import Job
        pending_jobs = []

        # Cargar desde el nuevo formato (pending_jobs)
        for j in job_data.get("pending_jobs", []):
            job = Job.from_dict(j)
            job.release_time = self._get_release_time_from_data(j)
            pending_jobs.append(job)

        # Compatibilidad: cargar desde formatos antiguos
        for j in job_data.get("available_jobs", []):
            job = Job.from_dict(j)
            job.release_time = self._get_release_time_from_data(j)
            pending_jobs.append(job)

        for j in job_data.get("job_queue", []):
            job = Job.from_dict(j)
            job.release_time = self._get_release_time_from_data(j)
            pending_jobs.append(job)

        return pending_jobs

    def _load_visible_jobs(self, job_data):
        """Carga trabajos visibles desde datos guardados"""
        from job import Job
        visible_jobs = []

        for j in job_data.get("visible_jobs", []):
            job = Job.from_dict(j)
            job.release_time = self._get_release_time_from_data(j)
            visible_jobs.append(job)

        return visible_jobs

    def _get_release_time_from_data(self, job_data):
        """Extrae el tiempo de liberación desde datos guardados (soporta formatos antiguos)"""
        if "release_at" in job_data:
            return int(job_data["release_at"])
        else:
            return int(job_data.get("release_time", 0))

    # def _filter_accepted_jobs(self):
    #     """Filtra trabajos ya aceptados de la cola de prioridad y trabajos visibles"""
    #     try:
    #         accepted_ids = {job.id for job in self.character.inventario.jobs}
    #         if hasattr(self, 'job_manager') and self.job_manager:
    #             self._filter_priority_queue(accepted_ids)
    #             self._filter_visible_jobs(accepted_ids)
    #     except Exception as e:
    #         print(f"[WARN] No se pudo filtrar trabajos aceptados al restaurar: {e}")

    # def _filter_priority_queue(self, accepted_ids):
    #     """Filtra trabajos aceptados de la cola de prioridad"""
    #     new_queue = []
    #     for release_time, jid, job in self.job_manager.job_priority_queue:
    #         if jid not in accepted_ids:
    #             new_queue.append((release_time, jid, job))
    #     self.job_manager.job_priority_queue = new_queue
    #     heapq.heapify(self.job_manager.job_priority_queue)

    # def _filter_visible_jobs(self, accepted_ids):
    #     """Filtra trabajos aceptados de la lista de trabajos visibles"""
    #     self.job_manager.visible_jobs = [j for j in self.job_manager.visible_jobs if j.id not in accepted_ids]




    def load_resources(self, minimal=False):
        """
        Carga los recursos principales: mapa, trabajos, personaje, HUD y clima.
        Si minimal=True, solo carga lo esencial para restaurar una partida.
        """
        self.mapa = Map("json_files/city_map.json", tile_size=20, top_bar_height=constants.TOP_BAR_HEIGHT)
        # Elegir cargador de trabajos
        jobs_list = load_jobs("json_files/city_jobs.json")
        self.job_manager = JobManager(jobs_list)
        if not minimal:
            self.character = Character(0,0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
        with open("json_files/city_map.json", "r", encoding="utf-8") as f:
            map_json = json.load(f)["data"]
        self.tiempo_limite = map_json.get("max_time", 120)
        self.objetivo_valor = map_json.get("goal", None)
        self.hud = UI(self.screen)
        from weather import Weather
        self.weather = Weather("json_files/city_weather.json")

    def create_current_game_state(self):
        """
        Crea un diccionario con el estado actual del juego para guardarlo (personaje, inventario, trabajos, clima, etc).
        """
        return {
            "character": self.character.to_dict(),
            "game": {
                "tiempo_juego_acumulado": self._get_elapsed_seconds() * 1000,
                "tiempo_limite": self.tiempo_limite,
                "objetivo_valor": self.objetivo_valor,
                "last_deadline_penalty": self.last_deadline_penalty,
                "show_inventory": self.show_inventory,
                "show_job_decision": self.show_job_decision,
                "job_decision_message": self.job_decision_message
            },
            "inventory": {
                "jobs": [job.to_dict() for job in self.character.inventario.jobs],
                "picked_jobs": [job.to_dict() for job in self.character.inventario.picked_jobs]
            },
            "jobs": {
                "pending_jobs": [job.to_dict() for job in self.job_manager.get_pending_jobs()],
                "visible_jobs": [job.to_dict() for job in self.job_manager.visible_jobs]
            },
            "weather": self.weather.to_dict() if hasattr(self.weather, "to_dict") else {}
        }

    def handle_events(self):
        """
        Procesa los eventos de teclado y ventana: movimiento, inventario, aceptar/rechazar trabajos, pausa, etc.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Solo cerrar el juego completamente, no ir a menú ni pausar
                self.running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.paused = True
                self.pause_menu()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.inventory_order = None
                    self.selected_job_index = 0  # Reset selection when opening/closing inventory
                elif self.show_inventory:
                    # Get current job list based on order
                    if self.inventory_order == 'deadline':
                        current_jobs = self.character.inventario.filter_by_deadline()
                    elif self.inventory_order == 'priority':
                        current_jobs = self.character.inventario.filter_by_priority()
                    else:
                        current_jobs = self.character.inventario.jobs

                    if event.key == pygame.K_d:
                        self.inventory_order = 'deadline'
                        self.selected_job_index = 0  # Reset selection when changing order
                    elif event.key == pygame.K_p:
                        self.inventory_order = 'priority'
                        self.selected_job_index = 0  # Reset selection when changing order
                    elif event.key == pygame.K_UP:
                        # Navigate up in job list
                        if current_jobs:
                            self.selected_job_index = (self.selected_job_index - 1) % len(current_jobs)
                    elif event.key == pygame.K_DOWN:
                        # Navigate down in job list
                        if current_jobs:
                            self.selected_job_index = (self.selected_job_index + 1) % len(current_jobs)
                    elif event.key == pygame.K_c:
                        # Cancel selected job
                        if current_jobs and 0 <= self.selected_job_index < len(current_jobs):
                            selected_job = current_jobs[self.selected_job_index]
                            if self.character.inventario.cancel_job(selected_job.id):
                                # Apply reputation penalty for canceling
                                self.character.reputation_expirar_job()
                                # Update character stats after cancellation
                                self.character.update_stats()
                                # Adjust selected index if needed
                                if self.selected_job_index >= len(current_jobs) - 1:
                                    self.selected_job_index = max(0, len(current_jobs) - 2)
                elif self.show_job_decision and not self.show_inventory:
                    if event.key == pygame.K_a:
                        if self.pending_job and self.character.inventario.accept_job(self.pending_job):
                            self.job_manager.remove_job(self.pending_job.id)
                            self.show_job_decision = False
                            self.pending_job = None
                            self.job_decision_message = ""
                        else:
                            self.job_decision_message = "No puedes aceptar el pedido por peso. Debes rechazarlo (N)."
                    elif event.key == pygame.K_n:
                        if self.pending_job:
                            self.job_manager.remove_job(self.pending_job.id)
                        self.show_job_decision = False
                        self.pending_job = None
                        self.job_decision_message = ""
                elif not self.show_job_decision and not self.show_inventory:
                    if not self.character.resistencia_exhausto:
                        if event.key == pygame.K_LEFT:
                            self.move_stack.push((self.character.tile_x, self.character.tile_y))
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
                            if prev_pos:
                                self.character.tile_x, self.character.tile_y = prev_pos
                                self.character.shape.center = (
                                    self.character.tile_x * self.character.tile_size + self.character.tile_size // 2,
                                    self.character.tile_y * self.character.tile_size + self.character.tile_size // 2 + constants.TOP_BAR_HEIGHT
                                )
                    # Intentar recoger trabajos si corresponde
                    for job in self.character.inventario.jobs[:]:
                        if not job.is_recogido():
                            recogido = self.character.inventario.pickup_job(job, (self.character.tile_x, self.character.tile_y))
                            if recogido:
                                self.character.update_stats()
                    # Solo intentar entregar trabajos que ya estaban recogidos
                    for job in [j for j in self.character.inventario.jobs if j.is_recogido()]:
                        self._process_dropoff_with_reputacion(job)
                        self.character.update_stats()

    def _process_dropoff_with_reputacion(self, job):
        """
        Procesa la entrega de un trabajo y actualiza la reputación y score según el tiempo de entrega.
        """
        entregado = self.character.inventario.deliver_job(job, (self.character.tile_x, self.character.tile_y))
        if entregado:
            # Calcular tiempo de entrega vs deadline
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

    def _init_time_if_needed(self):
        """
        Inicializa la marca de tiempo de inicio si aún no está definida.
        """
        if self.tiempo_inicio is None:
            self.tiempo_inicio = pygame.time.get_ticks()

    def _get_elapsed_seconds(self):
        """
        Devuelve los segundos transcurridos desde el inicio de la partida.
        """
        return int((pygame.time.get_ticks() - self.tiempo_inicio) / 1000)

    def _update_visible_jobs(self, elapsed_seconds):
        """
        Actualiza la lista de trabajos visibles según el tiempo transcurrido.
        """
        if self.first_frame:
            self.job_manager.update_visible_jobs(0)
            self.first_frame = False
        else:
            self.job_manager.update_visible_jobs(elapsed_seconds)

    def _update_weather(self):
        """
        Actualiza el estado del clima (si está implementado).
        """
        self.weather.update(1 / constants.FPS)

    def _process_pending_jobs(self):
        """
        Verifica si hay trabajos listos para ser aceptados y muestra el menú de decisión si corresponde.
        """
        if not self.show_job_decision:
            # Construir un set de IDs ya aceptados para evitar comparar por instancia
            accepted_ids = {j.id for j in self.character.inventario.jobs}
            # Tomar el primer trabajo visible que no esté aceptado
            for job in self.job_manager.visible_jobs:
                if job.id not in accepted_ids:
                    self.pending_job = job
                    self.show_job_decision = True
                    break

    def _recover_stamina_if_idle(self):
        """
        Recupera la resistencia del personaje si está inactivo y no exhausto.
        """
        self.character.recuperar_resistencia()

    def _remove_expired_jobs(self, elapsed_seconds):
        """
        Elimina trabajos expirados del inventario y aplica penalización.
        """
        expired_jobs = [job for job in self.character.inventario.jobs if job.is_expired(elapsed_seconds)]
        for job in expired_jobs:
            self.character.inventario.remove_job(job)
            self.character.reputation_expirar_job()
            self.last_deadline_penalty = True

    def update_game_state(self):
        """
        Actualiza toda la lógica del juego: tiempo, trabajos, clima, resistencia, penalizaciones, etc.
        """
        self._init_time_if_needed()
        elapsed_seconds = self._get_elapsed_seconds()
        self._update_visible_jobs(elapsed_seconds)
        self._update_weather()
        self._process_pending_jobs()
        self._recover_stamina_if_idle()
        self._remove_expired_jobs(elapsed_seconds)

        # Actualizar estadísticas del personaje continuamente
        self.character.update_stats()

    def draw(self):
        """
        Dibuja todos los elementos del juego en pantalla: mapa, personaje, HUD, inventario, etc.
        """
        reputacion = self.character.reputation
        # Verifica condiciones de victoria (score objetivo) o derrota (reputación o tiempo agotado)
        if self.character.score >= self.objetivo_valor:
            # Calcular puntaje final y mostrar victoria con detalles
            score_data = self.calculate_final_score()
            self.running = False
            self.hud.show_victory_with_final_score(score_data)
        elif self.character.reputation < 20 or self._get_elapsed_seconds() >= self.tiempo_limite:
            self.running = False
            self.hud.show_game_over(reason="Reputación baja" if self.character.reputation < 20 else "Tiempo agotado")
        else:
            self.mapa.draw_map(self.screen)
            self.character.draw(self.screen)
            # Definir variables requeridas para HUD
            tiempo_restante = max(0, self.tiempo_limite - self._get_elapsed_seconds())
            money_objective = self.objetivo_valor
            # Dibuja HUD principal (topbar, downbar, resistencia, puntos de pickup/dropoff)
            self.hud.draw(self.character, tiempo_restante=tiempo_restante, money_objective=money_objective, reputacion=reputacion, weather=self.weather)
            # Si corresponde, dibuja inventario
            if self.show_inventory:
                self.hud.draw_inventory(self.character.inventario, order=self.inventory_order, tiempo_limite=self.tiempo_limite, selected_job_index=self.selected_job_index)
            # Si corresponde, dibuja menú de decisión de trabajo
            if self.show_job_decision:
                self.hud.draw_job_decision(self.pending_job, job_decision_message=self.job_decision_message)

    def check_win_loss(self):
        """
        Verifica condiciones de victoria (score objetivo) o derrota (reputación o tiempo agotado).
        """
        if self.character.score >= self.objetivo_valor:
            print("¡Has ganado!")
            self.running = False
        elif self.character.reputation < 20 or self._get_elapsed_seconds() >= self.tiempo_limite:
            print("Has perdido.")
            self.running = False

    # Métodos getter para exponer información relevante del estado del juego
    def get_tiempo_juego_acumulado(self):
        return self.tiempo_juego_acumulado

    def get_tiempo_limite(self):
        return self.tiempo_limite

    def get_objetivo_valor(self):
        return self.objetivo_valor

    def get_last_deadline_penalty(self):
        return self.last_deadline_penalty

    def get_show_inventory(self):
        return self.show_inventory

    def get_show_job_decision(self):
        return self.show_job_decision

    def get_job_decision_message(self):
        return self.job_decision_message

    def get_job_manager(self):
        return self.job_manager

    def get_weather(self):
        return self.weather

    def calculate_final_score(self):
        """
        Calcula el puntaje final según la fórmula:
        score_base = suma de pagos * pay_mult (por reputación alta)
        bonus_tiempo = +X si terminas antes del 20% del tiempo restante
        score = score_base + bonus_tiempo - penalizaciones
        """
        # Score base con multiplicador de reputación
        pay_mult = self.character.reputacion_multiplicador_pago()
        score_base = int(self.character.score * pay_mult)

        # Bonus por tiempo (si termina antes del 20% del tiempo restante)
        elapsed_seconds = self._get_elapsed_seconds()
        tiempo_restante = self.tiempo_limite - elapsed_seconds
        twenty_percent_time = self.tiempo_limite * 0.2

        bonus_tiempo = 0
        if tiempo_restante >= twenty_percent_time:
            # Bonus proporcional al tiempo restante (máximo 500 puntos)
            bonus_percentage = tiempo_restante / self.tiempo_limite
            bonus_tiempo = int(500 * bonus_percentage)

        # Penalizaciones (se pueden expandir en el futuro)

        # Score final
        final_score = score_base + bonus_tiempo

        return {
            "score_base": score_base,
            "pay_mult": pay_mult,
            "bonus_tiempo": bonus_tiempo,
            "final_score": final_score,
            "tiempo_restante": tiempo_restante,
            "reputacion": self.character.reputation,
            "ingresos_base": self.character.score
        }

    def run(self):
        """
        Bucle principal del juego: procesa eventos, actualiza lógica, dibuja y verifica condiciones de fin.
        """
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            if not self.paused:
                self.update_game_state()
                self.draw()
                self.check_win_loss()
            pygame.display.flip()
            clock.tick(constants.FPS)
        # Cerrar Pygame y el proceso completamente al salir del bucle principal
        pygame.mixer.music.stop()
        pygame.quit()

        sys.exit()
