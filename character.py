
import pygame  # Librería para gráficos y eventos
import constants  # Constantes globales del juego
from job import Job  # Clase para trabajos
from inventory import Inventory  # Clase para el inventario



# Clase principal del jugador/courier
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
        self.reputacion = 70  # Reputación inicial (punto 7)
        self.tile_size = tile_size  # Tamaño de cada tile
        self.resistencia = 100  # Resistencia inicial
        self.peso_total = 0  # Peso total de trabajos recogidos
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
        self.ultimo_movimiento = 0  # Timestamp del último movimiento
        self.resistencia_exhausto = False  # Bandera para bloqueo de movimiento por fatiga
        self.inventario = Inventory(constants.MAX_WEIGHT)  # Inventario del jugador
        self.delay_recuperacion = 1000  # ms para recuperar resistencia
        self.score = 0  # Puntuación inicial
        self.entregas_sin_penalizacion = 0  # Para rachas
        self.racha_bonus_aplicado = False
        self.primera_tardanza_aplicada = False
    # --- Lógica de reputación y penalizaciones ---
    def reputacion_multiplicador_pago(self):
        """Multiplicador de pago por reputación alta (≥90)"""
        return 1.05 if self.reputacion >= 90 else 1.0

    def reputacion_derrota(self):
        """Devuelve True si la reputación está en derrota (<20)"""
        return self.reputacion < 20

    def reputacion_entrega_a_tiempo(self):
        self.reputacion = min(100, self.reputacion + 3)
        self.entregas_sin_penalizacion += 1
        self._check_racha_bonus()

    def reputacion_entrega_temprana(self):
        self.reputacion = min(100, self.reputacion + 5)
        self.entregas_sin_penalizacion += 1
        self._check_racha_bonus()

    def reputacion_entrega_tarde(self, segundos_tarde):
        # Primera tardanza del día a mitad de penalización si reputación ≥85
        if not self.primera_tardanza_aplicada and self.reputacion >= 85:
            self.primera_tardanza_aplicada = True
            if segundos_tarde <= 30:
                self.reputacion = max(0, self.reputacion - 1)
            elif segundos_tarde <= 120:
                self.reputacion = max(0, self.reputacion - 2.5)
            else:
                self.reputacion = max(0, self.reputacion - 5)
        else:
            if segundos_tarde <= 30:
                self.reputacion = max(0, self.reputacion - 2)
            elif segundos_tarde <= 120:
                self.reputacion = max(0, self.reputacion - 5)
            else:
                self.reputacion = max(0, self.reputacion - 10)
        self.entregas_sin_penalizacion = 0
        self.racha_bonus_aplicado = False

    def reputacion_cancelar_pedido(self):
        self.reputacion = max(0, self.reputacion - 4)
        self.entregas_sin_penalizacion = 0
        self.racha_bonus_aplicado = False

    def reputacion_expirar_paquete(self):
        self.reputacion = max(0, self.reputacion - 6)
        self.entregas_sin_penalizacion = 0
        self.racha_bonus_aplicado = False

    def _check_racha_bonus(self):
        # Racha de 3 entregas sin penalización: +2 (una vez por racha)
        if self.entregas_sin_penalizacion >= 3 and not self.racha_bonus_aplicado:
            self.reputacion = min(100, self.reputacion + 2)
            self.racha_bonus_aplicado = True

    def reset_racha(self):
        self.entregas_sin_penalizacion = 0
        self.racha_bonus_aplicado = False
        self.primera_tardanza_aplicada = False

    def get_score(self):
        """Devuelve la puntuación actual del jugador."""
        return self.score
    
    def pickup_job(self, job, mapa=None):
        """
        Intenta recoger un trabajo si el personaje está en el tile de pickup.
        Devuelve True si lo recoge, False si no.
        """
        pos = (self.tile_x, self.tile_y)
        return self.inventario.pickup_job(job, pos, mapa)
    
    def process_dropoff(self, job):
        """
        Intenta entregar el trabajo en la posición actual.
        Si se entrega, suma la recompensa a la puntuación.
        """
        entregado = self.inventario.deliver_job(job, (self.tile_x, self.tile_y))
        if entregado:
            self.score += job.payout
        return entregado
    
    def update_stats(self):
        """
        Actualiza el peso total de trabajos recogidos.
        La puntuación se actualiza en process_dropoff.
        """
        self.peso_total = sum(job.weight for job in self.inventario.jobs if job.is_recogido())

    def add_score(self, payout):
        """Suma una cantidad a la puntuación."""
        self.score += payout

    def draw(self, screen):
        """Dibuja el personaje en la pantalla."""
        pygame.draw.rect(screen, constants.COLOR_CHARACTER, self.shape)

    def recuperar_resistencia(self, segundos=1):
        """
        Recupera resistencia si ha pasado suficiente tiempo desde el último movimiento.
        """
        time = pygame.time.get_ticks()
        if time - self.ultimo_movimiento >= self.delay_recuperacion:
            self.resistencia = min(100, self.resistencia + 5 * segundos)
        print(self.resistencia)

    def update_resistencia(self, mapa=None):
        """
        Actualiza la resistencia según el peso y el tipo de superficie.
        Si la resistencia llega a 0, activa exhausto.
        """
        base_consumo = 0.5  # Consumo base por movimiento
        peso_extra = max(0, self.peso_total - 3) * 0.2  # Penalización por peso
        surface_multiplier = 1.0  # Multiplicador por superficie

        if mapa:
            surface_multiplier = mapa.get_surface_weight(self.tile_x, self.tile_y)
        # Imprime los pesos de los trabajos recogidos y el peso total
        recogidos = [job.weight for job in self.inventario.jobs if job.is_recogido()]
        print(f"Pesos recogidos: {recogidos}, Peso total: {self.peso_total}")
        self.resistencia -= (base_consumo + peso_extra) * surface_multiplier
        self.resistencia = max(0, self.resistencia)
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
        # Bloquea movimiento si está exhausto
        if self.resistencia_exhausto:
            return

        nueva_x = self.tile_x + dx
        nueva_y = self.tile_y + dy

        # Limitar movimiento por el tamaño real del mapa
        min_y = 0
        max_y = mapa.height - 1
        if nueva_y < min_y or nueva_y > max_y:
            return

        if not mapa.is_blocked(nueva_x, nueva_y):
            # Multiplicadores de velocidad
            v0 = 3  # tiles por segundo
            Mresistencia = 1.0 if self.resistencia > 30 else 0.8  # Penalización por baja resistencia
            Mpeso = max(0.8, 1 - 0.03 *  self.peso_total)  # Penalización por peso
            Mrep = 1.03 if self.reputacion >= 90 else 1.0  # Bonus por reputación alta
            Msurface = mapa.get_surface_weight(nueva_x, nueva_y)  # Multiplicador por superficie

            Mclima = 1.0  # Multiplicador por clima (placeholder)
            if weather:
                Mclima = weather.current_multiplier  # penalización o bonus por clima

            velocidad = v0 * Mresistencia * Mpeso * Mrep * Msurface * Mclima

            start_pos = self.shape.center
            end_pos = (nueva_x * self.tile_size + self.tile_size // 2,
                       nueva_y * self.tile_size + self.tile_size // 2 + self.top_bar_height)

            # Actualiza la posición final
            self.tile_x = nueva_x
            self.tile_y = nueva_y
            self.shape.center = end_pos

            # Actualiza resistencia y timestamp de movimiento
            self.update_resistencia(mapa)
            self.ultimo_movimiento = pygame.time.get_ticks()
            print(self.resistencia)

