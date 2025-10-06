import pygame  # Librería para gráficos y eventos
import constants  # Constantes globales del juego
from job import Job  # Clase para trabajos
from inventory import Inventory  # Clase para el inventario
import os



class Character:
    def __init__(self, tile_x, tile_y, tile_size, screen, top_bar_height=None):
        """
        Inicializa el personaje en la posición (tile_x, tile_y) con el tamaño de tile dado.
        screen: superficie de pygame donde se dibuja
        top_bar_height: altura de la barra superior (HUD)
        """
        self.screen = screen  # Superficie de dibujo
        self.tile_x = tile_x  # Posición X en tiles
        self.tile_y = tile_y  # Posición Y en tiles
        self.reputation = 70  # Reputación inicial (punto 7)
        self.tile_size = tile_size  # Tamaño de cada tile
        self.resistencia = 100  # Resistencia inicial
        self.total_weight = 0  # Peso total de trabajos recogidos
        self.top_bar_height = top_bar_height if top_bar_height is not None else 0  # Altura HUD
        # Rectángulo que representa al personaje
        self.shape = pygame.Rect(
            tile_x * tile_size,
            tile_y * tile_size + self.top_bar_height,
            constants.WIDTH_CHARACTER,
            constants.HEIGHT_CHARACTER
        )
        # Centrar el rectángulo en el tile
        self.shape.center = (tile_x * tile_size + tile_size // 2,
                             tile_y * tile_size + tile_size // 2 + self.top_bar_height)
        self.last_movement = 0  # Timestamp del último movimiento
        self.resistencia_exhausto = False  # Bandera para bloqueo de movimiento por fatiga
        self.inventory = Inventory(constants.MAX_WEIGHT)  # Inventario del jugador
        self.delay_recuperacion = 1000  # ms para recuperar resistencia
        self.score = 0  # Puntuación inicial
        self.deliveres_without_penalization = 0  # Para rachas
        self.streak_bonus_applied = False # Si ya se aplicó el bonus de racha
        self.first_job_late_aplied = False # Si ya se aplicó la primera tardanza del día

        # Dirección actual para dibujar el sprite del personaje
        self.facing = "down"  # down | up | left | right
        self.character_sprites = self.load_character_sprites()


    # --- Lógica de reputación y penalizaciones ---
    def pay_multiplier_reputation(self):
        """Multiplicador de pago por reputación alta (≥90)"""
        return 1.05 if self.reputation >= 90 else 1.0

    def loss_reputation(self):
        """Devuelve True si la reputación está en derrota (<20)"""
        return self.reputation < 20

    def job_delivered_in_time_reputation(self):
        """Entrega a tiempo: +3 reputación"""
        self.reputation = min(100, self.reputation + 3)
        self.deliveres_without_penalization += 1
        self._check_bonus_streak()

    def job_delivered_early_reputation(self):
        """Entrega temprana: +5 reputación"""
        self.reputation = min(100, self.reputation + 5)
        self.deliveres_without_penalization += 1
        self._check_bonus_streak()

    # Alias para compatibilidad con llamadas que usan 'reputacion'

    def job_delivered_late_reputacion(self, seconds_late):
        """Entrega tarde: penalización según tiempo tarde"""
        if not self.first_job_late_aplied and self.reputation >= 85:
            self.first_job_late_aplied = True
            if seconds_late <= 30:
                self.reputation = max(0, self.reputation - 1)
            elif seconds_late <= 120:
                self.reputation = max(0, self.reputation - 2.5)
            else:
                self.reputation = max(0, self.reputation - 5)
        else:
            if seconds_late <= 30:
                self.reputation = max(0, self.reputation - 2)
            elif seconds_late <= 120:
                self.reputation = max(0, self.reputation - 5)
            else:
                self.reputation = max(0, self.reputation - 10)
        self.deliveres_without_penalization = 0
        self.streak_bonus_applied = False

    def cancel_job_reputation(self):
        """Cancelar trabajo: -4 reputación"""
        self.reputation = max(0, self.reputation - 4)
        self.deliveres_without_penalization = 0
        self.streak_bonus_applied = False

    def job_expired_reputation(self):
        """Job expirado: -6 reputación"""
        self.reputation = max(0, self.reputation - 6)
        self.deliveres_without_penalization = 0
        self.streak_bonus_applied = False

    def job_rejected_reputation(self):
        """Rechazar pedido pendiente: -1 reputación (penalización leve)."""
        self.reputation = max(0, self.reputation - 3)
        self.deliveres_without_penalization = 0
        self.streak_bonus_applied = False

    def _check_bonus_streak(self):
        """Verifica y aplica bonus por racha de entregas sin penalización."""
        # Racha de 3 entregas sin penalización: +2 (una vez por racha)
        if self.deliveres_without_penalization >= 3 and not self.streak_bonus_applied:
            self.reputation = min(100, self.reputation + 2)
            self.streak_bonus_applied = True

    def reset_streak(self):
        """Resetea la racha de entregas sin penalización (usado al cambiar de día)."""
        self.deliveres_without_penalizacion = 0
        self.streak_bonus_applied = False
        self.first_job_late_aplied = False

    def pickup_job(self, job, mapa=None):
        """
        Intenta recoger un trabajo si el personaje está en el tile de pickup.
        Devuelve True si lo recoge, False si no.
        """
        pos = (self.tile_x, self.tile_y)
        return self.inventory.pickup_job(job, pos, mapa)

    def process_dropoff(self, job):
        """
        Intenta entregar el trabajo en la posición actual.
        Si se entrega, suma la recompensa a la puntuación.
        """
        delivered = self.inventory.deliver_job(job, (self.tile_x, self.tile_y))
        if delivered:
            self.score += job.payout
        return delivered

    def update_stats(self):
        """
        Actualiza el peso total de trabajos recogidos usando el inventario.
        La puntuación se actualiza en process_dropoff.
        """
        self.total_weight = self.inventory.total_weight()


    def add_score(self, payout):
        """Suma una cantidad a la puntuación."""
        self.score += payout

    def draw(self, screen):
        """Dibuja el personaje en la pantalla con sprite direccional si está disponible."""
        sprite = None
        if hasattr(self, 'character_sprites') and self.character_sprites:
            sprite = self.character_sprites.get(self.facing)
        if sprite:
            screen.blit(sprite, self.shape.topleft)
        else:
            pygame.draw.rect(screen, constants.COLOR_CHARACTER, self.shape)

    def restore_stamina(self, segundos=1):
        """
        Recupera resistencia automáticamente cuando el personaje está inactivo.
        """
        time = pygame.time.get_ticks()
        # Solo recuperar si ha pasado tiempo suficiente desde el último movimiento Y no está exhausto
        if time - self.last_movement >= self.delay_recuperacion:
            # Recuperar resistencia gradualmente
            recovery_rate = 5  # puntos por segundo de recuperación
            self.resistencia = min(100, self.resistencia + recovery_rate * segundos)
            # Debug: mostrar recuperación solo cuando realmente sucede
            if self.resistencia >= 30:
                self.resistencia_exhausto = False
            if recovery_rate * segundos > 0:
                print(f"Recuperando resistencia: {self.resistencia}")

    def update_stamina(self, mapa=None, stamina=1.0):
        """
        Actualiza la resistencia según el peso y el tipo de superficie.
        Si la resistencia llega a 0, activa exhausto.
        """
        if 10 < self.resistencia < 30:
            self.resistencia -= max(0, stamina * 0.8)
        else:
            self.resistencia -= max(0, stamina)
        if self.resistencia < 0:
            self.resistencia = 0
        # Si la resistencia llega a 0 o menos, activa exhausto
        if self.resistencia <= 0:
            self.resistencia_exhausto = True
        # Si la bandera está activa y la resistencia sube a 30 o más, desactiva exhausto
        if self.resistencia_exhausto and self.resistencia >= 30:
            self.resistencia_exhausto = False

    def movement(self, dx, dy, mapa, weather=None):
        """
        Mueve el personaje en la dirección (dx, dy) si no está exhausto y el tile destino no está bloqueado.
        Aplica multiplicadores de velocidad según peso, reputación, superficie y clima.
        """
        # Solo bloquea movimiento si self.resistencia_exhausto está activo y la resistencia es menor a 30
        if self.resistencia_exhausto and self.resistencia < 30:
            return

        nueva_x = self.tile_x + dx
        nueva_y = self.tile_y + dy

        min_y = 0
        max_y = mapa.height - 1
        if nueva_y < min_y or nueva_y > max_y:
            return

        if not mapa.is_blocked(nueva_x, nueva_y):
            # Multiplicadores de velocidad
            v0 = 3  # tiles por segundo
            M_stamina = 1.0 if self.resistencia > 30 else 0.8  # Penalización por baja resistencia
            M_weight = max(0.8, 1 - 0.03 * self.total_weight)  # Penalización por peso
            M_reputation = 1.03 if self.reputation >= 90 else 1.0  # Bonus por reputación alta
            M_surface = mapa.get_surface_weight(nueva_x, nueva_y)  # Multiplicador por superficie

            M_weather = 1.0  # Multiplicador por clima (placeholder)
            if weather:
                M_weather = weather.current_multiplier  # penalización o bonus por clima

            velocidad = v0 * M_stamina * M_weight * M_reputation * M_surface * M_weather

            end_pos = (nueva_x * self.tile_size + self.tile_size // 2,
                       nueva_y * self.tile_size + self.tile_size // 2 + self.top_bar_height)

            # Actualiza la posición final
            self.tile_x = nueva_x
            self.tile_y = nueva_y
            self.shape.center = end_pos

            # Actualiza dirección (solo cuando el movimiento fue válido)
            if dy < 0:
                self.facing = "up"
            elif dy > 0:
                self.facing = "down"
            elif dx < 0:
                self.facing = "left"
            elif dx > 0:
                self.facing = "right"

            # Actualiza resistencia y timestamp de movimiento
            self.update_stamina(mapa, velocidad)
            self.last_movement = pygame.time.get_ticks()
            print(self.resistencia)

    def get_score(self):
        """Devuelve la puntuación actual del jugador."""
        return self.score

    def get_tile_x(self):
        """Devuelve la posición X en tiles."""
        return self.tile_x

    def get_tile_y(self):
        """Devuelve la posición Y en tiles."""
        return self.tile_y

    def get_reputacion(self):
        """Devuelve la reputación actual."""
        return self.reputation

    def get_resistencia(self):
        """Devuelve la resistencia actual."""
        return self.resistencia

    def get_peso_total(self):
        """Devuelve el peso total actual."""
        return self.total_weight

    def get_entregas_sin_penalizacion(self):
        """Devuelve el número de entregas sin penalización."""
        return self.deliveres_without_penalization

    def get_racha_bonus_aplicado(self):
        """Devuelve si el bonus de racha está aplicado."""
        return self.streak_bonus_applied

    def get_primera_tardanza_aplicada(self):
        """Devuelve si la primera tardanza ya fue aplicada."""
        return self.first_job_late_aplied

    def get_inventario(self):
        """Devuelve el objeto inventario."""
        return self.inventory


    def to_dict(self):
        """
        Devuelve un diccionario con el estado serializable del personaje para guardado/carga.
        """
        return {
            "tile_x": self.tile_x,
            "tile_y": self.tile_y,
            "reputacion": self.reputation,
            "tile_size": self.tile_size,
            "resistencia": self.resistencia,
            "peso_total": self.total_weight,
            "top_bar_height": self.top_bar_height,
            "score": self.score,
            "entregas_sin_penalizacion": self.deliveres_without_penalization,
            "racha_bonus_aplicado": self.streak_bonus_applied,
            "primera_tardanza_aplicada": self.first_job_late_aplied
        }

    # --- Carga de sprites del personaje ---
    def load_character_sprites(self):
        """Carga sprites direccionales del personaje desde sprites/character/."""
        base = os.path.join("sprites", "character")
        mapping = {
            "up": "up_character.png",
            "down": "down_character.png",
            "left": "left_character.png",
            "right": "right_character.png",
        }
        sprites = {}
        for key, filename in mapping.items():
            path = os.path.join(base, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (constants.WIDTH_CHARACTER, constants.HEIGHT_CHARACTER))
                    sprites[key] = img
                except Exception as e:
                    print(f"Error loading character sprite {filename}: {e}")
            else:
                print(f"Character sprite not found: {path}")
        return sprites
