
import pygame
import json
import sys
import constants

class Map:
    def __init__(self, archivo_json, tile_size, hud_height = 60, top_bar_height = 40):
        self.tile_size = tile_size
        self.tiles = []
        self.legend = {}
        self.width = 0
        self.height = 0
        self.top_bar_height = top_bar_height
        self.hud_height = hud_height

        # Colores por defecto
        self.colors = {
            "C": (200, 200, 200),  # Calles
            "B": (100, 50, 50),    # Edificios
            "P": (50, 200, 50)     # Parques
        }

        # Cargar datos
        self.cargar_desde_json(archivo_json)

    def cargar_desde_json(self, archivo_json):
        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                data = json.load(f)["data"]
        except Exception as e:
            print("Error al leer el archivo JSON:", e)
            sys.exit()

        self.tiles = data["tiles"]
        self.legend = data["legend"]
        self.width = data["width"]
        self.height = data["height"]

    # Dibuja el mapa completo recorriendo los tiles dados por el json y se colorea dependiendo de su tipo
    def draw_map(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                color = self.colors.get(tile, (0, 0, 0))  # negro si no está definido
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size + self.top_bar_height,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(screen, color, rect)

    def get_hud_bottom_y(self):
        # Devuelve la posición Y donde debe ir el HUD inferior
        return self.height * self.tile_size + self.top_bar_height

    def is_blocked(self, tile_x, tile_y):
        # fuera del mapa
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True
        tile = self.tiles[tile_y][tile_x]
        info = self.legend.get(tile, {})
        return info.get("blocked", False)
    
    def get_surface_weight(self, tile_x, tile_y):
        tile = self.tiles[tile_y][tile_x]
        info = self.legend.get(tile, {})
        return info.get("surface_weight", 1.0)
