import pygame

import api
import constants
from character import Character
from job_loader import load_jobs
from job_manager import JobManager
from map import Map
from stack import Stack
from UI import UI
from SaveData import SaveData
import sys
import json
from AIController import AIController


class CourierQuestGame:
    def __init__(self, load_saved_game: bool = False, saved_game_state=None, use_plain_jobs: bool = False):
        """Constructor principal del juego."""
        self.init_pygame()
        self.running = True
        self.show_inventory = False
        self.inventory_order = None
        self.selected_job_index = 0
        self.pending_job = None
        self.show_job_decision = False
        self.job_decision_message = ""
        self.move_stack = Stack()
        self.first_frame = True
        self.tiempo_inicio = None
        self.tiempo_juego_acumulado = 0
        self.tiempo_pausa_inicio = None
        self.last_deadline_penalty = False
        self.paused = False
        self.save_system = SaveData()
        self.use_plain_jobs = use_plain_jobs

        if load_saved_game and saved_game_state is not None:
            self.load_resources(minimal=True)
            self.character = Character(0, 0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
            self.aiCharacter = Character(0, 0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
            self.restore_game_state(saved_game_state)
        else:
            self.load_resources()

    def init_pygame(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('song/persona3.mp3')
        pygame.mixer.music.set_volume(0.09)
        pygame.mixer.music.play(loops=-1)
        self.screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
        pygame.display.set_caption("Courier Quest")
        api.api_request()

    def pause_menu(self):
        self.tiempo_pausa_inicio = pygame.time.get_ticks()
        while self.paused:
            self.hud.show_pause_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
                    elif event.key == pygame.K_g:
                        if self.save_game():
                            print("¡Juego guardado exitosamente!")
                        else:
                            print("Error al guardar el juego")
                    elif event.key == pygame.K_q:
                        self.running = False
                        self.paused = False
                        return
            if not self.running:
                return

    def save_game(self, slot_number=1):
        try:
            game_state = self.create_current_game_state()
            return self.save_system.save_game(game_state, slot_number)
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    def load_game(self, slot_number=1):
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
        components = self.save_system.extract_game_components(game_state)
        self._restore_game_data(components["game"])
        self._restore_character_data(components["character"])
        self._restore_inventory_data(components.get("inventory", {}))
        self._restore_job_manager_data(components.get("jobs", {}))
        self.pending_job = None
        print("Game state restored successfully")

    def _restore_game_data(self, game_data):
        self.tiempo_juego_acumulado = game_data.get("tiempo_juego_acumulado", 0)
        self.tiempo_limite = game_data.get("tiempo_limite", 120)
        self.objetivo_valor = game_data.get("objetivo_valor", None)
        self.last_deadline_penalty = game_data.get("last_deadline_penalty", False)
        self.show_inventory = game_data.get("show_inventory", False)
        self.show_job_decision = game_data.get("show_job_decision", False)
        self.job_decision_message = game_data.get("job_decision_message", "")
        self._adjust_game_time()

    def _adjust_game_time(self):
        try:
            now_ms = pygame.time.get_ticks()
            self.tiempo_inicio = now_ms - int(self.tiempo_juego_acumulado)
        except Exception:
            self.tiempo_inicio = pygame.time.get_ticks()

    def _restore_character_data(self, character_data):
        self.character.tile_x = character_data.get("tile_x", 0)
        self.character.tile_y = character_data.get("tile_y", 0)
        self.character.reputation = character_data.get("reputacion", 70)
        self.character.resistencia = character_data.get("resistencia", 100)
        self.character.total_weight = character_data.get("peso_total", 0)
        self.character.score = character_data.get("score", 0)
        self.character.deliveres_without_penalizacion = character_data.get("entregas_sin_penalizacion", 0)
        self.character.streak_bonus_applied = character_data.get("racha_bonus_aplicado", False)
        self.character.first_job_late_aplied = character_data.get("primera_tardanza_aplicada", False)
        self._update_character_screen_position()

    def _update_character_screen_position(self):
        self.character.shape.center = (
            self.character.tile_x * self.character.tile_size + self.character.tile_size // 2,
            self.character.tile_y * self.character.tile_size + self.character.tile_size // 2 + self.character.top_bar_height
        )

    def _restore_inventory_data(self, inventory_data):
        from job import Job
        jobs_data = inventory_data.get("jobs", [])
        picked_jobs_data = inventory_data.get("picked_jobs", [])
        self.character.inventory.jobs = [Job.from_dict(j) for j in jobs_data]
        if picked_jobs_data:
            self.character.inventory.picked_jobs = [Job.from_dict(j) for j in picked_jobs_data]
        else:
            self.character.inventory.picked_jobs = [job for job in self.character.inventory.jobs if job.is_picked_up()]

    def _restore_job_manager_data(self, job_data):
        pending_jobs = self._load_pending_jobs(job_data)
        visible_jobs = self._load_visible_jobs(job_data)
        if pending_jobs or visible_jobs:
            self.job_manager = JobManager(pending_jobs)
            self.job_manager.visible_jobs = visible_jobs

    def _load_pending_jobs(self, job_data):
        from job import Job
        pending_jobs = []
        for j in job_data.get("pending_jobs", []):
            job = Job.from_dict(j)
            job.release_time = self._get_release_time_from_data(j)
            pending_jobs.append(job)
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
        from job import Job
        visible_jobs = []
        for j in job_data.get("visible_jobs", []):
            job = Job.from_dict(j)
            job.release_time = self._get_release_time_from_data(j)
            visible_jobs.append(job)
        return visible_jobs

    def _get_release_time_from_data(self, job_data):
        if "release_at" in job_data:
            return int(job_data["release_at"])
        else:
            return int(job_data.get("release_time", 0))

    def load_resources(self, minimal: bool = False):
        self.mapa = Map("data/json_files/city_map.json", tile_size=20, top_bar_height=constants.TOP_BAR_HEIGHT)
        jobs_list = load_jobs("data/json_files/city_jobs.json")
        self.job_manager = JobManager(jobs_list)
        if not minimal:
            self.character = Character(0, 0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
            # Personaje AI estático
            self.aiCharacter = Character(29, 0, tile_size=20, screen=self.screen, top_bar_height=constants.TOP_BAR_HEIGHT)
        with open("data/json_files/city_map.json", "r", encoding="utf-8") as f:
            map_json = json.load(f)["data"]
        self.tiempo_limite = map_json.get("max_time", 120)
        self.objetivo_valor = map_json.get("goal", None)
        self.hud = UI(self.screen)
        from weather import Weather
        self.weather = Weather("data/json_files/city_weather.json")

    def create_current_game_state(self):
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
                "jobs": [job.to_dict() for job in self.character.inventory.jobs],
                "picked_jobs": [job.to_dict() for job in self.character.inventory.picked_jobs]
            },
            "jobs": {
                "pending_jobs": [job.to_dict() for job in self.job_manager.get_pending_jobs()],
                "visible_jobs": [job.to_dict() for job in self.job_manager.visible_jobs]
            },
            "weather": self.weather.to_dict() if hasattr(self.weather, "to_dict") else {}
        }

    def handle_events(self):
        for job in self.aiCharacter.inventory.jobs[:]:
            if not job.is_picked_up():
                if self.aiCharacter.inventory.pickup_job(job, (self.aiCharacter.tile_x, self.aiCharacter.tile_y)):
                        self.aiCharacter.update_stats()
        for job in [j for j in self.aiCharacter.inventory.jobs if j.is_picked_up()]:
            self._process_dropoff_for(self.aiCharacter, job)
            self.aiCharacter.update_stats()
        self.handle_ai_movement()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.paused = True
                self.pause_menu()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.inventory_order = None
                    self.selected_job_index = 0
                elif self.show_inventory:
                    if self.inventory_order == 'deadline':
                        current_jobs = self.character.inventory.filter_by_deadline()
                    elif self.inventory_order == 'priority':
                        current_jobs = self.character.inventory.filter_by_priority()
                    else:
                        current_jobs = self.character.inventory.jobs

                    if event.key == pygame.K_d:
                        self.inventory_order = 'deadline'
                        self.selected_job_index = 0
                    elif event.key == pygame.K_p:
                        self.inventory_order = 'priority'
                        self.selected_job_index = 0
                    elif event.key == pygame.K_UP:
                        if current_jobs:
                            self.selected_job_index = (self.selected_job_index - 1) % len(current_jobs)
                    elif event.key == pygame.K_DOWN:
                        if current_jobs:
                            self.selected_job_index = (self.selected_job_index + 1) % len(current_jobs)
                    elif event.key == pygame.K_c:
                        if current_jobs and 0 <= self.selected_job_index < len(current_jobs):
                            selected_job = current_jobs[self.selected_job_index]
                            if self.character.inventory.cancel_job(selected_job.id):
                                self.character.cancel_job_reputation()
                                self.character.update_stats()
                                if self.selected_job_index >= len(current_jobs) - 1:
                                    self.selected_job_index = max(0, len(current_jobs) - 2)
                elif self.show_job_decision and not self.show_inventory:
                    if event.key == pygame.K_a:
                        if self.pending_job and self.character.inventory.accept_job(self.pending_job):
                            # Crear una copia independiente del trabajo para el AI
                            ai_job_copy = self.pending_job.copy()
                            self.aiCharacter.inventory.accept_job(ai_job_copy)
                            self.job_manager.remove_job(self.pending_job.id)
                            self.show_job_decision = False
                            self.pending_job = None
                            self.job_decision_message = ""
                        else:
                            self.job_decision_message = "You cannot accept this job due to weight. Please reject it (N)."
                    elif event.key == pygame.K_n:
                        if self.pending_job is not None:
                            try:
                                self.job_manager.remove_job(self.pending_job.id)
                            except Exception:
                                pass
                        self.character.job_rejected_reputation()
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
                    # Player inventory processing
                    for job in self.character.inventory.jobs[:]:
                        if not job.is_picked_up():
                            if self.character.inventory.pickup_job(job, (self.character.tile_x, self.character.tile_y)):
                                self.character.update_stats()
                    for job in [j for j in self.character.inventory.jobs if j.is_picked_up()]:
                        self._process_dropoff_for(self.character, job)
                        self.character.update_stats()
                    # AI inventory processing (static AI)

                        
    def handle_ai_movement(self):
        #use AIController to manage AI movement
        ai_controller = AIController(dificulty="easy", inventory=self.aiCharacter.inventory, game=self)
        dx, dy = ai_controller.manage_move(self.aiCharacter)
        self.aiCharacter.movement(dx, dy, self.mapa, weather=self.weather)
        if self.aiCharacter.resistencia_exhausto:
            self.aiCharacter.restore_stamina()
            return
        print(self.aiCharacter.inventory.picked_jobs)


    def _process_dropoff_with_reputacion(self, job):
        # Mantener compatibilidad: usa el helper generalizado para el jugador
        self._process_dropoff_for(self.character, job)
        self._process_dropoff_for(self.aiCharacter, job)

    def _process_dropoff_for(self, who: Character, job):
        entregado = who.inventory.deliver_job(job, (who.tile_x, who.tile_y))
        if entregado:
            try:
                now = pygame.time.get_ticks()
                elapsed_seconds = int((now - self.tiempo_inicio) / 1000) if self.tiempo_inicio else 0
                tiempo_deadline = job.deadline.split('T')[1] if 'T' in str(job.deadline) else str(job.deadline)
                min_deadline = int(tiempo_deadline.split(':')[0])
                sec_deadline = int(tiempo_deadline.split(':')[1])
                deadline_seconds = min_deadline * 60 + sec_deadline
                if elapsed_seconds <= deadline_seconds - int(0.2 * deadline_seconds):
                    who.job_delivered_early_reputation()
                elif elapsed_seconds <= deadline_seconds:
                    who.job_delivered_in_time_reputation()
                else:
                    segundos_tarde = elapsed_seconds - deadline_seconds
                    who.job_delivered_late_reputacion(segundos_tarde)
            except Exception:
                # Corrección: método en Character es job_delivered_in_time_reputation
                who.job_delivered_in_time_reputation()
            payout = int(job.payout * who.pay_multiplier_reputation())
            who.score += payout
    def _update_movement_ai(self):
        # AI estático: sin movimiento
        pass

    def _init_time_if_needed(self):
        if self.tiempo_inicio is None:
            self.tiempo_inicio = pygame.time.get_ticks()

    def _get_elapsed_seconds(self):
        return int((pygame.time.get_ticks() - self.tiempo_inicio) / 1000)

    def _update_visible_jobs(self, elapsed_seconds):
        if self.first_frame:
            self.job_manager.update_visible_jobs(0)
            self.first_frame = False
        else:
            self.job_manager.update_visible_jobs(elapsed_seconds)

    def _update_weather(self):
        self.weather.update(1 / constants.FPS)

    def _process_pending_jobs(self):
        if not self.show_job_decision:
            accepted_ids = {j.id for j in self.character.inventory.jobs}
            for job in self.job_manager.visible_jobs:
                if job.id not in accepted_ids:
                    self.pending_job = job
                    self.show_job_decision = True
                    break

    def _recover_stamina_if_idle(self):
        self.character.restore_stamina()

    def _remove_expired_jobs(self, elapsed_seconds):
        for job in self.character.inventory.jobs[:]:
            if job.is_expired(elapsed_seconds):
                self.character.inventory.remove_job(job.id)
                self.character.job_expired_reputation()
                self.last_deadline_penalty = True
                break

    def update_game_state(self):
        self._init_time_if_needed()
        elapsed_seconds = self._get_elapsed_seconds()
        self._update_visible_jobs(elapsed_seconds)
        self._update_weather()
        self._process_pending_jobs()
        self._recover_stamina_if_idle()
        self._remove_expired_jobs(elapsed_seconds)
        self.character.update_stats()
        # AI estático: sin movimiento

    def draw(self):
        print(self.aiCharacter.inventory.picked_jobs)
        reputacion = self.character.reputation
        if self.character.score >= self.objetivo_valor:
            score_data = self.calculate_final_score()
            self.running = False
            self.hud.show_victory_with_final_score(score_data)
        elif self.character.reputation < 20 or self._get_elapsed_seconds() >= self.tiempo_limite:
            self.running = False
            self.hud.show_game_over(reason="Low reputation" if self.character.reputation < 20 else "Time is up")
        else:
            self.mapa.draw_map(self.screen)
            self.character.draw(self.screen)
            self.aiCharacter.draw(self.screen)
            tiempo_restante = max(0, self.tiempo_limite - self._get_elapsed_seconds())
            money_objective = self.objetivo_valor
            self.hud.draw(self.character, tiempo_restante=tiempo_restante, money_objective=money_objective, reputacion=reputacion, weather=self.weather, ai_character=self.aiCharacter)
            if self.show_inventory:
                self.hud.draw_inventory(self.character.inventory, order=self.inventory_order, tiempo_limite=self.tiempo_limite, selected_job_index=self.selected_job_index)
            if self.show_job_decision:
                self.hud.draw_job_decision(self.pending_job, job_decision_message=self.job_decision_message)

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
        pay_mult = self.character.pay_multiplier_reputation()
        score_base = int(self.character.score * pay_mult)
        elapsed_seconds = self._get_elapsed_seconds()
        tiempo_restante = self.tiempo_limite - elapsed_seconds
        twenty_percent_time = self.tiempo_limite * 0.2
        bonus_tiempo = 0
        if tiempo_restante >= twenty_percent_time:
            bonus_percentage = tiempo_restante / self.tiempo_limite
            bonus_tiempo = int(500 * bonus_percentage)
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
            pygame.display.flip()
            clock.tick(constants.FPS)
        pygame.mixer.music.stop()
        pygame.quit()

        sys.exit()
