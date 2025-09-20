
import pygame
import constants
from job import Job
from inventory import Inventory


class Character:

    def __init__(self, tile_x, tile_y, tile_size, screen, top_bar_height=None):
        self.screen = screen
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.reputacion = 100
        self.tile_size = tile_size
        self.resistencia = 100
        self.peso_total = 0
        self.top_bar_height = top_bar_height if top_bar_height is not None else 0
        self.shape = pygame.Rect(
            tile_x * tile_size,
            tile_y * tile_size + self.top_bar_height,
            constants.WIDTH_CHARACTER,
            constants.HEIGHT_CHARACTER
        )
        self.shape.center = (tile_x * tile_size + tile_size // 2,
                             tile_y * tile_size + tile_size // 2 + self.top_bar_height)
        self.ultimo_movimiento = 0
        self.resistencia_exhausto = False  # Bandera para bloqueo de movimiento
        self.inventario = Inventory(constants.MAX_WEIGHT)
        self.delay_recuperacion = 1000  # milisegundos para recuperar resistencia
        self.score = 0  # Puntuación del jugador

    def process_dropoff(self, job):
        # Intenta entregar el trabajo y suma la recompensa si lo logra
        entregado = self.inventario.deliver_job(job, (self.tile_x, self.tile_y))
        if entregado:
            self.score += job.payout
        return entregado
    
    def update_stats(self):
        # Actualiza la puntuación y el peso total
        self.score = getattr(self, 'score', 0)  # No sumar por recogido, solo por entregado
        self.peso_total = sum(job.weight for job in self.inventario.jobs if getattr(job, 'recogido', False))

    def add_score(self, payout):
        self.score += payout

    def draw(self, screen):
        pygame.draw.rect(screen, constants.COLOR_CHARACTER, self.shape)

    def recuperar_resistencia(self, segundos=1):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_movimiento >= self.delay_recuperacion:
            self.resistencia = min(100, self.resistencia + 5 * segundos)
        print(self.resistencia)

    def update_resistencia(self, mapa=None):
        """
        Consumo por movimiento según proyecto.
        Si se pasa mapa, se toma en cuenta surface_weight del tile actual.
        """
        base_consumo = 0.5
        peso_extra = max(0, self.peso_total - 3) * 0.2
        surface_multiplier = 1.0

        if mapa:
            surface_multiplier = mapa.get_surface_weight(self.tile_x, self.tile_y)
        # Validación: imprime los pesos de los trabajos recogidos y el peso total
        recogidos = [job.weight for job in self.inventario.jobs if getattr(job, 'recogido', False)]
        print(f"Pesos recogidos: {recogidos}, Peso total: {self.peso_total}")
        self.resistencia -= (base_consumo + peso_extra) * surface_multiplier
        self.resistencia = max(0, self.resistencia)
        # Si la resistencia llega a 0 o menos, activa exhausto
        if self.resistencia <= 0:
            self.resistencia_exhausto = True
        # Si la bandera está activa y la resistencia sube a 30 o más, desactiva exhausto
        if self.resistencia_exhausto and self.resistencia >= 30:
            self.resistencia_exhausto = False


    def movement(self, dx, dy, mapa):
        """Mueve un tile según multiplicadores del proyecto, evitando navbar y HUD. Si resistencia llega a 0, queda exhausto hasta recuperarse a 30."""
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
            # Multiplicadores
            v0 = 3  # tiles por segundo
            Mresistencia = 1.0 if self.resistencia > 30 else 0.8
            Mpeso = max(0.8, 1 - 0.03 * max(0, self.peso_total - 3))
            Mrep = 1.03 if self.reputacion >= 90 else 1.0
            Msurface = mapa.get_surface_weight(nueva_x, nueva_y)
            Mclima = 1.0  # temporal, se actualizará con clima real

            velocidad = v0 * Mresistencia * Mpeso * Mrep * Msurface * Mclima

            # Interpolación suave
            start_pos = self.shape.center
            end_pos = (nueva_x * self.tile_size + self.tile_size // 2,
                       nueva_y * self.tile_size + self.tile_size // 2 + self.top_bar_height)

            pasos = max(1, int(5 / velocidad))
            for i in range(1, pasos + 1):
                interp_x = start_pos[0] + (end_pos[0] - start_pos[0]) * i / pasos
                interp_y = start_pos[1] + (end_pos[1] - start_pos[1]) * i / pasos
                self.shape.center = (interp_x, interp_y)

            self.tile_x = nueva_x
            self.tile_y = nueva_y
            self.shape.center = end_pos

            self.update_resistencia(mapa)
            self.ultimo_movimiento = pygame.time.get_ticks()
            print(self.resistencia)

